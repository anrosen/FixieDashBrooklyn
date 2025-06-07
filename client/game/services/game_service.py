"""
Game service that coordinates all game systems.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

import pygame

from ..core.cyclist import Cyclist
from ..core.physics import Physics
from ..ui.physics_bars import PhysicsBarsUI
from .api_client import APIClient
from .background_service import BackgroundService


@dataclass
class GameStats:
    """Track game statistics."""

    max_speed_reached: float = 0.0
    total_pedals: int = 0
    successful_pedals: int = 0
    start_time: int = 0

    # Level-specific tracking
    level_start_times: Dict[int, int] = None
    level_completion_times: Dict[int, float] = None
    level_end_times: Dict[int, int] = (
        None  # Track when levels ended (success or failure)
    )
    level_started: Dict[int, bool] = None  # Track if level timer has started
    completed_levels: set = None  # Track which levels are completed

    def __post_init__(self):
        if self.level_start_times is None:
            self.level_start_times = {}
        if self.level_completion_times is None:
            self.level_completion_times = {}
        if self.level_end_times is None:
            self.level_end_times = {}
        if self.level_started is None:
            self.level_started = {}
        if self.completed_levels is None:
            self.completed_levels = set()

    @property
    def completion_time(self) -> float:
        """Get completion time in seconds."""
        return (pygame.time.get_ticks() - self.start_time) / 1000.0

    @property
    def total_completion_time(self) -> float:
        """Get total time across all completed levels."""
        return sum(self.level_completion_times.values())

    @property
    def success_ratio(self) -> float:
        """Get percentage of successful pedals."""
        if self.total_pedals == 0:
            return 0.0
        return (self.successful_pedals / self.total_pedals) * 100

    def prepare_level(self, level: int):
        """Prepare a level (but don't start timer yet)."""
        self.level_started[level] = False

    def start_level_timer(self, level: int):
        """Start timing for a level when first pedal occurs."""
        if not self.level_started.get(level, False):
            self.level_start_times[level] = pygame.time.get_ticks()
            self.level_started[level] = True

    def end_level(self, level: int):
        """End a level (for game over scenarios)."""
        if level in self.level_start_times and self.level_started.get(level, False):
            self.level_end_times[level] = pygame.time.get_ticks()

    def complete_level(self, level: int):
        """Complete timing for a level."""
        if level in self.level_start_times and self.level_started.get(level, False):
            completion_time = (
                pygame.time.get_ticks() - self.level_start_times[level]
            ) / 1000.0
            self.level_completion_times[level] = completion_time
            self.completed_levels.add(level)
            self.level_end_times[level] = pygame.time.get_ticks()
            return completion_time
        return 0.0

    def get_current_level_time(self, level: int) -> float:
        """Get current elapsed time for a level."""
        if level in self.level_start_times and self.level_started.get(level, False):
            # If level has ended (game over), use the end time
            if level in self.level_end_times:
                return (
                    self.level_end_times[level] - self.level_start_times[level]
                ) / 1000.0
            # Otherwise use current time
            return (pygame.time.get_ticks() - self.level_start_times[level]) / 1000.0
        return 0.0


class GameService:
    """Main game service that coordinates all game systems."""

    # Level distance goals in meters
    LEVEL_DISTANCES = {1: 1000.0, 2: 1500.0, 3: 2000.0, 4: 2500.0}

    def __init__(
        self,
        screen: pygame.Surface,
        api_client: APIClient,
        user: Optional[Dict[str, Any]],
        level: int = 1,
    ):
        self.screen = screen
        self.api_client = api_client
        self.user = user
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Game state
        self.game_over = False
        self.paused = False
        self.session_id: Optional[str] = None
        self.current_level = level
        self.level_complete = False
        self.all_levels_complete = False
        self.level_start_distance = 0.0
        self.game_over_reason = ""  # Track why the game ended

        # Load celebratory image
        self.celebratory_image = self._load_celebratory_image()

        # Initialize background service first
        self.background_service = BackgroundService(
            self.screen_width, self.screen_height
        )
        self.background_service.set_level(level)

        # Initialize game systems
        cyclist_start_pos = self.background_service.get_cyclist_start_position()
        self.cyclist = Cyclist(x=cyclist_start_pos[0], y=cyclist_start_pos[1])
        self.physics = Physics(max_speed=25.0)
        self.stats = GameStats(start_time=pygame.time.get_ticks())

        # Prepare timing for the first level (but don't start timer yet)
        self.stats.prepare_level(level)

        # Initialize UI components
        self.physics_bars = PhysicsBarsUI(self.screen_width)

        # Cyclist movement for level completion
        self.cyclist_exit_speed = 100.0  # pixels per second when riding off screen

        # Feedback system
        self.last_pedal_message = ""
        self.message_timer = 0.0
        self.message_duration = 1000  # ms

        # Start game session
        self._start_session()

    def _load_celebratory_image(self) -> Optional[pygame.Surface]:
        """Load the celebratory image for completing all levels."""
        try:
            image = pygame.image.load("assets/get_that_empanada.png").convert_alpha()
            # Scale to fit screen while maintaining aspect ratio
            img_width, img_height = image.get_size()
            scale_factor = min(
                self.screen_width * 0.8 / img_width,
                self.screen_height * 0.8 / img_height,
            )
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            return pygame.transform.scale(image, (new_width, new_height))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load celebratory image: {e}")
            return None

    def get_level_target_distance(self, level: int) -> float:
        """Get the target distance for a level."""
        return self.LEVEL_DISTANCES.get(level, 1000.0)

    def get_level_progress(self) -> float:
        """Get progress towards current level completion (0.0 to 1.0)."""
        current_distance = self.physics.get_distance_meters()
        target_distance = self.get_level_target_distance(self.current_level)
        return min(current_distance / target_distance, 1.0)

    def get_total_distance_traveled(self) -> float:
        """Get total distance traveled across all levels."""
        total = 0.0

        # Add exact distances for completed levels
        for level in self.stats.completed_levels:
            total += self.get_level_target_distance(level)

        # Add current level progress (only if not complete)
        if not self.level_complete:
            total += self.physics.get_distance_meters()
        elif self.current_level not in self.stats.completed_levels:
            # Level just completed but not yet recorded, add the exact target distance
            total += self.get_level_target_distance(self.current_level)

        return total

    def get_total_time(self) -> float:
        """Get total time across all levels."""
        total_time = self.stats.total_completion_time

        # Only add current level time if level is not complete (timer still running)
        if (
            not self.level_complete
            and self.current_level in self.stats.level_start_times
        ):
            current_level_time = self.stats.get_current_level_time(self.current_level)
            total_time += current_level_time

        return total_time

    def _start_session(self):
        """Start a game session with the backend."""
        if self.api_client.is_server_available():
            if self.user:
                response = self.api_client.start_game_session(self.user["id"])
                if response.get("success"):
                    self.session_id = response["sessionId"]
                print(f"Started game session: {self.session_id}")
            else:
                print("Started game without user")

    def handle_pedal_input(self, side: str) -> bool:
        """Handle pedal input from the player."""
        if self.game_over or self.paused or self.level_complete:
            return False

        # Start level timer on first pedal
        self.stats.start_level_timer(self.current_level)

        # Start riding transition if we're on the start screen
        if self.background_service.is_on_start_screen():
            self.background_service.start_riding()

        current_time = pygame.time.get_ticks()

        # Update statistics
        self.stats.total_pedals += 1

        # Handle pedal with simplified physics
        success = self.physics.handle_pedal(side, current_time)

        if success:
            self.stats.successful_pedals += 1
            self.cyclist.pedal(side)
            self.last_pedal_message = "Good!"

            # Update max speed stat
            if self.physics.state.speed > self.stats.max_speed_reached:
                self.stats.max_speed_reached = self.physics.state.speed
        else:
            # Failed pedal attempt
            if self.physics.state.last_pedal_side == side:
                self.last_pedal_message = "Alternate left and right!"
            else:
                self.last_pedal_message = "Too fast or too slow!"

        # Reset message timer
        self.message_timer = 0.0

        return success

    def set_level(self, level: int):
        """Set the current level."""
        self.current_level = level
        self.background_service.set_level(level)
        self.level_complete = False

        # Reset cyclist position
        cyclist_start_pos = self.background_service.get_cyclist_start_position()
        self.cyclist.x = cyclist_start_pos[0]
        self.cyclist.y = cyclist_start_pos[1]

        # Reset physics for new level
        self.physics.reset()

        # Reset level start distance since physics is reset
        self.level_start_distance = 0.0

        # Prepare timing for the new level (but don't start timer yet)
        self.stats.prepare_level(level)

    def _complete_level(self):
        """Handle level completion."""
        if not self.level_complete:
            self.level_complete = True
            # Complete current level timing immediately when distance goal is reached
            completion_time = self.stats.complete_level(self.current_level)
            print(
                f"Level {self.current_level} distance goal reached! Time: {completion_time:.1f} seconds"
            )

    def _check_level_completion(self):
        """Check if current level is complete based on distance."""
        if self.level_complete or self.all_levels_complete:
            return

        current_distance = self.physics.get_distance_meters()
        target_distance = self.get_level_target_distance(self.current_level)

        if current_distance >= target_distance:
            self._complete_level()

    def toggle_pause(self):
        """Toggle game pause state."""
        self.paused = not self.paused

    def _end_game(self):
        """End the current game."""
        self.game_over = True

        # Stop the level timer immediately when game ends
        if (
            not self.level_complete
            and self.current_level in self.stats.level_start_times
        ):
            # Record the end time for this level
            self.stats.end_level(self.current_level)

        # End session with backend
        if self.session_id and self.api_client.is_server_available():
            self.api_client.end_game_session(
                self.session_id,
                self.stats.max_speed_reached,
                self.get_total_distance_traveled(),
                self.get_total_time(),
            )

    def restart(self):
        """Restart the game."""
        self.game_over = False
        self.paused = False
        self.session_id = None
        self.level_complete = False
        self.all_levels_complete = False
        self.level_start_distance = 0.0
        self.game_over_reason = ""

        # Reset to level 1
        self.current_level = 1
        self.background_service.set_level(1)

        # Reset all systems
        cyclist_start_pos = self.background_service.get_cyclist_start_position()
        self.cyclist = Cyclist(x=cyclist_start_pos[0], y=cyclist_start_pos[1])
        self.physics.reset()
        self.stats = GameStats(start_time=pygame.time.get_ticks())

        # Prepare timing for level 1 (but don't start timer yet)
        self.stats.prepare_level(1)

        # Reinitialize UI components
        self.physics_bars = PhysicsBarsUI(self.screen_width)

        self.last_pedal_message = ""
        self.message_timer = 0.0

        # Start new session
        self._start_session()

    def _check_game_over_conditions(self):
        """Check for game over conditions."""
        if self.game_over or self.level_complete or self.all_levels_complete:
            return

        current_time = pygame.time.get_ticks()

        # Check if player hasn't pedaled for too long (check this FIRST)
        if self.physics.state.last_pedal_time > 0:
            time_since_last_pedal = current_time - self.physics.state.last_pedal_time
            if time_since_last_pedal > self.physics.max_pedal_interval:
                self.game_over_reason = "You stopped pedaling for too long!"
                self._end_game()
                return

        # Check if stamina is depleted (only if still pedaling)
        if self.physics.get_stamina() <= 0:
            self.game_over_reason = "You ran out of stamina!"
            self._end_game()
            return

    def update(self, dt: float):
        """Update all game systems."""
        if self.game_over or self.paused:
            return

        current_time = pygame.time.get_ticks()

        # Only update physics if level is not complete
        if not self.level_complete:
            # Update physics
            self.physics.update(dt, current_time)

            # Check for game over conditions
            self._check_game_over_conditions()

            # If game over was triggered, stop here
            if self.game_over:
                return

            # Update background service with cyclist speed
            self.background_service.update(dt, self.physics.state.speed)

            # Check for level completion
            self._check_level_completion()
        else:
            # Level is complete - stop physics but keep background moving slowly for visual effect
            self.background_service.update(dt, 2.0)  # Slow background movement

        # Update cyclist position based on game phase
        if self.level_complete and not self.all_levels_complete:
            # Keep cyclist in place when level is complete, waiting for Enter
            if not self.background_service.is_on_start_screen():
                fixed_pos = self.background_service.get_cyclist_fixed_position()
                self.cyclist.x = fixed_pos[0]
                self.cyclist.y = fixed_pos[1]
        elif self.all_levels_complete:
            # Move cyclist to the right off screen after all levels complete
            self.cyclist.x += self.cyclist_exit_speed * (dt / 1000.0)

            # End game when cyclist is off screen
            if self.cyclist.x > self.screen_width + 100:
                self._end_game()
        else:
            # Keep cyclist at fixed position during normal gameplay
            if not self.background_service.is_on_start_screen():
                fixed_pos = self.background_service.get_cyclist_fixed_position()
                self.cyclist.x = fixed_pos[0]
                self.cyclist.y = fixed_pos[1]

        # Update cyclist animations
        self.cyclist.update(dt)

        # Update message timer
        self.message_timer += dt

    def draw(self):
        """Draw all game elements."""
        # Clear screen
        self.screen.fill((0, 0, 0))

        # Show celebratory image if all levels are complete
        if self.all_levels_complete and self.celebratory_image:
            self._draw_celebratory_screen()
            return

        # Draw background using background service
        self.background_service.draw(self.screen)

        # Draw game systems - only the cyclist now
        self.cyclist.draw(self.screen)

        # Draw physics bars at the top (unless level is complete)
        if not self.level_complete:
            current_time = pygame.time.get_ticks()
            self.physics_bars.draw(self.screen, self.physics, current_time)

        # Draw minimal UI (just overlays)
        self._draw_minimal_ui()

        # Draw level completion summary if level is complete
        if self.level_complete and not self.all_levels_complete:
            self._draw_level_completion_summary()

        # Draw overlays
        if self.paused:
            self._draw_pause_overlay()
        elif self.game_over:
            self._draw_game_over_overlay()

    def _draw_celebratory_screen(self):
        """Draw the celebratory completion screen."""
        # Dark background
        self.screen.fill((0, 0, 0))

        # Draw celebratory image
        if self.celebratory_image:
            img_rect = self.celebratory_image.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 50)
            )
            self.screen.blit(self.celebratory_image, img_rect)

        # Completion text
        font_medium = pygame.font.Font(None, 32)

        # Stats
        total_distance = self.get_total_distance_traveled()
        total_time = self.get_total_time()

        stats_y = self.screen_height - 200
        stats = [
            f"Total Distance: {total_distance:.1f}m",
            f"Total Time: {total_time:.1f}s",
            f"Max Speed: {self.stats.max_speed_reached:.1f} mph",
        ]

        for i, stat in enumerate(stats):
            stat_surface = font_medium.render(stat, True, (255, 255, 255))
            stat_rect = stat_surface.get_rect(
                center=(self.screen_width // 2, stats_y + i * 35)
            )
            self.screen.blit(stat_surface, stat_rect)

        # Instructions
        instruction_text = font_medium.render(
            "Press R to restart or M for menu", True, (200, 200, 200)
        )
        instruction_rect = instruction_text.get_rect(
            center=(self.screen_width // 2, self.screen_height - 30)
        )
        self.screen.blit(instruction_text, instruction_rect)

    def _draw_level_completion_summary(self):
        """Draw the level completion summary popup."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Summary box dimensions
        box_width = 400
        box_height = 250
        box_x = (self.screen_width - box_width) // 2
        box_y = (self.screen_height - box_height) // 2

        # Draw summary box
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, (40, 40, 40), box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 3)

        # Fonts
        font_large = pygame.font.Font(None, 32)
        font_medium = pygame.font.Font(None, 24)

        # Title
        title_text = f"Level {self.current_level} Complete!"
        title_surface = font_large.render(title_text, True, (0, 255, 0))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, box_y + 40))
        self.screen.blit(title_surface, title_rect)

        # Stats
        level_time = self.stats.level_completion_times.get(self.current_level, 0.0)
        total_distance = self.get_total_distance_traveled()

        stats_y = box_y + 80
        stats = [
            f"Level Time: {level_time:.1f}s",
            f"Total Distance: {total_distance:.1f}m",
            f"Level Distance: {self.get_level_target_distance(self.current_level):.0f}m",
        ]

        for i, stat in enumerate(stats):
            stat_surface = font_medium.render(stat, True, (255, 255, 255))
            stat_rect = stat_surface.get_rect(
                center=(self.screen_width // 2, stats_y + i * 30)
            )
            self.screen.blit(stat_surface, stat_rect)

        # Continue prompt
        if self.current_level < 4:
            prompt_text = f"Press ENTER to continue to Level {self.current_level + 1}"
        else:
            prompt_text = "Press ENTER to finish the game!"

        prompt_surface = font_medium.render(prompt_text, True, (255, 215, 0))
        prompt_rect = prompt_surface.get_rect(
            center=(self.screen_width // 2, box_y + box_height - 40)
        )
        self.screen.blit(prompt_surface, prompt_rect)

    def _draw_minimal_ui(self):
        """Draw minimal UI elements - just feedback messages."""
        font_medium = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)

        # Status message (pedal feedback)
        if self.message_timer < self.message_duration and self.last_pedal_message:
            # Fade out message
            alpha = int(255 * (1.0 - self.message_timer / self.message_duration))
            message_color = (255, 255, 255, alpha)

            message_surface = font_medium.render(
                self.last_pedal_message, True, message_color[:3]
            )
            message_rect = message_surface.get_rect(
                center=(self.screen_width // 2, 150)
            )
            self.screen.blit(message_surface, message_rect)

        # Current level time (top center)
        if not self.level_complete and not self.game_over:
            current_time = self.stats.get_current_level_time(self.current_level)
            time_text = f"{current_time:.1f}s"
            time_surface = font_medium.render(time_text, True, (255, 255, 255))

            # Create a box around the timer
            box_padding = 10
            box_width = time_surface.get_width() + (box_padding * 2)
            box_height = time_surface.get_height() + (box_padding * 2)
            box_x = (self.screen_width - box_width) // 2
            box_y = 100

            # Draw timer box
            box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
            pygame.draw.rect(self.screen, (40, 40, 40), box_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)

            # Draw timer text centered in box
            text_x = box_x + box_padding
            text_y = box_y + box_padding
            self.screen.blit(time_surface, (text_x, text_y))

        # Distance display (bottom left)
        distance_meters = self.physics.get_distance_meters()
        distance_text = f"Distance: {distance_meters:.1f}m"
        distance_surface = font_medium.render(distance_text, True, (255, 255, 255))
        self.screen.blit(distance_surface, (20, self.screen_height - 50))

        # Speed display (bottom right)
        speed_mph = self.physics.get_speed_mph()
        speed_text = f"Speed: {speed_mph:.1f} mph"
        speed_surface = font_medium.render(speed_text, True, (255, 255, 255))
        speed_rect = speed_surface.get_rect()
        speed_rect.right = self.screen_width - 20
        speed_rect.y = self.screen_height - 50
        self.screen.blit(speed_surface, speed_rect)

        # Simple instructions at bottom (moved up slightly to avoid overlap)
        if not self.level_complete:
            instruction_text = (
                "Use LEFT & RIGHT arrows to pedal | ESC to pause | M for menu"
            )
            instruction_surface = font_small.render(
                instruction_text, True, (200, 200, 200)
            )
            instruction_rect = instruction_surface.get_rect(
                center=(self.screen_width // 2, self.screen_height - 20)
            )
            self.screen.blit(instruction_surface, instruction_rect)

    def _draw_pause_overlay(self):
        """Draw pause overlay."""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 64)
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2)
        )
        self.screen.blit(pause_text, pause_rect)

        instruction_font = pygame.font.Font(None, 32)
        instruction_text = instruction_font.render(
            "Press ESC to resume", True, (200, 200, 200)
        )
        instruction_rect = instruction_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 + 60)
        )
        self.screen.blit(instruction_text, instruction_rect)

    def _draw_game_over_overlay(self):
        """Draw game over overlay."""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(192)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # Game Over title
        font = pygame.font.Font(None, 64)
        title_text = font.render("GAME OVER", True, (255, 100, 100))
        title_rect = title_text.get_rect(
            center=(self.screen_width // 2, self.screen_height // 2 - 150)
        )
        self.screen.blit(title_text, title_rect)

        # Game over reason
        if self.game_over_reason:
            reason_font = pygame.font.Font(None, 36)
            reason_text = reason_font.render(
                self.game_over_reason, True, (255, 255, 100)
            )
            reason_rect = reason_text.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 100)
            )
            self.screen.blit(reason_text, reason_rect)

        # Final stats - simplified
        stats_font = pygame.font.Font(None, 32)

        # Get the final level time and total stats
        final_level_time = self.stats.get_current_level_time(self.current_level)
        total_distance = self.get_total_distance_traveled()
        total_time = self.get_total_time()

        final_stats = [
            f"Level: {self.current_level}",
            f"Level Time: {final_level_time:.1f}s",
            f"Max Speed: {self.stats.max_speed_reached:.1f} mph",
            f"Total Distance: {total_distance:.1f}m",
            f"Total Time: {total_time:.1f}s",
        ]

        for i, stat in enumerate(final_stats):
            text_surface = stats_font.render(stat, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 - 20 + i * 35)
            )
            self.screen.blit(text_surface, text_rect)

        # Instructions
        instruction_font = pygame.font.Font(None, 28)
        instructions = ["Press R to restart", "Press M for menu"]

        for i, instruction in enumerate(instructions):
            text_surface = instruction_font.render(instruction, True, (200, 200, 200))
            text_rect = text_surface.get_rect(
                center=(self.screen_width // 2, self.screen_height // 2 + 180 + i * 30)
            )
            self.screen.blit(text_surface, text_rect)

    def handle_enter_key(self):
        """Handle Enter key press for level advancement."""
        if self.level_complete and not self.all_levels_complete:
            if self.current_level < 4:
                # Move to next level
                next_level = self.current_level + 1
                self.set_level(next_level)
                print(f"Starting level {next_level}")
            else:
                # All levels complete!
                self.all_levels_complete = True
                print("All levels completed! You got the empanada!")
