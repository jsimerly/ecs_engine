from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .component import SingletonComponent, Component
    from .component_pool import ComponentPool
    from .entity import Entity

    T = TypeVar('T', bound=SingletonComponent)

class IEcsAdmin(ABC):
    @abstractmethod
    def get_component_pool(self, component_type: Type[Component]) -> ComponentPool:
        pass

    @abstractmethod
    def get_entity(self, entity_id: int) -> Entity:
        pass

    @abstractmethod
    def get_singleton_component(self, component: Type[T]) -> T:
        pass

class IEventBus(ABC):
    @abstractmethod
    def subscribe(self, event_name: str, callback: Callable):
        pass

    @abstractmethod
    def publish(self, event_name: str, **kwargs):
        pass
