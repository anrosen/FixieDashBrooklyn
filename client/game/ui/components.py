"""
Reusable UI components for the FixieDashBrooklyn game.
"""

import asyncio
from typing import Callable, List, Optional, Tuple

import pygame

from game import container


class Button:
    """Reusable button component."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Callable = None,
        font_size: int = 24,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.is_pressed = False

        # Colors
        self.bg_color = (70, 130, 180)  # Steel blue
        self.hover_color = (100, 149, 237)  # Cornflower blue
        self.press_color = (65, 105, 225)  # Royal blue
        self.text_color = (255, 255, 255)  # White
        self.border_color = (255, 255, 255)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Returns True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.rect.collidepoint(event.pos):
                self.is_pressed = False
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
        return False

    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        # Choose color based on state
        if self.is_pressed:
            color = self.press_color
        elif self.is_hovered:
            color = self.hover_color
        else:
            color = self.bg_color

        # Draw button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class InputBox:
    """Text input box component."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        placeholder: str = "",
        font_size: int = 24,
        max_length: int = 20,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.text = ""
        self.max_length = max_length
        self.font = pygame.font.Font(None, font_size)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0

        # Colors
        self.active_color = (100, 149, 237)
        self.inactive_color = (70, 130, 180)
        self.text_color = (255, 255, 255)
        self.placeholder_color = (200, 200, 200)

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < self.max_length:
                    self.text += event.unicode

    def update(self, dt: float):
        """Update cursor blinking."""
        self.cursor_timer += dt
        if self.cursor_timer >= 500:  # Blink every 500ms
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, screen: pygame.Surface):
        """Draw the input box."""
        # Draw background
        color = self.active_color if self.active else self.inactive_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        # Draw text or placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = self.text_color if self.text else self.placeholder_color

        text_surface = self.font.render(display_text, True, text_color)
        text_rect = pygame.Rect(
            self.rect.x + 10, self.rect.y, self.rect.width - 20, self.rect.height
        )
        screen.blit(
            text_surface,
            (text_rect.x, text_rect.centery - text_surface.get_height() // 2),
        )

        # Draw cursor if active
        if self.active and self.cursor_visible and self.text:
            cursor_x = text_rect.x + text_surface.get_width() + 2
            cursor_y1 = text_rect.centery - 10
            cursor_y2 = text_rect.centery + 10
            pygame.draw.line(
                screen, self.text_color, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 1
            )


class MessageBox:
    """Message display component."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        message: str = "",
        font_size: int = 20,
        message_type: str = "info",
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.message = message
        self.font = pygame.font.Font(None, font_size)
        self.message_type = message_type
        self.visible = bool(message)

        # Colors based on message type
        if message_type == "error":
            self.bg_color = (220, 20, 60)  # Crimson
            self.text_color = (255, 255, 255)
        elif message_type == "success":
            self.bg_color = (34, 139, 34)  # Forest green
            self.text_color = (255, 255, 255)
        elif message_type == "warning":
            self.bg_color = (255, 140, 0)  # Dark orange
            self.text_color = (255, 255, 255)
        else:  # info
            self.bg_color = (70, 130, 180)  # Steel blue
            self.text_color = (255, 255, 255)

    def set_message(
        self,
        message: str,
        message_type: str = "info",
        clear_after: int | None = None,
    ):
        """Set a new message."""
        self.message = message
        self.message_type = message_type
        self.visible = bool(message)

        # Update colors
        if message_type == "error":
            self.bg_color = (220, 20, 60)
        elif message_type == "success":
            self.bg_color = (34, 139, 34)
        elif message_type == "warning":
            self.bg_color = (255, 140, 0)
        else:
            self.bg_color = (70, 130, 180)

        if clear_after:
            # Get the background event service from the container
            bg_service = container.background_event_service
            bg_service.add_task(self.clear_after(clear_after))

    async def clear_after(self, seconds: int):
        """Clear the message after a delay."""
        await asyncio.sleep(seconds)
        self.clear()

    def clear(self):
        """Clear the message."""
        self.message = ""
        self.visible = False

    def draw(self, screen: pygame.Surface):
        """Draw the message box."""
        if not self.visible or not self.message:
            return

        # Draw background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        # Wrap text if needed
        words = self.message.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = self.font.size(test_line)[0]

            if text_width < self.rect.width - 20:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Draw text lines
        line_height = self.font.get_height()
        start_y = self.rect.y + (self.rect.height - len(lines) * line_height) // 2

        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, self.text_color)
            text_x = self.rect.x + (self.rect.width - text_surface.get_width()) // 2
            text_y = start_y + i * line_height
            screen.blit(text_surface, (text_x, text_y))


class ScrollableList:
    """Scrollable list component for displaying leaderboards."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        item_height: int = 40,
        font_size: int = 20,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.item_height = item_height
        self.font = pygame.font.Font(None, font_size)
        self.items: List[str] = []
        self.scroll_offset = 0
        self.max_visible_items = height // item_height

        # Colors
        self.bg_color = (30, 30, 30)
        self.item_color = (50, 50, 50)
        self.alt_item_color = (60, 60, 60)
        self.text_color = (255, 255, 255)
        self.border_color = (255, 255, 255)

    def set_items(self, items: List[str]):
        """Set the items to display."""
        self.items = items
        self.scroll_offset = 0

    def handle_event(self, event: pygame.event.Event):
        """Handle scroll events."""
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(
            pygame.mouse.get_pos()
        ):
            self.scroll_offset -= event.y
            max_scroll = max(0, len(self.items) - self.max_visible_items)
            self.scroll_offset = max(0, min(max_scroll, self.scroll_offset))

    def draw(self, screen: pygame.Surface):
        """Draw the scrollable list."""
        # Draw background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        # Draw items
        visible_items = self.items[
            self.scroll_offset : self.scroll_offset + self.max_visible_items
        ]

        for i, item in enumerate(visible_items):
            item_y = self.rect.y + i * self.item_height
            item_rect = pygame.Rect(
                self.rect.x, item_y, self.rect.width, self.item_height
            )

            # Alternate colors
            color = self.alt_item_color if i % 2 == 0 else self.item_color
            pygame.draw.rect(screen, color, item_rect)

            # Draw text
            text_surface = self.font.render(item, True, self.text_color)
            text_x = self.rect.x + 10
            text_y = item_y + (self.item_height - text_surface.get_height()) // 2
            screen.blit(text_surface, (text_x, text_y))
