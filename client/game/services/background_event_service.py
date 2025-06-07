"""
Background event service for handling async tasks.
"""

import asyncio
import atexit
from threading import Thread
from typing import Optional


class BackgroundEventService:
    """Service for handling background async tasks."""

    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[Thread] = None
        self._tasks: set = set()
        self._running = False
        self._start_loop()

    def _start_loop(self):
        """Start the asyncio event loop in a separate thread."""

        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._running = True
            try:
                self._loop.run_forever()
            finally:
                self._running = False

        self._thread = Thread(target=run_loop, daemon=True)
        self._thread.start()

        # Wait for loop to be ready
        while self._loop is None:
            pass

        # Register cleanup
        atexit.register(self.shutdown)

    def add_task(self, coro):
        """Add a coroutine to be executed in the background."""
        if not self._running or self._loop is None:
            return

        def task_done_callback(task):
            self._tasks.discard(task)

        # Schedule the coroutine on the event loop
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        task = asyncio.wrap_future(future, loop=self._loop)
        task.add_done_callback(task_done_callback)
        self._tasks.add(task)

        return task

    def shutdown(self):
        """Shutdown the background event service."""
        if self._running and self._loop is not None:
            # Cancel all pending tasks
            for task in self._tasks.copy():
                if not task.done():
                    task.cancel()

            # Stop the event loop
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._running = False
