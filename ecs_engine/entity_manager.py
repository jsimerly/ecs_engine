from typing import TYPE_CHECKING
from .entity import Entity

if TYPE_CHECKING:
    from component import Component

class EntityManager:
    def __init__(self, max_entities: int) -> None:
        self.next_id = 0
        self.max_entities = max_entities
        self.destroyed_entity_ids = []

    def create_entity(self) -> Entity:
        entity = Entity(self.next_id)
        self.move_to_next_id()
        return entity        
    
    def add_destoryed_entity_id(self, id: int):
        self.destroyed_entity_ids.append(id)

    def move_to_next_id(self):
        '''
        Updates `next_id` for the next entity creation. Recycles old IDs from `destroyed_entities_ids`
        if the `max_entities` limit has been reached. Raises an error if no IDs are available.
        '''

        if self.next_id >= self.max_entities:
            if not self.destroyed_entity_ids: 
                raise ValueError("No available IDs: 'destroyed_entities_ids' is empty.")
            self.next_id = self.destroyed_entity_ids.pop()
        else:
            self.next_id += 1