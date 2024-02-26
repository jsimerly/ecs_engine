from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from .entity_admin import EcsAdmin
    from .component import Component
    from .entity import Entity

class Builder(ABC):
    def __init__(self, ecs_admin: EcsAdmin) -> None:
        self.ecs_admin = ecs_admin

    def build_entity(self, components: list[Component]) -> Entity:
        return self.ecs_admin.create_entity(components)

    def create_component(self, component_type: Type[Component], *args, **kwargs) -> Component:
        component_pool = self.ecs_admin.get_component_pool(component_type)
        component = component_pool.get_or_create_component_obj(*args, **kwargs)
        return component