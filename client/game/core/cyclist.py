"""
Cyclist component for managing the player character.
"""

from pathlib import Path
from typing import Dict, Optional

import pygame


class Cyclist:
    """Manages the cyclist player character state and animations."""

    def __init__(self, x: int = 150, y: int = 250, width: int = 100, height: int = 100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Animation state
        self.sprite_state = "flat"  # 'flat' or 'up'
        self.animation_timer = 0.0
        self.animation_speed = 200  # ms between frames

        # Movement state
        self.is_riding = True
        self.fall_animation_progress = 0.0

        # Load sprites
        self.sprites: Dict[str, Optional[pygame.Surface]] = {}
        self.load_sprites()

    def load_sprites(self):
        """Load cyclist sprites."""
        asset_path = Path("assets")
        sprite_files = {
            "flat": asset_path / "cyclist_flat.png",
            "up": asset_path / "cyclist_up.png",
        }

        for state, file_path in sprite_files.items():
            if file_path.exists():
                try:
                    sprite = pygame.image.load(str(file_path)).convert_alpha()
                    self.sprites[state] = pygame.transform.scale(
                        sprite, (self.width, self.height)
                    )
                except pygame.error as e:
                    print(f"Could not load cyclist sprite {state}: {e}")
                    self.sprites[state] = None
            else:
                print(f"Cyclist sprite not found: {file_path}")
                self.sprites[state] = None

    def pedal(self, side: str):
        """Animate pedaling action."""
        if not self.is_riding:
            return

        # Toggle sprite state for pedaling animation
        self.sprite_state = "up" if self.sprite_state == "flat" else "flat"
        self.animation_timer = 0.0

    def fall(self):
        """Handle cyclist falling."""
        self.is_riding = False
        self.fall_animation_progress = 0.0
        self.sprite_state = "flat"

    def get_back_up(self):
        """Get the cyclist back up after falling."""
        self.is_riding = True
        self.fall_animation_progress = 0.0
        self.sprite_state = "flat"

    def update(self, dt: float):
        """Update cyclist state and animations."""
        self.animation_timer += dt

        # Handle fall animation
        if not self.is_riding:
            self.fall_animation_progress = min(
                1.0, self.fall_animation_progress + dt / 1000.0
            )

        # Auto-return to flat position after pedaling
        if self.sprite_state == "up" and self.animation_timer > self.animation_speed:
            self.sprite_state = "flat"

    def draw(self, screen: pygame.Surface):
        """Draw the cyclist."""
        current_sprite = self.sprites.get(self.sprite_state)

        if current_sprite:
            # Calculate position with fall animation
            draw_y = self.y
            if not self.is_riding:
                # Slight fall animation - cyclist tilts down
                fall_offset = int(self.fall_animation_progress * 20)
                draw_y += fall_offset

            screen.blit(current_sprite, (self.x, draw_y))
        else:
            # Fallback: draw a simple rectangle
            color = (255, 100, 100) if not self.is_riding else (100, 150, 255)
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(screen, color, rect)

            # Draw a simple cyclist representation
            # Head
            head_radius = 15
            head_center = (self.x + self.width // 2, self.y + 20)
            pygame.draw.circle(screen, (255, 220, 177), head_center, head_radius)

            # Body
            body_rect = pygame.Rect(self.x + self.width // 2 - 10, self.y + 35, 20, 40)
            pygame.draw.rect(screen, (100, 100, 255), body_rect)

    def get_rect(self) -> pygame.Rect:
        """Get the cyclist's bounding rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)
