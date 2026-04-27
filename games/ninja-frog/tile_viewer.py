"""
tile_viewer.py — drop this in your project root and run it.
Click any tile to see its index. Press Q or Escape to quit.
"""
 
import pygame
import sys
 
# ── Config ────────────────────────────────────────────────────────────────────
SHEET_PATH  = 'graphics/Terrain/Terrain (16x16).png'
TILE_SIZE   = 16          # native size in the sheet
SCALE       = 4           # how much to zoom each tile in the viewer
COLS        = 22
ROWS        = 11
PADDING     = 4           # gap between tiles (scaled pixels)
MARGIN      = 20          # outer margin
INFO_HEIGHT = 60          # space at the bottom for the info bar
 
# Derived
CELL  = TILE_SIZE * SCALE + PADDING
W     = MARGIN * 2 + COLS * CELL - PADDING
H     = MARGIN * 2 + ROWS * CELL - PADDING + INFO_HEIGHT
 
BG          = (13,  13,  15)
GRID_COLOR  = (30,  30,  40)
HOVER_COLOR = (87, 200, 255)
SEL_COLOR   = (200, 255, 87)
TEXT_COLOR  = (197, 197, 212)
DIM_COLOR   = (90,  90, 114)
# ──────────────────────────────────────────────────────────────────────────────
 
def load_tiles(path):
    sheet = pygame.image.load(path).convert_alpha()
    tiles = []
    for row in range(ROWS):
        for col in range(COLS):
            tile = sheet.subsurface((col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            scaled = pygame.transform.scale(tile, (TILE_SIZE * SCALE, TILE_SIZE * SCALE))
            tiles.append(scaled)
    return tiles
 
 
def index_at(mx, my):
    """Return the tile index under the mouse, or None if outside the grid."""
    gx = mx - MARGIN
    gy = my - MARGIN
    if gx < 0 or gy < 0:
        return None
    col = gx // CELL
    row = gy // CELL
    # Check we're inside the tile itself, not the gap
    if gx % CELL >= TILE_SIZE * SCALE or gy % CELL >= TILE_SIZE * SCALE:
        return None
    if col >= COLS or row >= ROWS:
        return None
    return row * COLS + col
 
 
def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption('Tile Viewer')
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont('monospace', 13)
    font_b = pygame.font.SysFont('monospace', 13, bold=True)
 
    try:
        tiles = load_tiles(SHEET_PATH)
    except FileNotFoundError:
        print(f"Could not find sheet at: {SHEET_PATH}")
        print("Make sure you run this script from your project root.")
        sys.exit(1)
 
    selected = None
 
    while True:
        mx, my = pygame.mouse.get_pos()
        hovered = index_at(mx, my)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered is not None:
                    selected = hovered
 
        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BG)
 
        for idx, tile in enumerate(tiles):
            row = idx // COLS
            col = idx % COLS
            x = MARGIN + col * CELL
            y = MARGIN + row * CELL
 
            screen.blit(tile, (x, y))
 
            # Highlight border
            rect = pygame.Rect(x - 1, y - 1, TILE_SIZE * SCALE + 2, TILE_SIZE * SCALE + 2)
            if idx == selected:
                pygame.draw.rect(screen, SEL_COLOR, rect, 2)
            elif idx == hovered:
                pygame.draw.rect(screen, HOVER_COLOR, rect, 1)
 
        # ── Info bar ──────────────────────────────────────────────────────────
        bar_y = H - INFO_HEIGHT
        pygame.draw.line(screen, GRID_COLOR, (0, bar_y), (W, bar_y))
 
        if selected is not None:
            sel_row = selected // COLS
            sel_col = selected % COLS
            px, py  = sel_col * TILE_SIZE, sel_row * TILE_SIZE
 
            parts = [
                (SEL_COLOR,  f'tiles[{selected}]   '),
                (DIM_COLOR,  f'row={sel_row}  col={sel_col}  '),
                (DIM_COLOR,  f'sheet offset=({px}, {py})   '),
                (TEXT_COLOR, f'subsurface(({px}, {py}, 16, 16))'),
            ]
            x_cursor = MARGIN
            for color, text in parts:
                surf = font_b.render(text, True, color)
                screen.blit(surf, (x_cursor, bar_y + 14))
                x_cursor += surf.get_width()
 
            hint = font.render('click to select  |  Q / Esc to quit', True, DIM_COLOR)
            screen.blit(hint, (MARGIN, bar_y + 36))
        else:
            msg = font.render('Click a tile to select it   |   Q / Esc to quit', True, DIM_COLOR)
            screen.blit(msg, (MARGIN, bar_y + 20))
 
        pygame.display.flip()
        clock.tick(60)
 
 
if __name__ == '__main__':
    main()