"""
Main menu state for FixieDashBrooklyn.
"""

from typing import Any, Dict, List, Optional

import pygame

from ..services.api_client import APIClient
from ..ui.components import Button, InputBox, MessageBox


class MenuState:
    """Main menu state with sign in, leaderboard, and play functionality."""

    def __init__(self, screen: pygame.Surface, api_client: APIClient):
        self.screen = screen
        self.api_client = api_client
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # State management
        self.current_user: Optional[Dict[str, Any]] = None
        self.current_view = "main"  # main, signin, leaderboard
        self.next_state: Optional[str] = None

        # Fonts
        self.title_font = pygame.font.Font(None, 64)
        self.subtitle_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)

        # Initialize UI components
        self._init_main_menu()
        self._init_signin_menu()
        self._init_leaderboard_menu()

        # Check server connection
        self._check_server_connection()

    def _init_main_menu(self):
        """Initialize main menu UI components."""
        center_x = self.screen_width // 2
        button_width = 200
        button_height = 50
        button_spacing = 70
        start_y = 300

        self.main_buttons = {
            "signin": Button(
                center_x - button_width // 2,
                start_y,
                button_width,
                button_height,
                "Sign In",
                lambda: self._switch_view("signin"),
            ),
            "leaderboard": Button(
                center_x - button_width // 2,
                start_y + button_spacing,
                button_width,
                button_height,
                "Leaderboard",
                lambda: self._show_leaderboard(),
            ),
            "play": Button(
                center_x - button_width // 2,
                start_y + button_spacing * 2,
                button_width,
                button_height,
                "Play (Guest)",
                lambda: self._start_game_as_guest(),
            ),
            "quit": Button(
                center_x - button_width // 2,
                start_y + button_spacing * 3,
                button_width,
                button_height,
                "Quit",
                lambda: self._quit_game(),
            ),
        }

        # Message box for server status
        self.main_message = MessageBox(
            50,
            self.screen_height - 100,
            self.screen_width - 100,
            50,
            message_type="info",
        )

    def _init_signin_menu(self):
        """Initialize sign-in menu UI components."""
        center_x = self.screen_width // 2
        input_width = 300
        input_height = 40
        button_width = 120
        button_height = 40

        # Input fields
        self.username_input = InputBox(
            center_x - input_width // 2,
            250,
            input_width,
            input_height,
            "Enter username",
        )

        self.email_input = InputBox(
            center_x - input_width // 2,
            320,
            input_width,
            input_height,
            "Email (optional)",
        )

        # Buttons
        self.signin_buttons = {
            "signin": Button(
                center_x - button_width - 10,
                390,
                button_width,
                button_height,
                "Sign In",
                lambda: self._attempt_signin(),
            ),
            "back": Button(
                center_x + 10,
                390,
                button_width,
                button_height,
                "Back",
                lambda: self._switch_view("main"),
            ),
        }

        # Message box for signin feedback
        self.signin_message = MessageBox(
            center_x - 200,
            450,
            400,
            60,
            message_type="info",
        )

    def _init_leaderboard_menu(self):
        """Initialize leaderboard menu UI components."""
        # Back button
        self.leaderboard_buttons = {
            "back": Button(
                50,
                self.screen_height - 70,
                100,
                40,
                "Back",
                lambda: self._switch_view("main"),
            ),
            "refresh": Button(
                170,
                self.screen_height - 70,
                100,
                40,
                "Refresh",
                lambda: self._show_leaderboard(),
            ),
        }

        # Leaderboard data
        self.leaderboard_data = []
        self.leaderboard_loading = False

        # Message for leaderboard status
        self.leaderboard_message = MessageBox(
            50,
            50,
            self.screen_width - 100,
            50,
            message_type="info",
        )

    def _check_server_connection(self):
        """Check if the backend server is available."""
        if self.api_client.is_server_available():
            self.main_message.set_message(
                "✅ Connected to server", "success", clear_after=2
            )
            # Update play button text if signed in
            if self.current_user:
                self.main_buttons["play"].text = "Play Game"
        else:
            self.main_message.set_message(
                "⚠️ Server offline - Playing in offline mode", "warning", clear_after=3
            )
            # Disable online features
            self.main_buttons["signin"].text = "Sign In (Offline)"
            self.main_buttons["leaderboard"].text = "Leaderboard (Offline)"

    def _switch_view(self, view: str):
        """Switch between different menu views."""
        self.current_view = view

        # Clear messages when switching views
        if view == "signin":
            self.signin_message.clear()
        elif view == "leaderboard" and view != self.current_view:
            self._show_leaderboard()

    def _change_button_enablement(self, enable: bool, buttons: List[Button]):
        for button in buttons:
            button.disabled = not enable

    def _attempt_signin(self):
        """Attempt to sign in with the entered username."""
        username = self.username_input.text.strip()
        email = self.email_input.text.strip() or None

        if not username:
            self.signin_message.set_message(
                "Please enter a username", "error", clear_after=3
            )
            return

        if not self.api_client.is_server_available():
            self.signin_message.set_message("Cannot sign in - server offline", "error")
            return

        # Try to register/login
        # While logging in, disable the buttons
        self._change_button_enablement(False, self.signin_buttons.values())
        try:
            response = self.api_client.register_user(username, email)
        except Exception as e:
            self.signin_message.set_message(
                f"Sign in failed: {e}", "error", clear_after=3
            )
            self._change_button_enablement(True, self.signin_buttons.values())
            return

        if response.get("success"):
            self.current_user = response["user"]
            self.signin_message.set_message(f"Welcome, {username}!", "success")

            # Update main menu
            self.main_buttons["play"].text = "Play Game"
            self.main_buttons["signin"].text = f"Signed in as {username}"

            # Switch back to main menu after a delay
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # 1 second delay
        else:
            error_msg = response.get("error", "Unknown error")
            self.signin_message.set_message(f"Sign in failed: {error_msg}", "error")

    def _show_leaderboard(self):
        """Fetch and display the leaderboard."""
        self._switch_view("leaderboard")

        if not self.api_client.is_server_available():
            self.leaderboard_message.set_message(
                "Leaderboard unavailable - server offline", "error"
            )
            self.leaderboard_data = []
            return

        self.leaderboard_loading = True
        self.leaderboard_message.set_message(
            "Loading leaderboard...", "info", clear_after=3
        )

        response = self.api_client.get_leaderboard(10)

        if response.get("success"):
            entries = response.get("entries", [])
            if entries:
                self.leaderboard_data = []
                for i, entry in enumerate(entries, 1):
                    distance = entry.get("totalDistance", 0)
                    time = entry.get("completionTime", 0)
                    username = entry.get("username", "Unknown")

                    # Format the leaderboard entry with distance and time
                    rank_text = f"{i}. {username} - {distance:.0f}m in {time:.1f}s"
                    self.leaderboard_data.append(rank_text)
            else:
                self.leaderboard_data = ["No scores yet - be the first!"]
            self.leaderboard_message.clear()
        else:
            error_msg = response.get("error", "Unknown error")
            self.leaderboard_message.set_message(
                f"Failed to load leaderboard: {error_msg}", "error"
            )
            self.leaderboard_data = []

        self.leaderboard_loading = False

    def _start_game_as_guest(self):
        """Start the game as a guest player."""
        self.next_state = "game"

    def _quit_game(self):
        """Quit the application."""
        self.next_state = "quit"

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        # Handle custom timer event for signin delay
        if event.type == pygame.USEREVENT + 1:
            if self.current_view == "signin":
                self._switch_view("main")
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel timer

        # Handle events based on current view
        if self.current_view == "main":
            for button in self.main_buttons.values():
                button.handle_event(event)

        elif self.current_view == "signin":
            self.username_input.handle_event(event)
            self.email_input.handle_event(event)
            for button in self.signin_buttons.values():
                button.handle_event(event)

        elif self.current_view == "leaderboard":
            for button in self.leaderboard_buttons.values():
                button.handle_event(event)

        # Global key shortcuts
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.current_view != "main":
                    self._switch_view("main")
                else:
                    self._quit_game()

    def update(self, dt: float):
        """Update menu state."""
        if self.current_view == "signin":
            self.username_input.update(dt)
            self.email_input.update(dt)

    def draw(self):
        """Draw the current menu view."""
        # Clear screen with gradient background
        for y in range(self.screen_height):
            color_value = int(25 + (y / self.screen_height) * 40)
            color = (color_value, color_value, color_value + 20)
            pygame.draw.line(self.screen, color, (0, y), (self.screen_width, y))

        if self.current_view == "main":
            self._draw_main_menu()
        elif self.current_view == "signin":
            self._draw_signin_menu()
        elif self.current_view == "leaderboard":
            self._draw_leaderboard_menu()

    def _draw_main_menu(self):
        """Draw the main menu."""
        # Title
        title_text = self.title_font.render("FixieDashBrooklyn", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        subtitle_text = self.subtitle_font.render(
            "Race for the Last Empanada!", True, (200, 200, 200)
        )
        subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)

        # User status
        if self.current_user:
            status_text = self.text_font.render(
                f"Welcome, {self.current_user['username']}!", True, (100, 255, 100)
            )
            status_rect = status_text.get_rect(center=(self.screen_width // 2, 220))
            self.screen.blit(status_text, status_rect)

        # Buttons
        for button in self.main_buttons.values():
            button.draw(self.screen)

        # Server status message
        self.main_message.draw(self.screen)

    def _draw_signin_menu(self):
        """Draw the sign-in menu."""
        # Title
        title_text = self.subtitle_font.render("Sign In", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        self.screen.blit(title_text, title_rect)

        # Instructions
        instruction_text = self.text_font.render(
            "Enter your username to sign in or create an account", True, (200, 200, 200)
        )
        instruction_rect = instruction_text.get_rect(
            center=(self.screen_width // 2, 200)
        )
        self.screen.blit(instruction_text, instruction_rect)

        # Input fields
        self.username_input.draw(self.screen)
        self.email_input.draw(self.screen)

        # Buttons
        for button in self.signin_buttons.values():
            button.draw(self.screen)

        # Message
        self.signin_message.draw(self.screen)

    def _draw_leaderboard_menu(self):
        """Draw the leaderboard menu."""
        # Title
        title_text = self.subtitle_font.render("Leaderboard", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        self.screen.blit(title_text, title_rect)

        # Leaderboard content
        if self.leaderboard_loading:
            loading_text = self.text_font.render("Loading...", True, (200, 200, 200))
            loading_rect = loading_text.get_rect(center=(self.screen_width // 2, 250))
            self.screen.blit(loading_text, loading_rect)
        elif self.leaderboard_data:
            start_y = 150
            for i, entry in enumerate(self.leaderboard_data[:10]):  # Show top 10
                entry_text = self.text_font.render(entry, True, (255, 255, 255))
                self.screen.blit(entry_text, (100, start_y + i * 30))
        else:
            no_data_text = self.text_font.render(
                "No leaderboard data available", True, (200, 200, 200)
            )
            no_data_rect = no_data_text.get_rect(center=(self.screen_width // 2, 250))
            self.screen.blit(no_data_text, no_data_rect)

        # Buttons
        for button in self.leaderboard_buttons.values():
            button.draw(self.screen)

        # Message
        self.leaderboard_message.draw(self.screen)

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the currently signed-in user."""
        return self.current_user

    def get_next_state(self) -> Optional[str]:
        """Get the next state to transition to."""
        return self.next_state

    def reset_next_state(self):
        """Reset the next state."""
        self.next_state = None
