from __future__ import annotations
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Type, Callable, TypeVar
from functools import wraps

if TYPE_CHECKING:
    from component import Component, SingletonComponent
    from component_pool import ComponentPool
    from entity import Entity
    from interfaces import IEventBus, IEcsAdmin

    T = TypeVar('T', bound=SingletonComponent)

def subscribe_to_event(event_name):
    def decorator(func):
        if not hasattr(func, '_event_subscriptions'):
            func._event_subscriptions = []
        func._event_subscriptions.append(event_name)
        return func
    return decorator

class System(ABC):
    required_components = []

    def __init__(self, ecs_admin: IEcsAdmin, event_bus: IEventBus):
        self._required_components: list[Type[Component]] = self.required_components
        self.ecs_admin: IEcsAdmin = ecs_admin
        self.event_bus: IEventBus = event_bus
        self.subscribe_to_events()
            
        super().__init__()

    #this subscribes to all of the events with the subscribe_to_event decorator.
    def subscribe_to_events(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_event_subscriptions'):
                for event_name in attr._event_subscriptions:
                    self.event_bus.subscribe(event_name, getattr(self, attr_name))
    
    def publish_event(self, event_name: str, **kwargs):
        self.event_bus.publish(event_name, **kwargs)

    def get_component_pools(self) -> list[ComponentPool] | None:
        required_component_pools = []
        for component_type in self._required_components:
            component_pool = self.ecs_admin.get_component_pool(component_type)
            if component_pool:
                required_component_pools.append(component_pool)
                sorted_component_pools = sorted(required_component_pools, key=lambda pool: len(pool.entity_ids))
                return sorted_component_pools
            
    def get_singleton_component(self, component: Type[T]) -> T:
        return self.ecs_admin.get_singleton_component(component)

    def get_entity(self, entity_id: int) -> Entity:
        return self.ecs_admin.get_entity(entity_id)
        
    def get_required_entities(self) -> list[Entity]:
        entities: list[Entity] = []
        required_component_pools = self.get_component_pools()
        if required_component_pools:
            main_pool = required_component_pools.pop()

            for entity_id in main_pool.entity_ids:
                add_entity = True
                entity = self.get_entity(entity_id=entity_id)

                for remaining_component in required_component_pools:
                    if not entity.has_component(remaining_component.component_type):
                        add_entity = False
                        break

                if add_entity:
                    entities.append(entity)
                    
        return entities
        

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    