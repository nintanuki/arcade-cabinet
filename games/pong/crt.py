"""CRT overlay effect helpers for Pong."""

from settings import *
import random

class CRT:
    """Draw a CRT-style flicker and scanline overlay."""

    def __init__(self,screen):
        """Initialize the CRT overlay texture and target screen.

        Args:
            screen (pygame.Surface): Display surface receiving the overlay.

        Returns:
            None.
        """
        super().__init__()
        self.screen = screen
        self.tv = pygame.image.load('graphics/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv,(SCREEN_WIDTH,SCREEN_HEIGHT))

    def create_crt_lines(self):
        """Draw horizontal scanlines into the CRT texture.

        Args:
            None.

        Returns:
            None.
        """
        # TODO(bug): Lines are drawn into the same surface each frame and can accumulate.
        line_height = 3
        line_amount = int(SCREEN_HEIGHT / line_height)
        for line in range(line_amount):
            y_pos = line * line_height
            pygame.draw.line(self.tv,'black',(0,y_pos),(SCREEN_WIDTH,y_pos),1)

    def draw(self):
        """Flicker the overlay alpha and blit it onto the screen.

        Args:
            None.

        Returns:
            None.
        """
        self.tv.set_alpha(random.randint(75,90))
        self.create_crt_lines()
        self.screen.blit(self.tv,(0,0))