from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar
from .entity import Entity
from .events import EventBus
from .component_pool import ComponentPool
from .interfaces import IEcsAdmin

if TYPE_CHECKING:
    from system import System
    from component import Component, SingletonComponent
    T = TypeVar('T', bound=SingletonComponent)

class EcsAdmin(IEcsAdmin):
    '''
        This acts as a container for entities, components, and systems.
    '''
    events: list[str] = []
    init_systems: list[Type[System]] = []
    
    def __init__(self, max_entities: int = 1000):
        self.max_entities = max_entities
        Entity.max_entities = max_entities

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
        self.singleton_components[type(component)] = component 
    
    def get_singleton_component(self, component_type: type[T]) -> T:
        return self.singleton_components[component_type]

    def create_component_pool(self, component_type: Type[Component]) -> ComponentPool:
        new_component_pool = ComponentPool(
            component_type=component_type, 
            entity_capacity=self.max_entities, 
        )
        self.component_pools[component_type] = new_component_pool
        return new_component_pool
    
    def get_component_pool(self, component_type: Type[Component]) -> ComponentPool | None:
        return self.component_pools.get(component_type)
    
    def create_entity(self, components=None) -> Entity:
        entity = Entity()
        self.entity_map[entity.id] = entity
        
        if components is None:
            components = []

        for component in components:
            self.attach_component_to_entity(entity, component)
        return entity

    def get_entity(self, entity_id: int) -> Entity:
        return self.entity_map[entity_id]

    # attaches a component to an entity and then adds that entity to that components component pool.
    def attach_component_to_entity(self, entity: Entity, component: Component):
        entity._add_component(component)
        component_pool = self.get_component_pool(type(component))
        if component_pool is None:
            component_pool = self.create_component_pool(type(component))
        component_pool.add_entity(entity)

    def _register_events(self, events: list[str]):
        for event in events:
            self.event_bus.register_event(event)

    def _create_systems(self, systems: list[System]):
        for System in systems:
            system_obj = System(self, self.event_bus)
            self.systems.append(system_obj)



    





  


    

    



    

    