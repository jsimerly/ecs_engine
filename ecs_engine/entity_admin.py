from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar
from .entity import Entity
from .events import EventBus
from .component_pool import ComponentPool
from .interfaces import IEcsAdmin
from .entity_manager import EntityManager

if TYPE_CHECKING:
    from ecs_engine.system import System
    from component import Component, SingletonComponent
    T = TypeVar('T', bound=SingletonComponent)

class EcsAdmin(IEcsAdmin):
    '''
    Manages the core functionality of the Entity Component System (ECS),
    acting as the central registry for entities, components, systems, and events.

    Attributes:
        events (list[str]): A list of event names to be registered with the event bus.
        init_systems (list[Type[System]]): A list of system types to be initialized.
        max_entities (int): The maximum number of entities the ECS can manage.
        entity_map (dict[int, Entity]): A mapping of entity IDs to Entity instances.
        components (list[Component]): A list of all components managed by the ECS.
        component_pools (dict[Type[Component], ComponentPool]): A dictionary mapping component types
            to their respective ComponentPool instances for efficient management.
        singleton_components (dict[Type[SingletonComponent], SingletonComponent]): A dictionary holding
            instances of singleton components.

    Methods:
        add_singleton_component: Registers a singleton component with the ECS.
        get_singleton_component: Retrieves a registered singleton component by type.
        create_component_pool: Creates and registers a new component pool for a specific component type.
        get_component_pool: Retrieves a component pool for a specific component type, if it exists.
        create_entity: Creates a new entity, optionally initializing it with a set of components.
        get_entity: Retrieves an entity by its ID.
        attach_component_to_entity: Attaches a component to an entity and registers the entity with the relevant component pool.
    '''
    events: list[str] = []
    init_systems: list[Type[System]] = []
    
    def __init__(self, max_entities: int = 1000):
        '''
        Args:
            max_entities (int): The maximum number of entities that can be managed by the ECS.
        '''
        self.max_entities = max_entities
        self.entity_manager = EntityManager(max_entities)

        self.event_bus = EventBus()
        self.systems: list[System] = []

        self._register_events(self.events)
        self._create_systems(self.init_systems)

        self.entity_map: dict[int, Entity] = {}
        self.components: list[Component] = []
        self.component_pools: dict[Type[Component], ComponentPool] = {}
        self.singleton_components: dict[Type[SingletonComponent], SingletonComponent] = {}

    def __repr__(self) -> str:
        return str(self.__class__)
    
    def add_singleton_component(self, component: T):
        '''
        Registers a singleton component instance with the ECS.

        Args:
            component (SingletonComponent): An instance of a singleton component to be registered.
        '''
        self.singleton_components[type(component)] = component 
    
    def get_singleton_component(self, component_type: type[T]) -> T:
        '''
        Retrieves a singleton component instance by its type.

        Args:
            component_type (type[T]): The class type of the singleton component to retrieve.

        Returns:
            An instance of the specified singleton component type.
        '''
        return self.singleton_components[component_type]

    def create_component_pool(self, component_type: Type[Component]) -> ComponentPool:
        '''
        Creates a new component pool for managing instances of a specific component type.

        Args:
            component_type (Type[Component]): The component type for which to create a pool.

        Returns:
            A new ComponentPool instance for the specified component type.
        '''
        new_component_pool = ComponentPool(
            component_type=component_type, 
            entity_capacity=self.max_entities, 
        )
        self.component_pools[component_type] = new_component_pool
        return new_component_pool
    
    def get_component_pool(self, component_type: Type[Component]) -> ComponentPool | None:
        '''
        Retrieves the component pool associated with a specific component type, if it exists.

        Args:
            component_type (Type[Component]): The component type whose pool to retrieve.

        Returns:
            The ComponentPool instance for the specified component type, or None if not found.
        '''
        return self.component_pools.get(component_type)
    
    def create_entity(self, components=None) -> Entity:
        '''
        Creates a new entity and optionally initializes it with a given set of components.

        Args:
            components (list[Component], optional): A list of components to attach to the new entity.

        Returns:
            The newly created Entity instance.
        '''
        entity = self.entity_manager.create_entity()
        self.entity_map[entity.id] = entity
        
        if components is None:
            components = []

        for component in components:
            self.attach_component_to_entity(entity, component)
        return entity

    def get_entity(self, entity_id: int) -> Entity:
        '''
        Retrieves an entity by its ID.

        Args:
            entity_id (int): The ID of the entity to retrieve.

        Returns:
            The Entity instance with the specified ID.
        '''
        return self.entity_map[entity_id]

    def attach_component_to_entity(self, entity: Entity, component: Component):
        '''
        Attaches a component to an entity and registers the entity with the component's pool.

        Args:
            entity (Entity): The entity to which the component will be attached.
            component (Component): The component to attach to the entity.
        '''
        entity._add_component(component)
        component_pool = self.get_component_pool(type(component))
        if component_pool is None:
            component_pool = self.create_component_pool(type(component))
        component_pool.add_entity(entity)

    def _register_events(self, events: list[str]):
        '''
        Registers a list of event names with the event bus.

        Args:
            events (list[str]): The list of event names to register.
        '''
        for event in events:
            self.event_bus.register_event(event)

    def _create_systems(self, systems: list[System]):
        '''
        Initializes and registers a list of system types with the ECS.

        Args:
            systems (list[System]): The list of system types to initialize and register.
        '''
        for System in systems:
            system_obj = System(self, self.event_bus)
            self.systems.append(system_obj)



    





  


    

    



    

    