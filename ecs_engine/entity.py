from __future__ import annotations
from typing import TYPE_CHECKING, Type, TypeVar

if TYPE_CHECKING:
    from .component import Component
    T = TypeVar('T', bound=Component)

class Entity:
    '''
    Represents an individual entity in the Entity Component System (ECS).

    An entity is a general-purpose object characterized by its unique ID and
    the components attached to it. Entities themselves are kept lightweight
    and flexible, serving as containers for components that actually implement
    functionality and data.

    Attributes:
        next_id (int): Class variable to track the next available entity ID.
        max_entities (int): Class variable to limit the total number of entities.
        destroyed_entities_ids (list[int]): Class variable to recycle IDs of destroyed entities.

    Methods:
        create_next_id: Generates the next entity ID, recycling IDs if necessary.
        _add_component: Attaches a component to the entity.
        _remove_component: Removes a component from the entity.
        get_component: Retrieves a component attached to the entity, if it exists.
        has_component: Checks whether the entity has a specific type of component attached.
        reset_attributes: Resets class-level entity tracking attributes.
    '''

    def __init__(self, id: int):
        self.id: int = id
        self.components: dict[Type[Component], Component] =  {}

    def _add_component(self, component: Component):
        '''
        Attaches or updates a component to this entity. Existing components of the same type are overwritten.

        Args:
            component (Component): The component instance to attach.
        '''
        self.components[type(component)] = component

    def _remove_component(self, component_type: Type[Component]):
        '''
        Removes a component of the specified type from the entity.

        Args:
            component_type (Type[Component]): The type of component to remove.
        '''
        del self.components[component_type]

    def get_component(self, component_type: Type[T]) -> T | None:
        '''
        Retrieves a component of a specific type attached to this entity, if it exists.

        Args:
            component_type (Type[Component]): The type of component to retrieve.

        Returns:
            The component instance if found, otherwise None.
        '''
        if component_type in self.components:
            return self.components[component_type]
        return None
            
    def has_component(self, component_type: Type[Component]) -> bool:
        '''
        Checks whether the entity has a component of a specific type attached.

        Args:
            component_type (Type[Component]): The type of component to check for.

        Returns:
            True if the component is attached, False otherwise.
        '''
        return component_type in self.components
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    