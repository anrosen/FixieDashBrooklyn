"""
New modular game state using the GameService architecture.
"""

from typing import Any, Dict, Optional

import pygame

from ..services.api_client import APIClient
from ..services.game_service import GameService


class GameState:
    """Simplified game state that delegates to GameService."""

    def __init__(
        self,
        screen: pygame.Surface,
        api_client: APIClient,
        user: Optional[Dict[str, Any]],
    ):
        self.screen = screen
        self.api_client = api_client
        self.user = user

        # State management
        self.next_state: Optional[str] = None

        # Initialize game service
        self.game_service = GameService(screen, api_client, user)

        print(f"🚴‍♂️ Starting new game for {user['username'] if user else 'guest'}!")
        print("🏁 Use LEFT and RIGHT arrows to pedal")
        print("⏸️  Press ESC to pause, M for menu")

    def handle_event(self, event: pygame.event.Event):
        """Handle game input events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.game_service.handle_pedal_input("left")
            elif event.key == pygame.K_RIGHT:
                self.game_service.handle_pedal_input("right")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.game_service.handle_enter_key()
            elif event.key == pygame.K_ESCAPE:
                self.game_service.toggle_pause()
            elif event.key == pygame.K_r and self.game_service.game_over:
                self.game_service.restart()
            elif event.key == pygame.K_m:
                self.next_state = "menu"

    def update(self, dt: float):
        """Update the game."""
        self.game_service.update(dt)

    def draw(self):
        """Draw the game."""
        self.game_service.draw()

    def get_next_state(self) -> Optional[str]:
        """Get the next state to transition to."""
        return self.next_state

    def reset_next_state(self):
        """Reset the next state."""
        self.next_state = None
