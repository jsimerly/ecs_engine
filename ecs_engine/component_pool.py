from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar

if TYPE_CHECKING:
    from component import Component
    from entity import Entity
    T = TypeVar('T', bound=Component)

class ComponentPool:
    ''' 
        A component pool is a pool of entities that contain the component. The purpose of this component pool is to make look up, interation, addition, and removal of entities from component pools O(1).

        This class takes advange of a 'Sparse Set' data structure for caching efficency and lookup efficency.
    '''
    def __init__(self, component_type: Type[T],  entity_capacity: int) -> None:
        self.component_type: Type[T] = component_type
        self.pool: list[T] = []
        self.active: list[Entity] = []

        self.entity_ids = [] # the 'dense' array in the sparse set that hold the ids for the entities
        self.sparse = [-1] * entity_capacity
        self.entity_capacity = entity_capacity

    def get_or_create_component_obj(self, **kwargs) -> T:
        if not self.pool:
            new_instance = self.component_type(**kwargs)
            self.active.append(new_instance)
            return new_instance
        else: 
            instance = self.pool.pop()
            self.active.append(instance)
            return instance
        
    def release_component(self, instance: Component):
        self.active.remove(instance)
        self.pool.append(instance)
        

    ### Entity Sparse Set ###
    def add_entity(self, entity: Entity):
        if entity.has_component(self.component_type):
            if self.sparse[entity.id] == -1:
                self.sparse[entity.id] = len(self.entity_ids)
                self.entity_ids.append(entity.id)
        else:
            raise ValueError(f'{entity.__class__.__name__} must have a a {self.component_type.__class__.__name__} component.')

    # returns a boolean of whether the entity is in the pool or not.
    def contains_entity(self, entity: Entity) -> bool:
        if 0 <= entity.id < self.entity_capacity:
            sparse_index = self.sparse[entity.id]
            if 0 <= sparse_index < len(self.entity_ids):
                return self.entity_ids[sparse_index] == entity.id and sparse_index != -1
        return False
    
    # Check is the entity is in the pool and if it is it removes it and adjust the dense, sparse arrays to flex the change.
    def remove_entity(self, entity: Entity):
        if self.contains_entity(entity):
            dense_index = self.sparse[entity.id]
            last_entity_id = self.entity_ids[-1]

            self.entity_ids[dense_index] = last_entity_id
            self.sparse[last_entity_id] = dense_index
            self.sparse[entity.id] = -1

            self.entity_ids.pop()
