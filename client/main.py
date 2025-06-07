#!/usr/bin/env python3
"""
FixieDashBrooklyn - Python/Pygame Edition
A game where you race to get the last empanada on your fixie bike.

Usage: python main.py
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pygame

# Add the client directory to the path so we can import game modules
sys.path.insert(0, str(Path(__file__).parent))

from game import container
from game.services.api_client import APIClient
from game.services.config_service import ConfigService
from game.services.game_service import GameService
from game.states.game_state import GameState
from game.states.menu_state import MenuState


class GameApplication:
    """Main application class managing game states."""

    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Store reference to the container
        self.container = container

        # Services - register additional services before using them
        self._register_services()

        # Get configuration service
        self.config = self.container.get_singleton(ConfigService)

        # Window settings from config
        window_size = self.config.window_size
        self.WINDOW_WIDTH = window_size[0]
        self.WINDOW_HEIGHT = window_size[1]
        self.WINDOW_TITLE = "FixieDashBrooklyn - Race for the Last Empanada!"

        # Create display
        display_flags = 0
        if self.config.is_fullscreen:
            display_flags |= pygame.FULLSCREEN
        if self.config.get("window.vsync", True):
            display_flags |= pygame.SCALED

        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT), display_flags
        )
        pygame.display.set_caption(self.WINDOW_TITLE)

        # Game timing
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.running = True

        # State management
        self.current_state = "menu"
        self.states: Dict[str, Any] = {}

        # API client
        self.api_client = APIClient()

        # Current user (set by menu state)
        self.current_user: Optional[Dict[str, Any]] = None

        # Initialize states
        self._init_states()

    def _register_services(self):
        """Register additional services with the container."""
        # Register configuration service as singleton
        self.container.register_service(ConfigService, ConfigService)

        # Register game service factory (creates new instance each time)
        # We don't register as singleton since each game should be a new instance
        self.container.register_factory(
            GameService, lambda: None
        )  # Placeholder, will be created manually

        # You can register other services here as needed
        # Example: self.container.register_singleton(APIClient, APIClient())

    def _init_states(self):
        """Initialize all game states."""
        # Always start with menu
        self.states["menu"] = MenuState(self.screen, self.api_client)

        print("FixieDashBrooklyn initialized!")
        print("Navigate the menu with mouse and keyboard")
        print(
            f"Container services available: {len(self.container._singletons)} singletons, {len(self.container._factories)} factories"
        )
        print(f"Window size: {self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        print(f"Fullscreen: {self.config.is_fullscreen}")

    def _switch_state(self, new_state: str):
        """Switch to a new game state."""
        if new_state == "quit":
            self.running = False
            return

        # Get current user from menu if switching to game
        if new_state == "game":
            if "menu" in self.states:
                self.current_user = self.states["menu"].get_current_user()
                self.states["game"] = GameState(
                    self.screen, self.api_client, self.current_user
                )
                print("🎮 Created new game state!")

        elif new_state == "menu":
            # Preserve current user when returning to menu
            if "menu" in self.states and self.current_user:
                pass  # Menu state maintains its own user state

            # Clean up game state if returning from game
            if "game" in self.states:
                del self.states["game"]
                print("🧹 Cleaned up game state")

        self.current_state = new_state
        print(f"Switched to state: {new_state}")

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Global key shortcuts
                if event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                elif event.key == pygame.K_F12:
                    self._toggle_fps_display()
                else:
                    # Pass other events to current state
                    if self.current_state in self.states:
                        self.states[self.current_state].handle_event(event)
            else:
                # Pass events to current state
                if self.current_state in self.states:
                    self.states[self.current_state].handle_event(event)

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        current_fullscreen = self.config.is_fullscreen
        self.config.set("window.fullscreen", not current_fullscreen)

        # Recreate display with new settings
        display_flags = 0
        if self.config.is_fullscreen:
            display_flags |= pygame.FULLSCREEN
        if self.config.get("window.vsync", True):
            display_flags |= pygame.SCALED

        self.screen = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT), display_flags
        )
        print(f"Fullscreen: {'ON' if self.config.is_fullscreen else 'OFF'}")

    def _toggle_fps_display(self):
        """Toggle FPS display."""
        current_fps = self.config.get("game.show_fps", False)
        self.config.set("game.show_fps", not current_fps)
        print(f"FPS Display: {'ON' if self.config.get('game.show_fps') else 'OFF'}")

    def update(self, dt: float):
        """Update the current state."""
        if self.current_state in self.states:
            current_state_obj = self.states[self.current_state]
            current_state_obj.update(dt)

            # Check for state transitions
            next_state = current_state_obj.get_next_state()
            if next_state:
                current_state_obj.reset_next_state()
                self._switch_state(next_state)

    def draw(self):
        """Draw the current state."""
        # Clear screen
        self.screen.fill((0, 0, 0))

        # Draw current state
        if self.current_state in self.states:
            self.states[self.current_state].draw()
        else:
            # Fallback: draw error message
            font = pygame.font.Font(None, 48)
            error_text = font.render(
                f"Unknown state: {self.current_state}", True, (255, 0, 0)
            )
            text_rect = error_text.get_rect(
                center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2)
            )
            self.screen.blit(error_text, text_rect)

        # Draw FPS if enabled
        if self.config.get("game.show_fps", False):
            fps = self.clock.get_fps()
            font = pygame.font.Font(None, 24)
            fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 0))
            self.screen.blit(fps_text, (10, 10))

        # Update display
        pygame.display.flip()

    def run(self):
        """Main application loop."""
        print("Starting FixieDashBrooklyn!")
        print("🚴‍♂️ Welcome to the cycling game!")
        print("📱 Use the menu to sign in and play")
        print("🔧 Press F11 for fullscreen, F12 to toggle FPS display")

        # Check server status on startup
        if self.api_client.is_server_available():
            print("✅ Connected to backend server")
        else:
            print("⚠️  Backend server offline - running in offline mode")

        try:
            while self.running:
                # Calculate delta time
                dt = self.clock.tick(self.FPS)

                # Handle events
                self.handle_events()

                # Update current state
                self.update(dt)

                # Draw everything
                self.draw()
        finally:
            # Ensure cleanup happens
            self.cleanup()

        print("Thanks for playing FixieDashBrooklyn!")

    def cleanup(self):
        """Clean up resources and shutdown services."""
        print("Cleaning up application resources...")

        # Save configuration
        if hasattr(self, "config"):
            self.config.save_config()

        # Clear game states
        self.states.clear()

        # Shutdown container services
        self.container.shutdown()

        # Cleanup pygame
        pygame.quit()


def main():
    """Main entry point for the game."""
    app = None
    try:
        app = GameApplication()
        app.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        # Ensure cleanup happens even if app creation failed
        if app:
            app.cleanup()
        else:
            # If app wasn't created, at least shutdown pygame
            pygame.quit()
            # And the container if it was initialized
            try:
                container.shutdown()
            except:
                pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
