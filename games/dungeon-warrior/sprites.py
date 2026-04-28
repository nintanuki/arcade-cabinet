"""Sprites used by the action window.

Right now only a temporary placeholder player exists so we can verify the UI
frames render and the joystick / keyboard plumbing is alive end-to-end. When
the real player class lands it will replace DebugPlayer behind the same
GameManager.player attribute used by the renderer.
"""

import pygame

from settings import (
    ColorSettings,
    DebugPlayerSettings,
    GridSettings,
    InputSettings,
    UISettings,
)


class DebugPlayer:
    """Red-square placeholder player constrained to the active cell.

    Reads the keyboard (WASD / arrow keys) and the left analog stick on every
    connected controller, normalizes the resulting movement vector so diagonals
    are not faster than orthogonal motion, applies axis-separated AABB
    collision against the cell's wall tiles, and triggers a cell transition
    when the rect crosses the action window edge.
    """

    def __init__(self, game) -> None:
        """Spawn the player centered in the action window.

        Args:
            game: Active GameManager. Used to reach connected_joysticks
                and the active world state.
        """
        self.game = game
        self.size = GridSettings.TILE_SIZE

        # Collision hitbox is smaller than the visual sprite so the player
        # can squeeze through 1-tile-wide openings without pixel-perfect
        # alignment. Visual drawing still uses self.size; collision and
        # edge-crossing checks use the inset hitbox.
        inset = DebugPlayerSettings.HITBOX_INSET
        self.hitbox_offset = inset
        self.hitbox_size = self.size - (2 * inset)

        # Float position so sub-pixel velocities accumulate smoothly even
        # though we render at integer coordinates.
        center_x = UISettings.ACTION_WINDOW_X + (UISettings.ACTION_WINDOW_WIDTH // 2)
        center_y = UISettings.ACTION_WINDOW_Y + (UISettings.ACTION_WINDOW_HEIGHT // 2)
        self.x = float(center_x - (self.size // 2))
        self.y = float(center_y - (self.size // 2))

        # Action-window edges (the outer rectangle the player must stay
        # inside of, except at openings where they trigger a cell swap).
        self._aw_left = float(UISettings.ACTION_WINDOW_X)
        self._aw_top = float(UISettings.ACTION_WINDOW_Y)
        self._aw_right = float(UISettings.ACTION_WINDOW_X + UISettings.ACTION_WINDOW_WIDTH)
        self._aw_bottom = float(UISettings.ACTION_WINDOW_Y + UISettings.ACTION_WINDOW_HEIGHT)
        self._max_x = self._aw_right - self.size
        self._max_y = self._aw_bottom - self.size

    # -------------------------
    # INPUT
    # -------------------------

    def _read_keyboard(self) -> tuple[float, float]:
        """Return a (dx, dy) unit-ish direction vector from held keys."""
        keys = pygame.key.get_pressed()
        dx = 0.0
        dy = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1.0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1.0
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1.0
        return dx, dy

    def _read_left_stick(self) -> tuple[float, float]:
        """Sum the left-stick deflection across all connected joysticks.

        Values inside the deadzone are zeroed so a resting stick contributes
        nothing.
        """
        dx = 0.0
        dy = 0.0
        deadzone = DebugPlayerSettings.STICK_DEADZONE
        for joystick in self.game.connected_joysticks:
            ax = joystick.get_axis(InputSettings.JOY_AXIS_LEFT_X)
            ay = joystick.get_axis(InputSettings.JOY_AXIS_LEFT_Y)
            if abs(ax) > deadzone:
                dx += ax
            if abs(ay) > deadzone:
                dy += ay
        return dx, dy

    # -------------------------
    # COLLISION
    # -------------------------

    def _rect_overlaps_wall(self, x: float, y: float) -> bool:
        """Return True if the AABB at (x, y, size, size) overlaps any wall tile.

        Only the active cell's grid is queried; out-of-bounds is treated as
        non-wall by World.is_wall so the player can leave the action window
        through openings.
        """
        tile_size = GridSettings.TILE_SIZE
        aw_left = UISettings.ACTION_WINDOW_X
        aw_top = UISettings.ACTION_WINDOW_Y

        # Convert visual top-left to hitbox top-left/right/bottom for the
        # inclusive cell range the hitbox covers.
        hx = x + self.hitbox_offset
        hy = y + self.hitbox_offset
        hsize = self.hitbox_size
        left_col = int((hx - aw_left) // tile_size)
        right_col = int((hx + hsize - 1 - aw_left) // tile_size)
        top_row = int((hy - aw_top) // tile_size)
        bottom_row = int((hy + hsize - 1 - aw_top) // tile_size)

        world = self.game.world
        for row in range(top_row, bottom_row + 1):
            for col in range(left_col, right_col + 1):
                if world.is_wall(col, row):
                    return True
        return False

    # -------------------------
    # EDGE CROSSING
    # -------------------------

    def _cell_step_for_current_position(self) -> tuple[int, int]:
        """If the rect has crossed the action window border, return the (dx, dy) cell offset.

        Returns (0, 0) when the player is still inside the action window.
        Trigger fires on first overlap of any edge -- i.e., as soon as any
        part of the rect crosses the boundary line.
        """
        # Use the hitbox (not the visual rect) so the trigger lines up with
        # what collision considers "the player." The visual sprite slips a
        # few pixels past the action window edge before the swap fires,
        # which feels right when openings are tile-sized.
        hx = self.x + self.hitbox_offset
        hy = self.y + self.hitbox_offset
        hsize = self.hitbox_size

        dx_cells = 0
        dy_cells = 0
        if hx + hsize > self._aw_right:
            dx_cells = 1
        elif hx < self._aw_left:
            dx_cells = -1
        if hy + hsize > self._aw_bottom:
            dy_cells = 1
        elif hy < self._aw_top:
            dy_cells = -1
        return dx_cells, dy_cells

    def _on_cell_swap(self, dx_cells: int, dy_cells: int) -> None:
        """Place the player flush against the entry edge of the new cell."""
        if dx_cells == 1:
            self.x = self._aw_left
        elif dx_cells == -1:
            self.x = self._max_x
        if dy_cells == 1:
            self.y = self._aw_top
        elif dy_cells == -1:
            self.y = self._max_y

    def _clamp_to_action_window(self) -> None:
        """Pull the player back inside when no neighbor cell exists."""
        if self.x < self._aw_left:
            self.x = self._aw_left
        elif self.x > self._max_x:
            self.x = self._max_x
        if self.y < self._aw_top:
            self.y = self._aw_top
        elif self.y > self._max_y:
            self.y = self._max_y

    # -------------------------
    # UPDATE / DRAW
    # -------------------------

    def update(self) -> None:
        """Advance the player one frame using current input state."""
        kb_dx, kb_dy = self._read_keyboard()
        js_dx, js_dy = self._read_left_stick()
        dx = kb_dx + js_dx
        dy = kb_dy + js_dy

        magnitude_squared = (dx * dx) + (dy * dy)
        if magnitude_squared > 1.0:
            magnitude = magnitude_squared ** 0.5
            dx /= magnitude
            dy /= magnitude

        speed = DebugPlayerSettings.SPEED

        # Axis-separated movement so a diagonal that grazes a wall on one
        # axis still lets the player slide along the wall on the other.
        proposed_x = self.x + dx * speed
        if not self._rect_overlaps_wall(proposed_x, self.y):
            self.x = proposed_x

        proposed_y = self.y + dy * speed
        if not self._rect_overlaps_wall(self.x, proposed_y):
            self.y = proposed_y

        # Cell transitions: if the rect crossed the window edge, ask the
        # world to swap; on success we move to the matching entry side,
        # on failure (no neighbor) we clamp back inside.
        dx_cells, dy_cells = self._cell_step_for_current_position()
        if dx_cells == 0 and dy_cells == 0:
            return

        if self.game.world.step_to_neighbor(dx_cells, dy_cells):
            self._on_cell_swap(dx_cells, dy_cells)
        else:
            self._clamp_to_action_window()

    def draw(self, surface) -> None:
        """Render the placeholder red square at the current position."""
        rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        pygame.draw.rect(surface, DebugPlayerSettings.COLOR, rect)
