from __future__ import annotations
from typing import Any, Type
from abc import ABC

class Component(ABC):
    '''
        This is a standard use Abstact Component. Standard Components are using for components that are attached to many entities. eg: a HealthComponent where many entities will have seperate health.
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
        This is a SingletonComponent as outline by OW's Tim Ford in his GDC 2017 talk. The responsiblity of this component is for when systems and entities need to access the same infomation that is not owned by entities themselves. This prevents Systems from having their own state but instead creates a global state. eg: an InputComponent that stores the users most recent input.
    '''
    _instances: dict[Type, SingletonComponent]

    def __new__(cls, *args, **kwargs) -> SingletonComponent:
        if cls not in cls._instances:
            instance = super(SingletonComponent, cls).__new__(cls)
            cls._instances[cls] = instance
            return instance
        return cls._instances[cls]
    
    