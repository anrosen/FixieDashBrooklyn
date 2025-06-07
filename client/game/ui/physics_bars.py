"""
UI components for displaying physics-related bars (pedal speed and stamina).
"""

from typing import Optional, Tuple

import pygame

from ..core.physics import Physics


class PedalSpeedBar:
    """
    Bar showing pedal timing with gradient and prediction line.

    The bar represents a range of 0ms to 2000ms.
    The green rectangle represents the current speed as a 50ms wide rectangle.
    The white line represents the time since the last pedal.
    There is a red/yellow gradient which gives 100ms of yellow in each direction from the green rectangle, and red the rest of the way.
    The green zone represents the sweet spot.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Colors
        self.bg_color = (0, 0, 0, 204)
        self.border_color = (255, 255, 255)
        self.green_color = (0, 255, 0)
        self.white_line_color = (255, 255, 255)

    def draw(self, screen: pygame.Surface, physics: Physics, current_time: int):
        """Draw the pedal speed bar."""
        # Background
        bg_rect = pygame.Rect(self.x - 5, self.y - 5, self.width + 10, self.height + 10)
        pygame.draw.rect(screen, self.bg_color, bg_rect)

        # Draw gradient background (red/yellow based on green zone)
        self._draw_timing_gradient(screen, physics)

        # Draw green rectangle based on expected pedal interval
        self._draw_sweet_spot_indicator(screen, physics)

        # Draw white timing line showing time since last pedal
        self._draw_timing_line(screen, physics, current_time)

        # Border
        border_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.border_color, border_rect, 2)

    def _draw_timing_gradient(self, screen: pygame.Surface, physics: Physics):
        """Draw red/yellow gradient background with green zone around expected interval."""
        # Get expected pedal interval (this determines green zone position)
        expected_interval = physics.get_curr_interval()

        # Bar represents 0ms to 3000ms (updated max range)
        max_time = 3000
        segment_width = max(1, self.width // 200)

        # Define zones
        green_zone_start = max(0, expected_interval - 150)
        green_zone_end = expected_interval + 150

        for i in range(0, self.width, segment_width):
            # Calculate time this segment represents
            time_at_position = (i / self.width) * max_time

            # Determine color based on position relative to expected interval
            if green_zone_start <= time_at_position <= green_zone_end:
                # Green zone (100ms wide total, centered on expected interval)
                r, g, b = 0, 255, 0
            elif time_at_position < green_zone_start:
                # Red-to-yellow gradient from 0 to expected_interval-150ms
                if green_zone_start > 0:
                    ratio = time_at_position / green_zone_start
                    r = 255
                    g = int(255 * ratio)  # 0 to 255 (red to yellow)
                    b = 0
                else:
                    r, g, b = 255, 0, 0  # Pure red if green zone starts at 0
            else:
                # Yellow-to-red gradient from expected_interval+150ms to max_time
                remaining_time = max_time - green_zone_end
                if remaining_time > 0:
                    ratio = (time_at_position - green_zone_end) / remaining_time
                    r = 255
                    g = int(255 * (1 - ratio))  # 255 to 0 (yellow to red)
                    b = 0
                else:
                    r, g, b = 255, 0, 0  # Pure red if no remaining time

            color = (r, g, b)
            segment_rect = pygame.Rect(
                self.x + i, self.y, segment_width + 1, self.height
            )
            pygame.draw.rect(screen, color, segment_rect)

    def _draw_sweet_spot_indicator(self, screen: pygame.Surface, physics: Physics):
        """Draw green rectangle at expected pedal interval position."""
        expected_interval = physics.get_curr_interval()
        max_time = 3000  # Bar represents 0ms to 3000ms (updated max range)

        # Calculate position on bar (0ms = left, 3000ms = right)
        position_ratio = expected_interval / max_time

        if position_ratio > 1.0:
            # Expected interval is beyond our bar range, don't draw
            return

        # Position the green rectangle (100ms wide: ±50ms from expected)
        rect_width = int((100 / max_time) * self.width)  # 100ms wide in pixels
        rect_x = self.x + (position_ratio * self.width) - (rect_width // 2)

        # Make sure rectangle doesn't go off edges
        rect_x = max(self.x, min(rect_x, self.x + self.width - rect_width))

        # Draw green rectangle
        green_rect = pygame.Rect(rect_x, self.y, rect_width, self.height)
        pygame.draw.rect(screen, self.green_color, green_rect)

        # Draw center line in the green rectangle
        center_x = rect_x + rect_width // 2
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (center_x, self.y),
            (center_x, self.y + self.height),
            2,
        )

    def _draw_timing_line(
        self, screen: pygame.Surface, physics: Physics, current_time: int
    ):
        """Draw white line showing time since last pedal stroke."""
        if physics.state.last_pedal_time == 0:
            return

        time_since_last = physics.get_time_since_last_pedal(current_time)
        max_time = (
            physics.max_pedal_interval - physics.min_pedal_interval
        )  # Bar represents 0ms to 3000ms (updated max range)

        # Calculate position: 0ms = left edge, 3000ms = right edge
        if time_since_last >= max_time:
            line_position = 1.0  # Far right
        else:
            line_position = time_since_last / max_time

        line_x = self.x + (line_position * self.width)

        # Draw white timing line
        pygame.draw.line(
            screen,
            self.white_line_color,
            (line_x, self.y),
            (line_x, self.y + self.height),
            3,
        )


class StaminaBar:
    """Bar showing current stamina and predicted stamina change."""

    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Colors
        self.bg_color = (40, 40, 40)  # Dark background
        self.border_color = (255, 255, 255)
        self.stamina_color = (255, 0, 0)  # Red stamina
        self.prediction_color = (0, 255, 0)  # Green prediction line

    def draw(self, screen: pygame.Surface, physics: Physics, current_time: int):
        """Draw the stamina bar."""
        # Background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, bg_rect)

        # Current stamina bar
        current_stamina = physics.get_stamina()
        stamina_ratio = current_stamina / physics.max_stamina
        stamina_width = int(self.width * stamina_ratio)

        if stamina_width > 0:
            stamina_rect = pygame.Rect(self.x, self.y, stamina_width, self.height)
            pygame.draw.rect(screen, self.stamina_color, stamina_rect)

        # Stamina prediction line
        predicted_change = physics.predict_stamina_change(current_time)
        if predicted_change != 0:
            self._draw_prediction_line(screen, physics, predicted_change)

        # Border
        pygame.draw.rect(screen, self.border_color, bg_rect, 2)

        # Stamina text
        self._draw_stamina_text(screen, current_stamina, predicted_change)

    def _draw_prediction_line(
        self, screen: pygame.Surface, physics: Physics, predicted_change: float
    ):
        """Draw the black prediction line showing stamina change."""
        current_stamina = physics.get_stamina()
        new_stamina = max(
            0, min(physics.max_stamina, current_stamina + predicted_change)
        )

        new_ratio = new_stamina / physics.max_stamina
        line_x = self.x + int(self.width * new_ratio)

        # Draw vertical line
        pygame.draw.line(
            screen,
            self.prediction_color,
            (line_x, self.y),
            (line_x, self.y + self.height),
            2,
        )

    def _draw_stamina_text(
        self, screen: pygame.Surface, current_stamina: float, predicted_change: float
    ):
        """Draw stamina value and prediction text."""
        font = pygame.font.Font(None, 20)

        # Current stamina
        stamina_text = f"Stamina: {int(current_stamina)}"
        text_surface = font.render(stamina_text, True, (255, 255, 255))
        screen.blit(text_surface, (self.x + 5, self.y - 25))

        # Prediction text (if significant change)
        if abs(predicted_change) > 0.1:
            change_sign = "+" if predicted_change > 0 else ""
            prediction_text = f"({change_sign}{predicted_change:.1f})"

            color = (0, 255, 0) if predicted_change > 0 else (255, 100, 100)
            prediction_surface = font.render(prediction_text, True, color)
            screen.blit(prediction_surface, (self.x + 120, self.y - 25))


class PhysicsBarsUI:
    """Combined UI component for both pedal speed and stamina bars."""

    def __init__(self, screen_width: int, margin: int = 50):
        self.screen_width = screen_width
        self.margin = margin

        bar_width = screen_width - (2 * margin)
        bar_height = 25

        # Pedal speed bar at the very top
        self.speed_bar = PedalSpeedBar(
            x=margin, y=10, width=bar_width, height=bar_height
        )

        # Stamina bar right below
        self.stamina_bar = StaminaBar(
            x=margin, y=45, width=bar_width, height=bar_height
        )

    def draw(self, screen: pygame.Surface, physics: Physics, current_time: int):
        """Draw both bars."""
        # Title for speed bar
        font = pygame.font.Font(None, 20)
        speed_title = font.render("Pedal Speed:", True, (255, 255, 255))
        screen.blit(speed_title, (self.margin, self.speed_bar.y - 20))

        self.speed_bar.draw(screen, physics, current_time)
        self.stamina_bar.draw(screen, physics, current_time)
