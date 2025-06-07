"""
Simple physics system for basic speed and pedaling mechanics.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PhysicsState:
    """Simple physics state without complex mechanics."""

    speed: float = 0.0
    distance_traveled: float = 0.0
    stamina: float = 100.0  # Stamina from 0-100
    last_pedal_side: Optional[str] = None
    last_pedal_time: int = 0
    last_pedal_interval: int = 0  # Time between last two pedals


class Physics:
    """
    Simple physics system for basic cycling mechanics.

    To calculate speed from current interval, we use the following formula:
    speed_at_0ms = max_speed + max_speed*min_pedal_interval/(max_pedal_interval-min_pedal_interval)
    current_speed = speed_at_0ms - current_interval * max_speed / (max_pedal_interval-min_pedal_interval)

    To calculate interval from speed, we use the following formula:
    target_interval = (speed_at_0ms - current_speed) * (max_pedal_interval-min_pedal_interval) / max_speed

    The stamina formula is:
    stamina_change = -(1/1000) * (current_interval - target_interval)^2 + 10
    """

    def __init__(self, max_speed: float = 35.0):
        self.max_speed = max_speed
        self.state = PhysicsState()

        # Physics parameters
        self.min_speed = 0.0
        self.min_moving_speed = 1.0
        self.max_speed = 35.0
        self.max_stamina = 100.0
        self.min_stamina = 0.0

        # Pedaling frequency parameters
        self.min_pedal_interval = 150  # Minimum time between pedals (ms)
        self.max_pedal_interval = 3000  # Max time between pedals (ms)

        self.speed_at_0ms = (
            self.max_speed
            + self.max_speed
            * self.min_pedal_interval
            / (self.max_pedal_interval - self.min_pedal_interval)
        )

    def reset(self):
        """Reset physics state."""
        self.state = PhysicsState()

    def get_curr_interval(self) -> int:
        """
        Calculate expected pedal interval based on current speed.
        = (speed_at_0ms - current_speed) * (max_pedal_interval-min_pedal_interval) / max_speed
        """
        return int(
            (self.speed_at_0ms - self.state.speed)
            * (self.max_pedal_interval - self.min_pedal_interval)
            / self.max_speed
        )

    def get_time_since_last_pedal(self, current_time: int) -> int:
        """Get time since last pedal."""
        if self.state.last_pedal_time == 0:
            return 0
        return current_time - self.state.last_pedal_time

    def get_last_pedal_interval(self) -> int:
        """Get the interval of the last pedal stroke."""
        return self.state.last_pedal_interval

    def predict_speed_change(self, current_time: int) -> float:
        """
        Predict how speed would change if we pedaled right now.
        speed_for_interval = speed_at_0ms - current_interval * max_speed / (max_pedal_interval-min_pedal_interval)
        """
        if self.state.last_pedal_time == 0:
            return self.min_moving_speed  # First pedal always increases speed

        new_interval = current_time - self.state.last_pedal_time
        current_speed = self.state.speed
        speed_for_interval = self.speed_at_0ms - new_interval * self.max_speed / (
            self.max_pedal_interval - self.min_pedal_interval
        )

        if new_interval < self.min_pedal_interval:
            return 0  # Too fast, no change

        return speed_for_interval - current_speed

    def predict_stamina_change(self, current_time: int) -> float:
        """Predict how stamina would change if we pedaled right now."""
        if self.state.last_pedal_time == 0:
            return 0  # First pedal doesn't affect stamina much

        new_interval = current_time - self.state.last_pedal_time
        current_interval = self.get_curr_interval()

        if new_interval < self.min_pedal_interval:
            return -100  # Spamming pedals is bad

        timing_diff = new_interval - current_interval

        if timing_diff > 0:
            # the pedal is late
            return int(-3 / 40.0 * (timing_diff) + 15)
        else:
            # the pedal is early
            return int(3 / 40.0 * (timing_diff + 200))

    def handle_pedal(self, side: str, current_time: int) -> bool:
        """Handle a pedal input and return if it was successful."""
        # Check if alternating properly
        if self.state.last_pedal_side is not None:
            if side == self.state.last_pedal_side:
                # Same side twice - not allowed
                return False

        # Check minimum timing
        if self.state.last_pedal_time > 0:
            stamina_change = self.predict_stamina_change(current_time)
            speed_change = self.predict_speed_change(current_time)
            self.state.speed = min(
                max(self.min_speed, self.state.speed + speed_change), self.max_speed
            )
            self.state.stamina = min(
                max(self.min_stamina, self.state.stamina + stamina_change),
                self.max_stamina,
            )
        else:
            self.state.speed = self.min_moving_speed

        self.state.last_pedal_side = side
        self.state.last_pedal_time = current_time

        return True

    def update(self, dt: float, current_time: int):
        """Update physics state."""
        # If we go too long without pedaling, reduce stamina to 0
        if self.state.last_pedal_time > 0:
            time_since_last = current_time - self.state.last_pedal_time
            if time_since_last > self.max_pedal_interval:
                self.state.stamina = self.min_stamina
                return

        # Update distance traveled
        if self.state.speed > 0:
            # Convert speed from mph to pixels per second (rough conversion)
            pixels_per_second = (
                self.state.speed * 10
            )  # Adjust this multiplier as needed
            distance_delta = pixels_per_second * (dt / 1000.0)
            self.state.distance_traveled += distance_delta

    def get_speed_mph(self) -> float:
        """Get current speed in mph."""
        return self.state.speed

    def get_distance_meters(self) -> float:
        """Get distance traveled in meters (approximate)."""
        return self.state.distance_traveled / 3.0  # Rough pixel to meter conversion

    def get_stamina(self) -> float:
        """Get current stamina."""
        return self.state.stamina
