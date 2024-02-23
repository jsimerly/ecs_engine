from __future__ import annotations
from typing import Any, Type, TYPE_CHECKING, TypeVar
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    T = TypeVar('T', bound='SingletonComponent')

class Component(ABC):
    '''
    Abstract base class for components in an Entity Component System (ECS) architecture.

    Components are reusable data containers that entities use to store state or attributes.
    Standard Components are intended for use cases where multiple entities each have
    their own distinct instances of a component, such as a HealthComponent where
    each entity has separate health values.

    Methods:
        serialize: Converts the component's state to a serializable format.
        deserialize: Reconstructs a component instance from serialized data.

    Subclasses must implement serialize and deserialize methods to support
    serialization and deserialization of component state.
    '''

    def serialize(self) -> Any:
        raise NotImplementedError(f'{self.__class__} has not defined a serialize method.')
    
    @classmethod
    def deserialize(cls: Type, serialized_data: Any) -> Type:
        raise NotImplementedError(f'{cls} has not defined a deserialize method.')
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    
class SingletonComponent(Component):
    '''
    A singleton component for global state management within an ECS architecture.

    SingletonComponents are used when systems and entities need to access shared information
    that is not owned by individual entities, facilitating a global state accessible across
    the entire ECS. This design prevents systems from maintaining their own separate states,
    promoting a more unified and accessible state management approach.

    Example use cases include a global InputComponent that stores the user's most recent inputs,
    ensuring that this information is readily available to any system or entity that requires it.
    '''

    _instances: dict[Type, SingletonComponent] = {}

    def __new__(cls : Type[T], *args, **kwargs) -> T:
        '''
        Overrides the __new__ method to ensure only one instance of each SingletonComponent subclass exists.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The singleton instance of the requested SingletonComponent subclass.
        '''
        if cls not in cls._instances:
            instance = super(SingletonComponent, cls).__new__(cls)
            cls._instances[cls] = instance
            return instance
        return cls._instances[cls]
    
    