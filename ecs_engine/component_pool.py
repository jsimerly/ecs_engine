from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar

if TYPE_CHECKING:
    from component import Component
    from entity import Entity
    T = TypeVar('T', bound=Component)

class ComponentPool:
    ''' 
    Manages a pool of components and stores them in memory when out of use to reduce object init times.
    Stores entity_ids in a Sparse Set for quick querying and management.

    Attributes:
        component_type (Type[Component]): The type of component this pool manages.   
        pool (list[Component]): A list of inactive component instances available for reuse.
        active (list[Component): A list of Componens that are actively using components of this type.
        entity_ids (list[int]): The 'dense' array part of the sparse set containing entity IDs.
        sparse (list[int]): The 'sparse' array part of the sparse set for quick lookup.
        entity_capacity (int): The maximum number of entities that can be managed.

    Methods:
        get_or_create
    '''
    def __init__(self, component_type: Type[T],  entity_capacity: int) -> None:
        self.component_type: Type[T] = component_type
        self.pool: list[T] = []
        self.active: list[Component] = []

        self.entity_ids = [] # the 'dense' array in the sparse set that hold the ids for the entities
        self.entities: list[Entity] = []
        self.sparse = [-1] * entity_capacity
        self.entity_capacity = entity_capacity

    def get_or_create_component_obj(self, **kwargs) -> T:
        '''
        Retrieves an inactive component from the pool or creates a new instance if the pool is empty.
        
        Args:
            **kwargs: Arbitrary keyword arguments passed to the component's constructor.

        Returns:
            An instance of the component.
        '''
        if not self.pool:
            new_instance = self.component_type(**kwargs)
            self.active.append(new_instance)
            return new_instance
        else: 
            instance = self.pool.pop()
            self.active.append(instance)
            return instance
        
    def release_component(self, instance: Component):
        '''
        Releases a component instance, making it available for reuse.
        
        Args:
            instance (Component): The component instance to release.
        '''
        self.active.remove(instance)
        self.pool.append(instance)
        


    def add_entity(self, entity: Entity):
        '''
        Adds an entity to the component pool if it has the required component.
        
        Args:
            entity (Entity): The entity to add.
            
        Raises:
            ValueError: If the entity does not have the required component.
        '''
        if entity.has_component(self.component_type):
            if self.sparse[entity.id] == -1:
                self.sparse[entity.id] = len(self.entity_ids)
                self.entity_ids.append(entity.id)
                self.entities.append(entity)
        else:
            raise ValueError(f'{entity.__class__.__name__} must have a a {self.component_type.__class__.__name__} component.')

    def contains_entity(self, entity: Entity) -> bool:
        '''
        Checks if the entity is in the component pool.

        Args:
            entity (Entity): The entity to check.
            
        Returns:
            bool: True if the entity is in the pool, False otherwise.
        '''
        if 0 <= entity.id < self.entity_capacity:
            sparse_index = self.sparse[entity.id]
            if 0 <= sparse_index < len(self.entity_ids):
                return self.entity_ids[sparse_index] == entity.id and sparse_index != -1
        return False
    
    def remove_entity(self, entity: Entity):
        '''
        Removes an entity from the component pool if it is present.
        
        Args:
            entity (Entity): The entity to remove.
        '''
        if self.contains_entity(entity):
            dense_index = self.sparse[entity.id]
            last_entity_id = self.entity_ids[-1]
            last_entity = self.entities[-1]

            self.entity_ids[dense_index] = last_entity_id
            self.entities[dense_index] = last_entity

            self.sparse[last_entity_id] = dense_index
            self.sparse[entity.id] = -1

            self.entity_ids.pop()
            self.entities.pop()
