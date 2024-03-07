from __future__ import annotations
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Type, Callable, TypeVar
from functools import wraps
from .events import subscribe_to_event, subscribe_to_events

if TYPE_CHECKING:
    from .component import Component, SingletonComponent
    from .component_pool import ComponentPool
    from .entity import Entity
    from .interfaces import IEventBus
    from .entity_builder import Builder
    from .entity_admin import EcsAdmin

    T = TypeVar('T', bound=SingletonComponent)
    B = TypeVar('B', bound=Builder)
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

    def __init__(self, ecs_admin: EcsAdmin, event_bus: IEventBus):
        '''
        Args:
            ecs_admin (IEcsAdmin): The central ECS administration interface.
            event_bus (IEventBus): The event bus for event communication.
        '''
        self._required_components: list[Type[Component]] = self.required_components
        self.ecs_admin: EcsAdmin= ecs_admin
        self.event_bus: IEventBus = event_bus
        subscribe_to_events(self)
            
        super().__init__()
    
    def publish_event(self, event_name: str, **kwargs):
        '''
        Publishes an event through the event bus.
        
        Args:
            event_name (str): The name of the event to publish.
            **kwargs: Arbitrary keyword arguments passed to the event handlers.
        '''
        self.event_bus.publish(event_name, **kwargs)
            
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
    
    def get_builder(self, builder_type: Type[B]) -> B:
        return self.ecs_admin.get_builder(builder_type)
    
    def remove_component(self, entity: Entity, component: Component):
        self.ecs_admin.remove_component(entity, component)
    
    def attach_component_to_entity(self, entity: Entity, component: Component):
        self.ecs_admin.attach_component_to_entity(entity, component)

    def create_entity(self, componenets=None) -> Entity:
        return self.ecs_admin.create_entity(componenets)

    def destroy_entity(self, entity: Entity):
        self.ecs_admin.destroy_entity(entity)
        
    def get_required_entities(self) -> list[Entity]:
        '''
        Retrieves all entities that possess all of the system's required components.
        
        Returns:
            A list of Entity instances that meet the system's component requirements.
        '''
        return self.ecs_admin.get_entities_intersect(self.required_components)
    
    def get_entities_intersect(self, component_types:list[Type[Component]]) -> list[Entity]:
        return self.ecs_admin.get_entities_intersect(component_types)
    
    def get_entities_union(self, component_types:list[Type[Component]]) -> list[Entity]:
        return self.ecs_admin.get_entities_union(component_types)

    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    