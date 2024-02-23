from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar

if TYPE_CHECKING:
    from component import Component
    T = TypeVar('T', bound=Component)

class Entity:
    next_id = 0
    max_entities = 1000
    destroyed_entities_ids = []

    def __init__(self):
        self.id: int = Entity.next_id
        self.create_next_id()
        self.components: dict[Type[Component], Component] =  {}

    # Creates a new ID for the next entity to be created. If we've reached 1000 entities we recycle old ids. This is needed for our SparseSet System in our Component Pools
    def create_next_id(self):
        if self.next_id >= self.max_entities:
            if not self.destroyed_entities_ids: 
                raise ValueError("No available IDs: 'destroyed_entities_ids' is empty.")
            Entity.next_id = self.destroyed_entities_ids.pop()
        else:
            Entity.next_id += 1

    #this will add and update components. If the component already exists, it will be overwritten. Be careful with this as it may cause unintended interactions.
    def _add_component(self, component: Component):
        self.components[type(component)] = component

    # Remove the component from the entity.
    def _remove_component(self, component_type: Type[Component]):
        del self.components[component_type]

    # return the component if it exists. If not it will return None
    def get_component(self, component_type: Type[T]) -> T | None:
        if component_type in self.components:
            return self.components[component_type]
        return None
            
    # returns a boolean determining if the entity has said component.
    def has_component(self, component_type: Type[Component]) -> bool:
        return component_type in self.components
    
    @classmethod
    def reset_attributes(cls, max_entites:int=1000):
        cls.next_id = 0
        cls.destroyed_entities_ids = []
        cls.max_entities = max_entites

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    