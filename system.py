from __future__ import annotations
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from entity_admin import EcsAdmin
    from component import Component
    from component_pool import ComponentPool
    from entity import Entity


class System(ABC):
    required_components = []
    uses_time_step = True

    def __init__(self, ecs_admin: EcsAdmin) -> None:
        self._required_components: list[Type[Component]] = self.required_components
        self.admin = ecs_admin
        super().__init__()
    
    @abstractmethod
    def update(self, time: float):
        ...

    def notify_component(self):
        ...

    def get_component_pools(self) -> list[ComponentPool] | None:
        required_component_pools = []
        for component_type in self._required_components:
            component_pool = self.admin.get_component_pool(component_type)
            if component_pool:
                required_component_pools.append(component_pool)
                sorted_component_pools = sorted(required_component_pools, key=lambda pool: len(pool.dense))
                return sorted_component_pools
            
    def get_entity(self, entity_id: int) -> Entity:
        self.admin.get_entity(entity_id)
        
    def get_required_entities(self) -> list[Entity]:
        entities: list[Entity] = []
        required_component_pools = self.get_component_pools()
        if required_component_pools:
            main_pool = required_component_pools.pop()

            for entity_id in main_pool.dense:
                add_entity = True
                entity = self.get_entity(entity_id=entity_id)

                for remaining_component in required_component_pools:
                    if not entity.has_component(remaining_component.component_type):
                        add_entity = False
                        break

                if add_entity:
                    entities.append(entity)
                    
        return entities
        

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    