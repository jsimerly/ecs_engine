from typing import TYPE_CHECKING, Type
from entity import Entity
from component_pool import ComponentPool

if TYPE_CHECKING:
    from system import System
    from component import Component, SingletonComponent

class EcsAdmin:
    '''
        This acts as a container for entities, components, and systems.
    '''
    # These are the systems that will be spun up on initialization. It's recommended to include all systems on start-up.
    init_systems = [

    ]

    def __init__(self, max_entities:int = 1000) -> None:
        self.max_entities = max_entities
        Entity.max_entities = max_entities

        self.entity_map: dict[int, Entity] = {}
        self.components: list[Component] = []
        self.singleton_components: dict[Type[SingletonComponent], SingletonComponent] = {}
        self.systems: list[System] = self._create_systems()
        self.component_pools: dict[Type[Component], ComponentPool]

    def __repr__(self) -> str:
        return str(self.__class__)

    # Updates the systems giving it a time_step to determine how long it's been since the last process.
    def update(self, time_step: float):
        for system in self.systems:
            system.update(time_step)

    # Creates a new component pool or overwrites the previous one if called.
    def create_component_pool(self, component_type: Type[Component]) -> ComponentPool:
        new_component_pool = ComponentPool(component_type=component_type, capacity=self.max_entities)
        self.component_pools[component_type] = new_component_pool
        return new_component_pool

    # returns a component pool based on needed components.
    def get_component_pool(self, component_type: Type[Component]) -> ComponentPool | None:
        return self.component_pools.get(component_type)
    
    # returns an Entity object for the corrosponding id. It should raise an error if there is no corrosponding.
    def get_entity(self, entity_id: int) -> Entity:
        self.entity_map[entity_id]

    # attaches a component to an entity and then adds that entity to that components component pool.
    def attach_component(self, entity: Entity, component: Component):
        entity._add_component(component)
        component_pool = self.get_component_pool(type(component))
        if component_pool is None:
            component_pool = self.create_component_pool(type(component))
        component_pool.add(entity)


    # Creates all of the system on instantiation 
    def _create_systems(self):
        return [system(self) for system in self.init_systems]

    





  


    

    



    

    