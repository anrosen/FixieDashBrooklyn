"""
Timing system for rhythm-based cycling mechanics.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import pygame


@dataclass
class PedalResult:
    """Result of a pedal input attempt."""

    success: bool
    timing_quality: str  # 'perfect', 'good', 'bad', 'miss'
    speed_change: float
    muscle_cost: float
    message: str


class TimingSystem:
    """Manages the timing bar and pedaling rhythm mechanics."""

    def __init__(self, screen_width: int):
        self.screen_width = screen_width

        # Timing bar properties
        self.bar_x = 50
        self.bar_y = 20
        self.bar_width = screen_width - 100
        self.bar_height = 30

        # Timing line state
        self.timing_position = 0.0  # 0.0 to 1.0 across the bar
        self.timing_speed = 0.01  # How fast the line moves per frame

        # Green zone (perfect timing area)
        self.green_zone_size = 0.03  # Width of perfect timing zone
        self.green_zone_center = 0.5  # Will be dynamic based on speed

        # Pedaling state
        self.last_pedal_side: Optional[str] = None
        self.last_pedal_time = pygame.time.get_ticks()

        # Rhythm tracking
        self.rhythm_tolerance_min = 200  # Minimum ms between pedals
        self.rhythm_tolerance_max = 1200  # Maximum ms between pedals

    def update_green_zone(self, current_speed: float, max_speed: float):
        """Update green zone position based on current speed."""
        # Green zone moves right as speed increases (making it harder)
        speed_ratio = current_speed / max_speed if max_speed > 0 else 0
        self.green_zone_center = 0.3 + (speed_ratio * 0.6)  # Range: 0.3 to 0.9

    def update(self, dt: float):
        """Update timing system."""
        # Move timing line
        self.timing_position += self.timing_speed

        # Reset timing line when it reaches the end
        if self.timing_position >= 1.0:
            self.timing_position = 0.0

    def attempt_pedal(
        self, side: str, current_speed: float, max_speed: float
    ) -> PedalResult:
        """Process a pedal input and return the result."""
        now = pygame.time.get_ticks()

        # Check alternating requirement
        if self.last_pedal_side == side:
            return PedalResult(
                success=False,
                timing_quality="miss",
                speed_change=0.0,
                muscle_cost=0.0,
                message="Must alternate left/right pedals!",
            )

        # Check rhythm timing (after first pedal)
        if self.last_pedal_side is not None:
            time_since_last = now - self.last_pedal_time

            if time_since_last < self.rhythm_tolerance_min:
                return PedalResult(
                    success=False,
                    timing_quality="miss",
                    speed_change=-5.0,  # Penalty for being too fast
                    muscle_cost=0.5,
                    message="Too fast! Maintain rhythm!",
                )
            elif time_since_last > self.rhythm_tolerance_max:
                return PedalResult(
                    success=False,
                    timing_quality="miss",
                    speed_change=-8.0,  # Penalty for being too slow
                    muscle_cost=0.8,
                    message="Too slow! Keep up the pace!",
                )

        # Update state
        self.last_pedal_side = side
        self.last_pedal_time = now

        # Calculate timing quality based on green zone
        distance_from_green = abs(self.timing_position - self.green_zone_center)

        if distance_from_green <= self.green_zone_size / 2:
            # Perfect hit!
            return PedalResult(
                success=True,
                timing_quality="perfect",
                speed_change=3.0,
                muscle_cost=-0.2,  # Restore some muscle
                message="Perfect!",
            )
        elif distance_from_green <= self.green_zone_size:
            # Good hit
            return PedalResult(
                success=True,
                timing_quality="good",
                speed_change=2.0,
                muscle_cost=0.1,
                message="Good!",
            )
        else:
            # Calculate speed change based on timing
            if self.timing_position < self.green_zone_center:
                # Early = speed up but costs muscle
                speed_change = distance_from_green * 8  # More aggressive speed increase
                muscle_cost = distance_from_green * 1.2
                message = "Early! Speed up!"
            else:
                # Late = slow down
                speed_change = -distance_from_green * 6
                muscle_cost = distance_from_green * 0.8
                message = "Late! Slow down!"

            return PedalResult(
                success=True,
                timing_quality="bad",
                speed_change=speed_change,
                muscle_cost=muscle_cost,
                message=message,
            )

    def draw(self, screen: pygame.Surface, current_speed: float, max_speed: float):
        """Draw the timing bar system."""
        # Update green zone position
        self.update_green_zone(current_speed, max_speed)

        # Draw background
        bg_rect = pygame.Rect(
            self.bar_x - 5, self.bar_y - 5, self.bar_width + 10, self.bar_height + 10
        )
        pygame.draw.rect(screen, (0, 0, 0, 204), bg_rect)

        # Draw gradient timing bar
        self._draw_gradient_bar(screen)

        # Draw green zone
        self._draw_green_zone(screen)

        # Draw timing line
        self._draw_timing_line(screen)

        # Draw border
        border_rect = pygame.Rect(
            self.bar_x, self.bar_y, self.bar_width, self.bar_height
        )
        pygame.draw.rect(screen, (255, 255, 255), border_rect, 2)

        # Draw instructions
        self._draw_instructions(screen)

    def _draw_gradient_bar(self, screen: pygame.Surface):
        """Draw the colorful gradient timing bar."""
        segment_width = self.bar_width // 100

        for i in range(100):
            segment_x = self.bar_x + i * segment_width
            ratio = i / 100.0

            # Create color gradient (red->yellow->green->yellow->red)
            if ratio < 0.25:
                r, g, b = 255, int(255 * (ratio / 0.25)), 0
            elif ratio < 0.5:
                r, g, b = int(255 * (1 - (ratio - 0.25) / 0.25)), 255, 0
            elif ratio < 0.75:
                r, g, b = 0, 255, int(255 * ((ratio - 0.5) / 0.25))
            else:
                r, g, b = (
                    int(255 * ((ratio - 0.75) / 0.25)),
                    int(255 * (1 - (ratio - 0.75) / 0.25)),
                    255,
                )

            color = (r, g, b)
            segment_rect = pygame.Rect(
                segment_x, self.bar_y, segment_width + 1, self.bar_height
            )
            pygame.draw.rect(screen, color, segment_rect)

    def _draw_green_zone(self, screen: pygame.Surface):
        """Draw the green timing zone."""
        zone_x = self.bar_x + (self.green_zone_center * self.bar_width)
        zone_width = self.green_zone_size * self.bar_width

        # Green zone highlight
        highlight_rect = pygame.Rect(
            zone_x - zone_width // 2, self.bar_y, zone_width, self.bar_height
        )
        highlight_surface = pygame.Surface((zone_width, self.bar_height))
        highlight_surface.set_alpha(128)
        highlight_surface.fill((255, 255, 255))
        screen.blit(highlight_surface, (zone_x - zone_width // 2, self.bar_y))

        # Green zone center line
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (zone_x, self.bar_y - 5),
            (zone_x, self.bar_y + self.bar_height + 5),
            3,
        )

    def _draw_timing_line(self, screen: pygame.Surface):
        """Draw the moving timing line."""
        line_x = self.bar_x + (self.timing_position * self.bar_width)
        pygame.draw.line(
            screen,
            (0, 0, 0),
            (line_x, self.bar_y),
            (line_x, self.bar_y + self.bar_height),
            4,
        )

    def _draw_instructions(self, screen: pygame.Surface):
        """Draw timing instructions."""
        font = pygame.font.Font(None, 20)
        instruction_text = "Hit WHITE line in green zone for perfect timing | Left/Right arrows to pedal"
        text_surface = font.render(instruction_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(
            center=(self.bar_x + self.bar_width // 2, self.bar_y + self.bar_height + 15)
        )
        screen.blit(text_surface, text_rect)
