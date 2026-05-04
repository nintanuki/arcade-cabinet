"""Rendering logic for the arcade launcher UI."""

from pathlib import Path

import pygame

from launcher.crt import LauncherCRT
from launcher.models import MenuFrame, MenuNode
from settings import (
    ColorSettings,
    FontSettings,
    InputSchemeSettings,
    LauncherSettings,
    MenuSettings,
    ScreenSettings,
)


class LauncherRenderer:
    """
    Handles all drawing for the launcher UI.

    Owns fonts, the JIL logo, the CRT overlay reference, and the per-frame
    hitbox list. The manager calls draw() each tick, passing the current
    menu state; all visual output is contained here so ArcadeLauncher stays
    focused on coordination and state.
    """

    def __init__(self, screen: pygame.Surface, root_dir: Path, crt: LauncherCRT) -> None:
        """
        Initialize fonts, the JIL logo, and rendering resources.

        Must be called after pygame.display is initialized so convert_alpha()
        has a valid display context.

        Args:
            screen (pygame.Surface): The display surface to draw onto.
            root_dir (Path): Launcher root directory, used to resolve asset paths.
            crt (LauncherCRT): Pre-built CRT overlay instance.
        """
        self.screen = screen
        self.crt = crt
        self.preview_images: dict[str, pygame.Surface] = {}
        self.menu_option_hitboxes: list[pygame.Rect] = []

        font_path = root_dir / FontSettings.FILE
        self.title_font = pygame.font.Font(str(font_path), FontSettings.TITLE_SIZE)
        self.subtitle_font = pygame.font.Font(str(font_path), FontSettings.SUBTITLE_SIZE)
        self.option_font = pygame.font.Font(str(font_path), FontSettings.OPTION_SIZE)
        self.hint_font = pygame.font.Font(str(font_path), FontSettings.HINT_SIZE)
        self.description_font = pygame.font.Font(str(font_path), FontSettings.DESCRIPTION_SIZE)

        # Logo loads after display init so convert_alpha() has a real context.
        # A missing or corrupt file is non-fatal; draw falls back to a placeholder rect.
        jil_logo_path = root_dir / LauncherSettings.JIL_LOGO_PATH
        try:
            logo_img = pygame.image.load(str(jil_logo_path)).convert_alpha()
            self.jil_logo_surface = pygame.transform.smoothscale(logo_img, LauncherSettings.JIL_LOGO_SIZE)
        except (FileNotFoundError, pygame.error):
            self.jil_logo_surface = None

    # ------------------------------------------------------------------
    # Loading screen
    # ------------------------------------------------------------------

    def draw_loading_frame(self, text: str) -> None:
        """
        Render a single loading screen frame and flip the display.

        Args:
            text (str): The loading text to display (e.g. "LOADING...").
        """
        self.screen.fill(ColorSettings.BLACK)
        surface = self.option_font.render(text, False, ColorSettings.WHITE)
        rect = surface.get_rect(center=(ScreenSettings.WIDTH // 2, ScreenSettings.HEIGHT // 2))
        self.screen.blit(surface, rect)
        pygame.display.flip()

    # ------------------------------------------------------------------
    # Header and footer
    # ------------------------------------------------------------------

    def _draw_header(self) -> None:
        """Render the JIL logo and title/subtitle as a centered unit."""
        # Center the JIL logo + title group horizontally as one unit so the
        # fixed gap between them stays the same regardless of title length.
        logo_w = LauncherSettings.JIL_LOGO_SIZE[0]
        title_surface = self.title_font.render(MenuSettings.TITLE_TEXT, False, ColorSettings.GREEN)
        title_w = title_surface.get_width()
        total_width = logo_w + LauncherSettings.JIL_LOGO_TITLE_SPACING + title_w
        start_x = (ScreenSettings.WIDTH - total_width) // 2
        logo_y = MenuSettings.TITLE_CENTER_Y - (LauncherSettings.JIL_LOGO_SIZE[1] // 2)

        if self.jil_logo_surface is not None:
            self.screen.blit(self.jil_logo_surface, (start_x, logo_y))
        else:
            pygame.draw.rect(
                self.screen,
                LauncherSettings.JIL_LOGO_PLACEHOLDER_COLOR,
                (start_x, logo_y, *LauncherSettings.JIL_LOGO_SIZE),
                2,
            )

        title_rect = title_surface.get_rect(
            midleft=(start_x + logo_w + LauncherSettings.JIL_LOGO_TITLE_SPACING, MenuSettings.TITLE_CENTER_Y)
        )
        self.screen.blit(title_surface, title_rect)

        subtitle_surface = self.subtitle_font.render(
            MenuSettings.SUBTITLE_TEXT, False, ColorSettings.LIGHT_BLUE
        )
        subtitle_rect = subtitle_surface.get_rect(
            center=(ScreenSettings.WIDTH // 2, MenuSettings.SUBTITLE_CENTER_Y)
        )
        self.screen.blit(subtitle_surface, subtitle_rect)

    def _draw_footer(self, status_message: str, status_message_until: int) -> None:
        """
        Render the two footer hint lines, replacing line 2 with a status message if active.

        Args:
            status_message (str): Temporary error/status text to show in place of line 2.
            status_message_until (int): Timestamp (ms) at which the status message expires.
        """
        hint_line_1 = self.hint_font.render(
            MenuSettings.FOOTER_TEXT_LINE_1, False, ColorSettings.LIGHT_BLUE
        )
        self.screen.blit(
            hint_line_1,
            hint_line_1.get_rect(center=(ScreenSettings.WIDTH // 2, MenuSettings.FOOTER_LINE_1_CENTER_Y)),
        )

        footer_line_2_text = MenuSettings.FOOTER_TEXT_LINE_2
        if status_message and pygame.time.get_ticks() < status_message_until:
            footer_line_2_text = status_message

        hint_line_2 = self.hint_font.render(footer_line_2_text, False, ColorSettings.LIGHT_BLUE)
        self.screen.blit(
            hint_line_2,
            hint_line_2.get_rect(center=(ScreenSettings.WIDTH // 2, MenuSettings.FOOTER_LINE_2_CENTER_Y)),
        )

    # ------------------------------------------------------------------
    # Menu rendering
    # ------------------------------------------------------------------

    def draw_menu(self, frame: MenuFrame) -> None:
        """
        Pick the carousel or static-list renderer based on the active frame.

        Args:
            frame (MenuFrame): The currently active menu frame.
        """
        if len(frame.items) > MenuSettings.CAROUSEL_THRESHOLD:
            self.draw_carousel_menu(frame)
        else:
            self.draw_list_menu(frame)

    def draw_carousel_menu(self, frame: MenuFrame) -> None:
        """
        Draw a vertical carousel centered on the selected item in this frame.

        Args:
            frame (MenuFrame): The currently active menu frame.
        """
        count = len(frame.items)
        # Reset hitboxes to the active frame's item count so only currently
        # visible carousel items react to the mouse.
        self.menu_option_hitboxes = [pygame.Rect(0, 0, 0, 0) for _ in range(count)]
        if count == 0:
            return

        for offset in range(-MenuSettings.CAROUSEL_VISIBLE_RADIUS, MenuSettings.CAROUSEL_VISIBLE_RADIUS + 1):
            option_index = (frame.selected_index + offset) % count
            node = frame.items[option_index]
            distance = abs(offset)
            is_selected = offset == 0

            color = ColorSettings.YELLOW if is_selected else ColorSettings.WHITE
            text_surface = self.option_font.render(node.label.upper(), False, color).convert_alpha()

            scale = max(
                MenuSettings.CAROUSEL_MIN_SCALE,
                MenuSettings.CAROUSEL_SELECTED_SCALE - (distance * MenuSettings.CAROUSEL_SCALE_STEP),
            )
            if scale != 1.0:
                text_surface = pygame.transform.smoothscale(
                    text_surface,
                    (
                        max(1, int(text_surface.get_width() * scale)),
                        max(1, int(text_surface.get_height() * scale)),
                    ),
                )

            alpha = max(
                MenuSettings.CAROUSEL_MIN_ALPHA,
                MenuSettings.CAROUSEL_SELECTED_ALPHA - (distance * MenuSettings.CAROUSEL_ALPHA_STEP),
            )
            text_surface.set_alpha(alpha)

            item_center = (
                MenuSettings.CAROUSEL_CENTER_X,
                MenuSettings.CAROUSEL_CENTER_Y + (offset * MenuSettings.CAROUSEL_ITEM_SPACING),
            )
            text_rect = text_surface.get_rect(center=item_center)
            self.screen.blit(text_surface, text_rect)
            self.menu_option_hitboxes[option_index] = text_rect.inflate(36, 16)

    def draw_list_menu(self, frame: MenuFrame) -> None:
        """
        Draw a static vertical list with a ``>`` cursor on the selected item.

        Args:
            frame (MenuFrame): The currently active menu frame.
        """
        count = len(frame.items)
        self.menu_option_hitboxes = [pygame.Rect(0, 0, 0, 0) for _ in range(count)]
        if count == 0:
            return

        total_height = (count - 1) * MenuSettings.LIST_ITEM_SPACING
        start_y = MenuSettings.CAROUSEL_CENTER_Y - total_height // 2

        for index, node in enumerate(frame.items):
            is_selected = index == frame.selected_index
            color = ColorSettings.YELLOW if is_selected else ColorSettings.WHITE
            label_surface = self.option_font.render(node.label.upper(), False, color)
            label_rect = label_surface.get_rect(
                center=(MenuSettings.CAROUSEL_CENTER_X, start_y + index * MenuSettings.LIST_ITEM_SPACING)
            )
            self.screen.blit(label_surface, label_rect)

            if is_selected:
                cursor_text = MenuSettings.LIST_CURSOR_TEXT.strip() or ">"
                cursor_surface = self.option_font.render(cursor_text, False, color)
                cursor_rect = cursor_surface.get_rect(midright=(label_rect.left - 8, label_rect.centery))
                self.screen.blit(cursor_surface, cursor_rect)

            # Inflate hitbox enough to cover the cursor area on the left.
            self.menu_option_hitboxes[index] = label_rect.inflate(80, 16)

    # ------------------------------------------------------------------
    # Preview panel
    # ------------------------------------------------------------------

    def draw_preview_panel(self, node: MenuNode | None) -> None:
        """
        Draw the preview box; contents depend on game-vs-submenu highlight.

        Args:
            node (MenuNode | None): The currently highlighted node, or None.
        """
        preview_rect = pygame.Rect(
            MenuSettings.PREVIEW_BOX_X,
            MenuSettings.PREVIEW_BOX_Y,
            MenuSettings.PREVIEW_BOX_WIDTH,
            MenuSettings.PREVIEW_BOX_HEIGHT,
        )
        inner_rect = preview_rect.inflate(
            -(MenuSettings.PREVIEW_INNER_PADDING * 2),
            -(MenuSettings.PREVIEW_INNER_PADDING * 2),
        )

        pygame.draw.rect(
            self.screen,
            ColorSettings.WHITE,
            preview_rect,
            MenuSettings.PREVIEW_BORDER_WIDTH,
            MenuSettings.PREVIEW_BORDER_RADIUS,
        )

        if node is None:
            return

        if node.kind == "game":
            self._draw_game_preview(node, inner_rect, preview_rect)
        else:
            self._draw_description(node, inner_rect)

    def _draw_game_preview(
        self, node: MenuNode, inner_rect: pygame.Rect, preview_rect: pygame.Rect
    ) -> None:
        """
        Render the screenshot (or fallback) plus the under-construction stamp.

        Args:
            node (MenuNode): The game node being previewed.
            inner_rect (pygame.Rect): The padded inner area of the preview box.
            preview_rect (pygame.Rect): The full preview box rect (used to center the stamp).
        """
        preview_surface = self.preview_images.get(node.preview_label) if node.preview_label else None
        if preview_surface is not None:
            self.screen.blit(preview_surface, preview_surface.get_rect(center=inner_rect.center))
        else:
            fallback = self.subtitle_font.render("PREVIEW NOT AVAILABLE", False, ColorSettings.WHITE)
            self.screen.blit(fallback, fallback.get_rect(center=inner_rect.center))

        if node.under_construction:
            # White outline so the red label stays legible over busy preview
            # screenshots -- straight red text disappears against warm-toned
            # panels (e.g. the dungeon previews).
            self.draw_outlined_text(
                MenuSettings.UNDER_CONSTRUCTION_TEXT,
                self.option_font,
                ColorSettings.RED,
                ColorSettings.WHITE,
                preview_rect.center,
            )

    def _draw_description(self, node: MenuNode, inner_rect: pygame.Rect) -> None:
        """
        Render a wrapped category description centered inside the preview panel.

        Specific phrases listed in MenuSettings.DESCRIPTION_HIGHLIGHTS render
        in their assigned colors; everything else falls back to white. Each
        line is centered horizontally based on its total rendered width so a
        colored phrase doesn't pull the line off-axis.

        Args:
            node (MenuNode): The submenu node whose description to render.
            inner_rect (pygame.Rect): The padded inner area of the preview box.
        """
        description = (node.description or "").upper()
        if not description.strip():
            return
        color_map = self._build_description_color_map(description)
        lines = self._wrap_description_with_colors(
            description, color_map, self.description_font, inner_rect.width
        )
        if not lines:
            return
        line_height = self.description_font.get_linesize()
        spacing = MenuSettings.DESCRIPTION_LINE_SPACING
        block_height = len(lines) * line_height + (len(lines) - 1) * spacing
        start_y = inner_rect.centery - block_height // 2
        for index, runs in enumerate(lines):
            if not runs:
                continue
            run_surfaces = [
                self.description_font.render(segment, False, color) for segment, color in runs
            ]
            total_width = sum(s.get_width() for s in run_surfaces)
            x = inner_rect.centerx - total_width // 2
            y = start_y + index * (line_height + spacing)
            for surface in run_surfaces:
                self.screen.blit(surface, (x, y))
                x += surface.get_width()

    # ------------------------------------------------------------------
    # Description text helpers
    # ------------------------------------------------------------------

    def _build_description_color_map(self, text: str) -> list[tuple[int, int, int]]:
        """
        Return a per-character color list for ``text`` (already uppercased).

        Default color is white. Each entry in MenuSettings.DESCRIPTION_HIGHLIGHTS
        paints its phrase characters with the assigned color when found at a
        word boundary. Longer phrases win over shorter ones if they overlap,
        because they are applied first.

        Args:
            text (str): The uppercased description string to colorize.

        Returns:
            list[tuple[int, int, int]]: One RGB color per character in ``text``.
        """
        color_map: list[tuple[int, int, int]] = [ColorSettings.WHITE] * len(text)
        highlights = sorted(
            MenuSettings.DESCRIPTION_HIGHLIGHTS.items(),
            key=lambda item: -len(item[0]),
        )
        for phrase, color in highlights:
            needle = phrase.upper()
            if not needle:
                continue
            search_from = 0
            while True:
                idx = text.find(needle, search_from)
                if idx < 0:
                    break
                before_ok = idx == 0 or not text[idx - 1].isalnum()
                end = idx + len(needle)
                after_ok = end == len(text) or not text[end].isalnum()
                if before_ok and after_ok:
                    for i in range(idx, end):
                        color_map[i] = color
                search_from = idx + 1
        return color_map

    def _wrap_description_with_colors(
        self,
        text: str,
        color_map: list[tuple[int, int, int]],
        font: pygame.font.Font,
        max_width: int,
    ) -> list[list[tuple[str, tuple[int, int, int]]]]:
        """
        Greedy word-wrap ``text`` into per-line color runs.

        Each line in the returned list is a sequence of (segment, color)
        pairs to render side-by-side. Single inter-word spaces are added
        back at render time and inherit the color of the following word.

        Args:
            text (str): The full description string to wrap.
            color_map (list): Per-character color list from _build_description_color_map.
            font (pygame.font.Font): Font used to measure text width.
            max_width (int): Maximum pixel width for each line.

        Returns:
            list: Lines, each a list of (segment_text, color) pairs.
        """
        # Tokenize into (word_text, start_index_in_text) pairs.
        words: list[tuple[str, int]] = []
        i = 0
        n = len(text)
        while i < n:
            if text[i].isspace():
                i += 1
                continue
            start = i
            while i < n and not text[i].isspace():
                i += 1
            words.append((text[start:i], start))

        # Greedy line packing: keep adding words while the joined line still fits.
        raw_lines: list[list[tuple[str, int]]] = []
        current_line: list[tuple[str, int]] = []
        current_str = ""
        for word, start in words:
            candidate = (current_str + " " + word).strip() if current_str else word
            if font.size(candidate)[0] <= max_width:
                current_line.append((word, start))
                current_str = candidate
                continue
            if current_line:
                raw_lines.append(current_line)
                current_line = [(word, start)]
                current_str = word
            else:
                # Single word wider than the box -- emit it on its own line
                # rather than infinite-looping trying to fit it.
                raw_lines.append([(word, start)])
                current_line = []
                current_str = ""
        if current_line:
            raw_lines.append(current_line)

        # For each line, walk word-by-word and merge same-colored chars into runs.
        rendered_lines: list[list[tuple[str, tuple[int, int, int]]]] = []
        for line in raw_lines:
            chars: list[str] = []
            colors: list[tuple[int, int, int]] = []
            for word_index, (word, start) in enumerate(line):
                if word_index > 0:
                    # Inter-word space inherits the next word's color so a
                    # highlight phrase that spans multiple words renders as
                    # one continuous colored run.
                    chars.append(" ")
                    colors.append(color_map[start])
                for offset, ch in enumerate(word):
                    chars.append(ch)
                    colors.append(color_map[start + offset])
            runs: list[tuple[str, tuple[int, int, int]]] = []
            if not chars:
                rendered_lines.append(runs)
                continue
            run_text = chars[0]
            run_color = colors[0]
            for ch, color in zip(chars[1:], colors[1:]):
                if color == run_color:
                    run_text += ch
                else:
                    runs.append((run_text, run_color))
                    run_text = ch
                    run_color = color
            runs.append((run_text, run_color))
            rendered_lines.append(runs)
        return rendered_lines

    # ------------------------------------------------------------------
    # Warning and caption lines
    # ------------------------------------------------------------------

    def collect_warning_lines(self, node: MenuNode) -> list[str]:
        """
        Return red-text warnings for the given game node in render order.

        The input-scheme label (when set to anything other than STANDARD)
        takes the upper slot; the optional free-form note sits beneath it.
        If only the note is present, it promotes into the upper slot.

        Args:
            node (MenuNode): The game node to collect warnings for.

        Returns:
            list[str]: Up to two uppercased warning strings.
        """
        lines: list[str] = []
        scheme_label = (
            InputSchemeSettings.LABELS.get(node.input_scheme_key)
            if node.input_scheme_key
            else None
        )
        if scheme_label:
            lines.append(scheme_label)
        if node.note:
            lines.append(node.note)
        return [line.upper() for line in lines]

    def draw_preview_warnings(self, node: MenuNode | None) -> None:
        """
        Render the white caption + up to two warning lines under the preview.

        The caption is a per-game description for sponsor games (pulled from
        GameSettings.GAME_DESCRIPTIONS) and the manifest-supplied byline for
        student games. If a caption is wider than the preview box it wraps
        onto multiple lines, and the warning slots are pushed down by the
        extra lines so they always sit below the caption block.

        Args:
            node (MenuNode | None): The currently highlighted node, or None.
        """
        if node is None or node.kind != "game":
            return

        preview_center_x = MenuSettings.PREVIEW_BOX_X + (MenuSettings.PREVIEW_BOX_WIDTH // 2)

        # Wrap the caption against the preview-box width so a long
        # description flows onto a second/third line instead of bleeding
        # horizontally past the panel above it.
        caption_lines: list[str] = []
        if node.attribution:
            caption_lines = self._wrap_simple(
                node.attribution.upper(), self.hint_font, MenuSettings.PREVIEW_BOX_WIDTH
            )

        line_height = self.hint_font.get_linesize()
        line_spacing = MenuSettings.CAPTION_LINE_SPACING
        last_caption_center_y = MenuSettings.ATTRIBUTION_LINE_CENTER_Y - (line_height + line_spacing)
        for index, line in enumerate(caption_lines):
            center_y = MenuSettings.ATTRIBUTION_LINE_CENTER_Y + index * (line_height + line_spacing)
            line_surface = self.hint_font.render(line, False, ColorSettings.WHITE)
            self.screen.blit(
                line_surface,
                line_surface.get_rect(center=(preview_center_x, center_y)),
            )
            last_caption_center_y = center_y

        # Single-line captions keep the original warning Y positions intact;
        # wrapped captions push the warnings down so they sit below the
        # caption block instead of overlapping it.
        warning_gap = MenuSettings.WARNING_LINE_2_CENTER_Y - MenuSettings.WARNING_LINE_1_CENTER_Y
        pushed_warning_1_y = last_caption_center_y + (line_height + line_spacing)
        warning_1_y = max(MenuSettings.WARNING_LINE_1_CENTER_Y, pushed_warning_1_y)
        warning_2_y = warning_1_y + warning_gap

        warnings = self.collect_warning_lines(node)
        slot_y_positions = (warning_1_y, warning_2_y)
        for slot_index, warning_text in enumerate(warnings):
            warning_surface = self.hint_font.render(warning_text, False, ColorSettings.RED)
            self.screen.blit(
                warning_surface,
                warning_surface.get_rect(center=(preview_center_x, slot_y_positions[slot_index])),
            )

    # ------------------------------------------------------------------
    # Text utilities
    # ------------------------------------------------------------------

    def draw_outlined_text(
        self,
        text: str,
        font: pygame.font.Font,
        fg_color: tuple[int, int, int],
        outline_color: tuple[int, int, int],
        center: tuple[int, int],
    ) -> None:
        """
        Render text with a 1-pixel outline by stamping the outline color around the foreground.

        Args:
            text (str): The string to render.
            font (pygame.font.Font): Font to use for rendering.
            fg_color (tuple): RGB foreground color.
            outline_color (tuple): RGB outline color.
            center (tuple): (x, y) center position for the rendered text.
        """
        fg_surface = font.render(text, False, fg_color)
        outline_surface = font.render(text, False, outline_color)
        fg_rect = fg_surface.get_rect(center=center)
        # All eight neighbors so the outline traces the full glyph silhouette,
        # not just the cardinal sides.
        outline_offsets = (
            (-1, -1), (0, -1), (1, -1),
            (-1,  0),          (1,  0),
            (-1,  1), (0,  1), (1,  1),
        )
        for offset_x, offset_y in outline_offsets:
            self.screen.blit(outline_surface, fg_rect.move(offset_x, offset_y))
        self.screen.blit(fg_surface, fg_rect)

    def _wrap_simple(self, text: str, font: pygame.font.Font, max_width: int) -> list[str]:
        """
        Greedy word-wrap a single-color string into lines fitting ``max_width`` pixels.

        Args:
            text (str): The string to wrap.
            font (pygame.font.Font): Font used to measure pixel widths.
            max_width (int): Maximum pixel width per line.

        Returns:
            list[str]: Wrapped lines.
        """
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = (current + " " + word).strip() if current else word
            if font.size(candidate)[0] <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
                current = word
            else:
                # Single word wider than the box -- emit it on its own line
                # rather than infinite-looping trying to fit it.
                lines.append(word)
                current = ""
        if current:
            lines.append(current)
        return lines

    # ------------------------------------------------------------------
    # Main draw entry point
    # ------------------------------------------------------------------

    def draw(
        self,
        frame: MenuFrame,
        node: MenuNode | None,
        status_message: str,
        status_message_until: int,
    ) -> None:
        """
        Render the full launcher frame and flip the display.

        Args:
            frame (MenuFrame): The currently active menu frame.
            node (MenuNode | None): The currently highlighted node, or None.
            status_message (str): Temporary error/status text (replaces footer line 2 when active).
            status_message_until (int): Timestamp (ms) at which the status message expires.
        """
        self.screen.fill(ColorSettings.BLACK)
        self._draw_header()
        self.draw_menu(frame)
        self.draw_preview_panel(node)
        self.draw_preview_warnings(node)
        self._draw_footer(status_message, status_message_until)
        self.crt.draw()
        pygame.display.flip()
