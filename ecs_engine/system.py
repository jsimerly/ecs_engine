from __future__ import annotations
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Type, Callable, TypeVar
from functools import wraps

if TYPE_CHECKING:
    from component import Component, SingletonComponent
    from component_pool import ComponentPool
    from entity import Entity
    from interfaces import IEventBus, IEcsAdmin
    from entity_builder import Builder

    T = TypeVar('T', bound=SingletonComponent)

def subscribe_to_event(event_name):
    '''
    Decorator to mark a System method for subscription to a specific event.
    
    Args:
        event_name (str): The name of the event to subscribe to.
        
    Returns:
        The decorated function with an added '_event_subscriptions' attribute.
    '''
    def decorator(func):
        if not hasattr(func, '_event_subscriptions'):
            func._event_subscriptions = []
        func._event_subscriptions.append(event_name)
        return func
    return decorator

class System(ABC):
    '''
    Abstract base class for systems in an Entity Component System (ECS) framework.
    
    Systems encapsulate the logic that operates on entities possessing a specific set of components.
    This class provides mechanisms to subscribe to events, publish events, and access entities and
    components relevant to the system's functionality.
    
    Attributes:
        _required_components (list[Type[Component]]): A list of component types required by the system.
        ecs_admin (IEcsAdmin): The central ECS administration interface, providing access to entities and components.
        event_bus (IEventBus): The event bus for subscribing to and publishing events.
    '''
    required_components = []

    def __init__(self, ecs_admin: IEcsAdmin, event_bus: IEventBus):
        '''
        Args:
            ecs_admin (IEcsAdmin): The central ECS administration interface.
            event_bus (IEventBus): The event bus for event communication.
        '''
        self._required_components: list[Type[Component]] = self.required_components
        self.ecs_admin: IEcsAdmin = ecs_admin
        self.event_bus: IEventBus = event_bus
        self.subscribe_to_events()
            
        super().__init__()

    def subscribe_to_events(self):
        '''
        Subscribes the system to events based on methods decorated with `subscribe_to_event`.
        '''
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_event_subscriptions'):
                for event_name in attr._event_subscriptions:
                    self.event_bus.subscribe(event_name, getattr(self, attr_name))
    
    def publish_event(self, event_name: str, **kwargs):
        '''
        Publishes an event through the event bus.
        
        Args:
            event_name (str): The name of the event to publish.
            **kwargs: Arbitrary keyword arguments passed to the event handlers.
        '''
        self.event_bus.publish(event_name, **kwargs)

    def get_component_pools(self) -> list[ComponentPool] | None:
        '''
        Retrieves the component pools for the system's required components.
        
        Returns:
            A list of ComponentPool instances for the required components, sorted by the number of entities.
        '''
        required_component_pools = []
        for component_type in self._required_components:
            component_pool = self.ecs_admin.get_component_pool(component_type)
            if component_pool:
                required_component_pools.append(component_pool)
                sorted_component_pools = sorted(required_component_pools, key=lambda pool: len(pool.entity_ids))
                return sorted_component_pools
            
    def get_singleton_component(self, component: Type[T]) -> T:
        '''
        Retrieves a singleton component instance.
        
        Args:
            component (Type[SingletonComponent]): The type of the singleton component to retrieve.
            
        Returns:
            An instance of the specified singleton component type.
        '''
        return self.ecs_admin.get_singleton_component(component)

    def get_entity(self, entity_id: int) -> Entity:
        '''
        Retrieves an entity by its ID.
        
        Args:
            entity_id (int): The ID of the entity to retrieve.
            
        Returns:
            The Entity instance with the specified ID.
        '''
        return self.ecs_admin.get_entity(entity_id)
    
    def get_builder(self, builder_type: Type[Builder]) -> Builder:
        return self.ecs_admin.get_builder(builder_type)
        
    def get_required_entities(self) -> list[Entity]:
        '''
        Retrieves all entities that possess all of the system's required components.
        
        Returns:
            A list of Entity instances that meet the system's component requirements.
        '''
        entities: list[Entity] = []
        required_component_pools = self.get_component_pools()
        if required_component_pools:
            main_pool = required_component_pools.pop()

            for entity in main_pool.entities:
                add_entity = True

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
    