from typing import Any
import unittest
from .component import Component, SingletonComponent
from .entity import Entity

class HealthComponent(Component):
    def __init__(self, health) -> None:
        self.health:int = health
        self.max_health: int = health

class PositionComponent(Component):
    def __init__(self, x, y) -> None:
        self.x: int = x
        self.y: int = y

    def serialize(self) -> Any:
        return {'x': self.x, 'y': self.y}
    
    @classmethod
    def deserialize(cls, serialized_data: Any):
        return cls(**serialized_data)
    
class TestComponent(unittest.TestCase):
    def setUp(self) -> None:
        self.health_comp = HealthComponent(100)
        self.pos_comp = PositionComponent(1, 2)

    def test_component_initialization(self):
        self.assertEqual(self.health_comp.health, 100)
        self.assertEqual(self.health_comp.max_health, 100)

    def test_component_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.health_comp.serialize()
            self.health_comp.deserialize()

    def test_serialization(self):
        serialized_pos_comp = self.pos_comp.serialize()
        self.assertEqual(serialized_pos_comp, {'x': 1, 'y': 2})

    def test_deserialize(self):
        serialized_pos_comp = self.pos_comp.serialize()
        deserialized_pos_comp = PositionComponent.deserialize(serialized_pos_comp)

        self.assertEqual(PositionComponent, type(deserialized_pos_comp))
        self.assertEqual(deserialized_pos_comp.x, self.pos_comp.x)
        self.assertEqual(deserialized_pos_comp.y, self.pos_comp.y)

class InputComponent(SingletonComponent):
    def __init__(self, mouse_pos):
        self.mouse_pos: tuple[int,int] = mouse_pos
        self.clicked = False

class TestSingletonComponent(unittest.TestCase):
    def setUp(self) -> None:
        self.input_comp = InputComponent((100, 100))

    def test_singleton_values(self):
        self.assertEqual(self.input_comp.mouse_pos, (100,100))

    def test_singleton_creation(self):
        self.input_comp.clicked = True
        new_input_comp = InputComponent((200, 200))
        self.assertEqual(new_input_comp, self.input_comp)

class TestEntity(unittest.TestCase):
    def setUp(self) -> None:
        Entity.reset_attributes()
        self.entity = Entity()

    def test_next_id(self):
        self.assertEqual(self.entity.id, 0)
        self.assertEqual(Entity._next_id, 1)

    def test_add_component(self):
        health_component = HealthComponent(100)
        pos_component = PositionComponent(0,0)
        self.entity._add_component(health_component)
        
        expected_components = {HealthComponent: health_component}
        self.assertEqual(expected_components, self.entity.components)

        self.entity._add_component(pos_component)
        expected_components[PositionComponent] = pos_component
        self.assertEqual(expected_components, self.entity.components)

    def test_remove_component(self):
        health_component = HealthComponent(100)
        pos_component = PositionComponent(0,0)
        self.entity._add_component(health_component)
        self.entity._add_component(pos_component)
        self.entity._remove_component(HealthComponent)
    
        expected_components = {PositionComponent: pos_component}
        self.assertEqual(expected_components, self.entity.components)
    
    def test_get_component(self):
        pos_component = PositionComponent(0,0)
        self.entity._add_component(pos_component)
        component = self.entity.get_component(PositionComponent)
        self.assertEqual(pos_component, component)

    def test_get_component_missing(self):
        component = self.entity.get_component(PositionComponent)
        self.assertIsNone(component)

    def test_has_component(self):
        pos_component = PositionComponent(0,0)
        self.entity._add_component(pos_component)
        has_pos_component = self.entity.has_component(PositionComponent)
        has_health_componnet = self.entity.has_component(HealthComponent)

        self.assertTrue(has_pos_component)
        self.assertFalse(has_health_componnet)

    def test_reset_attributes(self):
        Entity._next_id = 300
        Entity.max_entities = 400
        Entity.destroyed_entities_ids = [42]
        Entity.reset_attributes()

        self.assertEqual(Entity._next_id, 0)
        self.assertEqual(Entity.max_entities, 1000)
        self.assertEqual(Entity.destroyed_entities_ids, [])

        Entity.reset_attributes(4000)
        self.assertEqual(Entity.max_entities, 4000)

class TestEntityNext(unittest.TestCase):
    def setUp(self) -> None:
        Entity.reset_attributes()

    def test_raise_over_entity_limit(self):
        Entity.destroyed_entities_ids = []
        Entity._next_id = 1000
        Entity.max_entities = 1000
        with self.assertRaises(ValueError):
            new_entity = Entity()

    def test_destoryed_entity_id(self):
        Entity.destroyed_entities_ids = [42]
        Entity._next_id = 1000
        Entity.max_entities = 1000
        new_entity_1 = Entity()
        new_entity_2 = Entity()
        self.assertEqual(new_entity_1.id, 1000)
        self.assertEqual(new_entity_2.id, 42)

class TestComponentPool(unittest.TestCase):
    ...



if __name__ == '__main__':
    unittest.main()