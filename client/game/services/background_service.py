"""
Background service for managing level backgrounds and transitions.
"""

from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame


class BackgroundPhase(Enum):
    """Different phases of the background display."""

    START_SCREEN = "start_screen"
    TRANSITION = "transition"
    REPEATABLE = "repeatable"
    LEVEL_COMPLETE = "level_complete"


class BackgroundService:
    """Manages level backgrounds, start screens, and transitions."""

    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Current state
        self.current_level = 1
        self.phase = BackgroundPhase.START_SCREEN
        self.scroll_offset = 0.0
        self.transition_progress = 0.0

        # Transition settings
        self.start_screen_duration = 2.0  # seconds to show start screen

        # Background completion settings - will be calculated from image
        self.background_length = 0.0  # Will be set based on actual image size
        self.total_scrolled = 0.0  # total distance scrolled

        # Enhanced scrolling mechanics
        self.current_scroll_speed = 0.0  # Current actual scroll speed
        self.target_scroll_speed = 0.0  # Target scroll speed based on cyclist
        self.scroll_acceleration = 200.0  # pixels/second^2 acceleration
        self.scroll_deceleration = 150.0  # pixels/second^2 deceleration
        self.base_speed_multiplier = 8.0  # Base conversion from mph to pixels/second
        self.max_scroll_speed = 300.0  # Maximum scroll speed (pixels/second)

        # Momentum and smoothing
        self.last_cyclist_speed = 0.0
        self.speed_smoothing_factor = 0.1  # How much to smooth speed changes (0-1)

        # Asset storage
        self.start_screens: Dict[int, Optional[pygame.Surface]] = {}
        self.repeatable_background: Optional[pygame.Surface] = None
        self.scaled_background_width = 0  # Store the scaled width

        # Load assets
        self.load_assets()

        # Track time for start screen
        self.phase_start_time = pygame.time.get_ticks()

    def load_assets(self):
        """Load all background assets."""
        self.load_start_screens()
        self.load_repeatable_background()

    def load_start_screens(self):
        """Load start screen images for all levels."""
        start_screens_path = Path("assets/start_screens")

        if not start_screens_path.exists():
            print(f"Start screens directory not found: {start_screens_path}")
            return

        # Map specific start screens to levels
        level_mapping = {
            1: "williamsburg.png",
            3: "prospect_park_entrance.png",
            4: "prospect_farmers.png",
            2: "wegmans.png",
        }

        # Load mapped start screens
        for level, filename in level_mapping.items():
            file_path = start_screens_path / filename

            if file_path.exists():
                try:
                    image = pygame.image.load(str(file_path)).convert_alpha()
                    # Scale to screen size
                    self.start_screens[level] = pygame.transform.scale(
                        image, (self.screen_width, self.screen_height)
                    )
                    print(f"Loaded start screen for level {level}: {file_path}")
                except pygame.error as e:
                    print(f"Could not load start screen {file_path}: {e}")
                    self.start_screens[level] = self._create_placeholder_start_screen(
                        level
                    )
            else:
                print(f"Start screen not found: {file_path}")
                self.start_screens[level] = self._create_placeholder_start_screen(level)

    def load_repeatable_background(self):
        """Load the repeatable background image."""
        bg_path = Path("assets/repeatable_background.png")

        if bg_path.exists():
            try:
                self.repeatable_background = pygame.image.load(
                    str(bg_path)
                ).convert_alpha()

                # Calculate the scaled dimensions
                bg_height = self.repeatable_background.get_height()
                scale_factor = self.screen_height / bg_height
                self.scaled_background_width = int(
                    self.repeatable_background.get_width() * scale_factor
                )

                # Set background length to the actual image width (scaled)
                # Multiply by a factor to make levels longer if desired
                self.background_length = float(
                    self.scaled_background_width * 3
                )  # 3x the image width

                print(f"Loaded repeatable background: {bg_path}")
                print(f"Scaled background width: {self.scaled_background_width}px")
                print(f"Background length set to: {self.background_length}px")
            except pygame.error as e:
                print(f"Could not load repeatable background: {e}")
                self.repeatable_background = None
                self.scaled_background_width = 800  # Default fallback
                self.background_length = 2400.0  # Default fallback
        else:
            print(f"Repeatable background not found: {bg_path}")
            self.repeatable_background = None
            self.scaled_background_width = 800  # Default fallback
            self.background_length = 2400.0  # Default fallback

    def _create_placeholder_start_screen(self, level: int) -> pygame.Surface:
        """Create a simple placeholder start screen."""
        surface = pygame.Surface((self.screen_width, self.screen_height))

        # Gradient background
        for y in range(self.screen_height):
            if y < self.screen_height * 0.7:
                # Sky - different color per level
                hue = (level * 30) % 360
                blue_intensity = int(135 + (y / (self.screen_height * 0.7)) * 50)
                color = (135, 206, min(255, blue_intensity))
            else:
                # Ground
                green_intensity = int(
                    34
                    + ((y - self.screen_height * 0.7) / (self.screen_height * 0.3))
                    * 100
                )
                color = (green_intensity, min(255, green_intensity + 100), 34)

            pygame.draw.line(surface, color, (0, y), (self.screen_width, y))

        # Add level text
        font = pygame.font.Font(None, 64)
        level_text = font.render(f"Level {level}", True, (255, 255, 255))
        text_rect = level_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )
        surface.blit(level_text, text_rect)

        # Add starting line or platform
        platform_rect = pygame.Rect(50, self.screen_height - 100, 200, 20)
        pygame.draw.rect(surface, (100, 100, 100), platform_rect)

        return surface

    def set_level(self, level: int):
        """Set the current level and reset to start screen."""
        self.current_level = level
        self.phase = BackgroundPhase.START_SCREEN
        self.scroll_offset = 0.0
        self.transition_progress = 0.0
        self.total_scrolled = 0.0

        # Background length is now based on the actual image, but we can still
        # vary it by level if desired (making later levels longer)
        base_length = 5000
        level_multiplier = 1.0 + (level - 1) * 0.2  # Each level is 20% longer
        self.background_length = base_length * level_multiplier

        self.phase_start_time = pygame.time.get_ticks()
        print(
            f"Set background to level {level} (length: {self.background_length:.0f}px)"
        )

    def start_riding(self):
        """Start the transition from start screen to repeatable background."""
        if self.phase == BackgroundPhase.START_SCREEN:
            self.phase = BackgroundPhase.TRANSITION
            self.phase_start_time = pygame.time.get_ticks()

    def update(self, dt: float, cyclist_speed: float):
        """Update background based on current phase and cyclist speed."""
        if self.phase == BackgroundPhase.START_SCREEN:
            # Stay on start screen until player starts pedaling
            pass

        elif self.phase == BackgroundPhase.TRANSITION:
            # Transition from start screen to repeatable background
            # Only move if cyclist is actually moving
            if cyclist_speed > 0:
                scroll_speed = (
                    cyclist_speed * self.base_speed_multiplier
                )  # Apply multiplier
                self.transition_progress += scroll_speed * (dt / 1000.0)

                # Switch to repeatable phase when transition is complete
                if self.transition_progress >= self.screen_width:
                    self.phase = BackgroundPhase.REPEATABLE
                    self.scroll_offset = 0.0
                    self.total_scrolled = 0.0

        elif self.phase == BackgroundPhase.REPEATABLE:
            # Scroll the repeatable background based on cyclist speed
            if cyclist_speed > 0:
                scroll_speed = (
                    cyclist_speed * self.base_speed_multiplier
                )  # Apply multiplier
                scroll_distance = scroll_speed * (dt / 1000.0)
                self.scroll_offset += scroll_distance
                self.total_scrolled += scroll_distance

                # Check if we've reached the end of the background
                if self.total_scrolled >= self.background_length:
                    self.phase = BackgroundPhase.LEVEL_COMPLETE

        elif self.phase == BackgroundPhase.LEVEL_COMPLETE:
            # Background is complete, cyclist will ride off screen
            pass

    def draw(self, screen: pygame.Surface):
        """Draw the current background phase."""
        if self.phase == BackgroundPhase.START_SCREEN:
            self._draw_start_screen(screen)

        elif self.phase == BackgroundPhase.TRANSITION:
            self._draw_transition(screen)

        elif self.phase == BackgroundPhase.REPEATABLE:
            self._draw_repeatable(screen)

        elif self.phase == BackgroundPhase.LEVEL_COMPLETE:
            # Show the final position of the repeatable background
            self._draw_repeatable_final(screen)

    def _draw_start_screen(self, screen: pygame.Surface):
        """Draw the level start screen."""
        start_screen = self.start_screens.get(self.current_level)

        if start_screen:
            screen.blit(start_screen, (0, 0))
        else:
            # Fallback: simple gradient
            self._draw_fallback_background(screen)

    def _draw_transition(self, screen: pygame.Surface):
        """Draw the transition from start screen to repeatable background."""
        # Draw start screen sliding out to the left
        start_screen = self.start_screens.get(self.current_level)
        if start_screen:
            start_x = -int(self.transition_progress)
            screen.blit(start_screen, (start_x, 0))

        # Draw repeatable background sliding in from the right
        if self.repeatable_background:
            bg_x = self.screen_width - int(self.transition_progress)
            self._draw_repeatable_at_position(screen, bg_x)
        else:
            # Fill the incoming area with fallback
            incoming_rect = pygame.Rect(
                self.screen_width - int(self.transition_progress),
                0,
                int(self.transition_progress),
                self.screen_height,
            )
            pygame.draw.rect(screen, (135, 206, 235), incoming_rect)

    def _draw_repeatable(self, screen: pygame.Surface):
        """Draw the repeatable background with scrolling."""
        if self.repeatable_background:
            # Use the pre-calculated scaled width
            scaled_width = self.scaled_background_width
            scaled_height = self.screen_height

            scaled_bg = pygame.transform.scale(
                self.repeatable_background, (scaled_width, scaled_height)
            )

            # Draw tiled background with scrolling
            offset_x = int(self.scroll_offset) % scaled_width

            # Draw background tiles
            x = -offset_x
            while x < self.screen_width:
                screen.blit(scaled_bg, (x, 0))
                x += scaled_width
        else:
            # Fallback background
            self._draw_fallback_background(screen)

    def _draw_repeatable_at_position(self, screen: pygame.Surface, x: int):
        """Draw repeatable background at a specific x position."""
        if self.repeatable_background:
            # Use the pre-calculated scaled dimensions
            scaled_width = self.scaled_background_width
            scaled_height = self.screen_height

            scaled_bg = pygame.transform.scale(
                self.repeatable_background, (scaled_width, scaled_height)
            )

            # Draw background starting at x position
            current_x = x
            while current_x < self.screen_width:
                screen.blit(scaled_bg, (current_x, 0))
                current_x += scaled_width

    def _draw_fallback_background(self, screen: pygame.Surface):
        """Draw a simple gradient fallback background."""
        for y in range(self.screen_height):
            if y < self.screen_height * 0.7:
                # Sky
                blue_intensity = int(135 + (y / (self.screen_height * 0.7)) * 50)
                color = (135, 206, min(255, blue_intensity))
            else:
                # Ground
                green_intensity = int(
                    34
                    + ((y - self.screen_height * 0.7) / (self.screen_height * 0.3))
                    * 100
                )
                color = (green_intensity, min(255, green_intensity + 100), 34)

            pygame.draw.line(screen, color, (0, y), (self.screen_width, y))

    def get_cyclist_start_position(self) -> Tuple[int, int]:
        """Get the starting position for the cyclist on the current level."""
        # Position cyclist on the starting platform/area
        start_x = 100  # A bit in from the left edge
        start_y = self.screen_height - 150  # Above the ground
        return start_x, start_y

    def is_on_start_screen(self) -> bool:
        """Check if we're still showing the start screen."""
        return self.phase == BackgroundPhase.START_SCREEN

    def _draw_repeatable_final(self, screen: pygame.Surface):
        """Draw the final position of repeatable background when level is complete."""
        # For the final position, just draw the background normally
        # The level is complete, so we can show the end
        if self.repeatable_background:
            scaled_width = self.scaled_background_width
            scaled_height = self.screen_height

            scaled_bg = pygame.transform.scale(
                self.repeatable_background, (scaled_width, scaled_height)
            )

            # Calculate final offset based on total distance traveled
            final_offset = int(self.total_scrolled) % scaled_width
            x = -final_offset

            # Draw remaining background tiles
            tiles_drawn = 0
            while (
                x < self.screen_width and tiles_drawn < 3
            ):  # Limit to avoid infinite loop
                screen.blit(scaled_bg, (x, 0))
                x += scaled_width
                tiles_drawn += 1

            # Fill any remaining space with sky color
            if x < self.screen_width:
                remaining_rect = pygame.Rect(
                    x, 0, self.screen_width - x, self.screen_height
                )
                pygame.draw.rect(screen, (135, 206, 235), remaining_rect)
        else:
            # Fallback background
            self._draw_fallback_background(screen)

    def is_level_complete(self) -> bool:
        """Check if the level is complete (background has ended)."""
        return self.phase == BackgroundPhase.LEVEL_COMPLETE

    def get_cyclist_fixed_position(self) -> Tuple[int, int]:
        """Get the fixed position where the cyclist should stay during scrolling."""
        # Keep cyclist at a fixed position during the scrolling phase
        fixed_x = 200  # Fixed position from left edge
        fixed_y = self.screen_height - 150  # Above the ground
        return fixed_x, fixed_y

    def should_cyclist_move_right(self) -> bool:
        """Check if the cyclist should move right (level complete phase)."""
        return self.phase == BackgroundPhase.LEVEL_COMPLETE
