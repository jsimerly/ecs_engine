from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from component import Component
    from entity import Entity

class ComponentPool:
    ''' 
        A component pool is a pool of entities that contain the component. The purpose of this component pool is to make look up, interation, addition, and removal of entities from component pools O(1).

        This class takes advange of a 'Sparse Set' data structure for caching efficency and lookup efficency.
    '''
    def __init__(self, component_type: Type[Component], capacity: int) -> None:
        self.component_type = component_type
        self.dense = [] #this array hold the id values of the entities themselves
        self.sparse = [-1] * capacity
        self.capacity = capacity
        self.n = 0

    # Adds a new entity to the component pool
    def add(self, entity: Entity):
        if self.sparse[entity.id] == -1:
            self.sparse[entity.id] = len(self.dense)
            self.dense.append(entity)

    # returns a boolean of whether the entity is in the pool or not.
    def contains(self, entity: Entity) -> bool:
        return all([
            0 <= entity.id < self.capacity,
            self.sparse[entity.id] != -1,
            self.dense[self.sparse[entity.id]] == entity.id
        ])
    
    # Check is the entity is in the pool and if it is it removes it and adjust the dense, sparse arrays to flex the change.
    def remove(self, entity: Entity):
        if self.contains(entity):
            dense_index = self.sparse[entity.id]
            last_entity_id = self.dense[-1]

            self.dense[dense_index] = last_entity_id
            self.sparse[last_entity_id] = dense_index
            self.sparse[entity.id] = -1

            self.dense.pop()
