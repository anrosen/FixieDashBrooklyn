"""
Dependency injection container for FixieDashBrooklyn.
Manages service registration, resolution, and lifecycle.
"""

from typing import Any, Callable, Dict, Type, TypeVar

from game.services.background_event_service import BackgroundEventService

T = TypeVar("T")


class ServiceContainer:
    """Dependency injection container for managing services."""

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._initialized = False

    def register_singleton(self, service_type: Type[T], instance: T) -> None:
        """Register a singleton service instance."""
        key = self._get_service_key(service_type)
        self._singletons[key] = instance

    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for creating service instances."""
        key = self._get_service_key(service_type)
        self._factories[key] = factory

    def register_service(self, service_type: Type[T], implementation: Type[T]) -> None:
        """Register a service implementation type."""
        key = self._get_service_key(service_type)
        self._factories[key] = implementation

    def get(self, service_type: Type[T]) -> T:
        """Resolve and return a service instance."""
        key = self._get_service_key(service_type)

        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]

        # Check factories
        if key in self._factories:
            factory = self._factories[key]
            if callable(factory):
                if isinstance(factory, type):
                    # It's a class, instantiate it
                    instance = factory()
                else:
                    # It's a factory function, call it
                    instance = factory()
                return instance

        raise ValueError(f"Service {service_type.__name__} not registered")

    def get_singleton(self, service_type: Type[T]) -> T:
        """Get or create a singleton service instance."""
        key = self._get_service_key(service_type)

        # Return existing singleton
        if key in self._singletons:
            return self._singletons[key]

        # Create new singleton from factory
        if key in self._factories:
            factory = self._factories[key]
            if isinstance(factory, type):
                instance = factory()
            else:
                instance = factory()
            self._singletons[key] = instance
            return instance

        raise ValueError(f"Service {service_type.__name__} not registered")

    def _get_service_key(self, service_type: Type) -> str:
        """Generate a key for the service type."""
        return f"{service_type.__module__}.{service_type.__name__}"

    def initialize_core_services(self):
        """Initialize core services needed by the application."""
        if self._initialized:
            return

        # Register background event service as singleton
        background_service = BackgroundEventService()
        self.register_singleton(BackgroundEventService, background_service)

        self._initialized = True

    def shutdown(self):
        """Shutdown all services and clean up resources."""
        # Shutdown background event service
        if BackgroundEventService.__name__ in [
            key.split(".")[-1] for key in self._singletons.keys()
        ]:
            bg_service = self.get_singleton(BackgroundEventService)
            bg_service.shutdown()

        # Clear all services
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._initialized = False

    @property
    def background_event_service(self) -> BackgroundEventService:
        """Get the background event service."""
        return self.get_singleton(BackgroundEventService)


# Global container instance
container = ServiceContainer()

# Initialize core services
container.initialize_core_services()
