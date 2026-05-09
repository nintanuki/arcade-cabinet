import pygame
import random
from core.sprites import Fish
from settings import FishSettings, PlayerSettings

class FishManager:
    """Spawn fish, update fish lifecycle, and resolve player-vs-fish collisions."""

    def __init__(self, sprite_group):
        """Store references and initialize spawn timing state.

        Args:
            sprite_group: Pygame sprite group that contains all enemy fish.
        """
        self.sprite_group = sprite_group
        self.spawn_timer = 0

    def update(self, player=None):
        """Advance fish systems by one frame.

        Args:
            player: The player fish sprite used for collision checks, or None
                to run spawn/movement without collisions.

        Returns:
            tuple[bool, list[int]]: (game_over, eaten_fish_sizes) — True when
            the player was eaten this frame, and a list of eaten fish sizes.
        """
        self.spawn_timer += 1
        if self.spawn_timer >= FishSettings.SPAWN_RATE:
            self.spawn_fish()
            self.spawn_timer = 0

        if player is None:
            return False, []

        return self.check_collisions(player)

    def spawn_fish(self):
        """Create one fish with skewed-small size distribution and inverse speed."""
        side = random.choice(["left", "right"])

        # random.random() gives 0.0 to 1.0. 
        # Squaring it (or cubing it) makes small numbers much more common.
        skew_factor = random.random()**16  # Higher exponent = more small fish
        size_range = FishSettings.MAX_SIZE - FishSettings.MIN_SIZE
        size = int(FishSettings.MIN_SIZE + (skew_factor * size_range))

        # Calculate speed (Inversely proportional to size)
        size_range = FishSettings.MAX_SIZE - FishSettings.MIN_SIZE
        # We use a 0.0 to 1.0 ratio of where this fish sits in the size range
        size_ratio = (size - FishSettings.MIN_SIZE) / size_range

        speed_range = FishSettings.MAX_SPEED - FishSettings.MIN_SPEED
        # 1.0 ratio (big fish) -> Min Speed | 0.0 ratio (small fish) -> Max Speed
        speed = FishSettings.MAX_SPEED - (size_ratio * speed_range)
        
        new_fish = Fish(side, size, speed)
        self.sprite_group.add(new_fish)

    def check_collisions(self, player):
        """Resolve collisions and report whether the player was eaten.

        Args:
            player: The player fish sprite.

        Returns:
            tuple[bool, list[int]]: (game_over, eaten_fish_sizes) — True if a
            larger or equal fish consumed the player, and eaten fish sizes.
        """
        # We use pygame.sprite.spritecollide with a custom callback or manual loop
        # We pass False for dokill because we want to decide which one gets removed (player or fish) based on their relative sizes.
        collided_fish = pygame.sprite.spritecollide(player, self.sprite_group, False, pygame.sprite.collide_mask)

        eaten_sizes = []
        # If there are multiple collisions in the same frame, we process them one at a time.
        for fish in collided_fish:
            # Compare conceptual sizes directly — both player.size and fish.size are the
            # same unit (body width in pixels), so this is an apples-to-apples comparison.
            # Using player.rect area was wrong because the rect height includes the bow,
            # inflating the player's apparent size relative to enemies.
            if player.size > fish.size:
                # Player eats fish
                fish.kill()
                self.grow_player(player, fish)
                eaten_sizes.append(fish.size)
            else:
                # Fish eats player
                return True, eaten_sizes

        return False, eaten_sizes

    def grow_player(self, player, fish):
        """Increase player size after eating a fish.

        Args:
            player: The player fish sprite that should grow.
            fish: The eaten fish used to derive growth amount.
        """
        growth_amount = fish.size * PlayerSettings.PLAYER_GROWTH_COEFFICIENT
        player.grow(growth_amount)