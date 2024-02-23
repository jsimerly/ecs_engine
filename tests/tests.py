from typing import Any
import unittest
from unittest.mock import MagicMock, patch
from ecs_engine.component import Component, SingletonComponent
from ecs_engine.entity import Entity
from ecs_engine.component_pool import ComponentPool
from ecs_engine.entity_admin import EcsAdmin
from ecs_engine.system import System, subscribe_to_event

class HealthComponent(Component):
    def __init__(self, health):
        self.health:int = health
        self.max_health: int = health

class PositionComponent(Component):
    def __init__(self, x, y):
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

    def reset(self):
        self.mouse_pos = (0,0)
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
        self.assertEqual(Entity.next_id, 1)

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
        Entity.next_id = 300
        Entity.max_entities = 400
        Entity.destroyed_entities_ids = [42]
        Entity.reset_attributes()

        self.assertEqual(Entity.next_id, 0)
        self.assertEqual(Entity.max_entities, 1000)
        self.assertEqual(Entity.destroyed_entities_ids, [])

        Entity.reset_attributes(4000)
        self.assertEqual(Entity.max_entities, 4000)

class TestEntityNext(unittest.TestCase):
    def setUp(self) -> None:
        Entity.reset_attributes()

    def test_raise_over_entity_limit(self):
        Entity.destroyed_entities_ids = []
        Entity.next_id = 1000
        Entity.max_entities = 1000
        with self.assertRaises(ValueError):
            new_entity = Entity()

    def test_destoryed_entity_id(self):
        Entity.destroyed_entities_ids = [42]
        Entity.next_id = 1000
        Entity.max_entities = 1000
        new_entity_1 = Entity()
        new_entity_2 = Entity()
        self.assertEqual(new_entity_1.id, 1000)
        self.assertEqual(new_entity_2.id, 42)

class TestComponentPool(unittest.TestCase):
    def setUp(self) -> None:
        self.component_pool = ComponentPool(HealthComponent, entity_capacity=1000)

    def test_get_component_obj(self):
        comp_1 = self.component_pool.get_or_create_component_obj(health=100)
        self.assertEqual(type(comp_1), HealthComponent)
        
        self.component_pool.pool = []
        comp_2 = self.component_pool.get_or_create_component_obj(health=100)
        self.assertEqual(type(comp_2), HealthComponent)

    def test_release_component(self):
        comp_1 = self.component_pool.get_or_create_component_obj(health=100)
        pool_size = len(self.component_pool.pool)
        active_size = len(self.component_pool.active)
        self.assertEqual(pool_size, 0)
        self.assertEqual(active_size, 1)

        self.component_pool.release_component(comp_1)
        pool_size = len(self.component_pool.pool)
        active_size = len(self.component_pool.active)
        self.assertEqual(pool_size, 1)
        self.assertEqual(active_size, 0)

    def test_add_entity(self):
        entity_1 = Entity()
        entity_1._add_component(HealthComponent(100))
        self.component_pool.add_entity(entity_1)
        n_entity_ids = len(self.component_pool.entity_ids)
        self.assertEqual(n_entity_ids, 1)

    def test_add_entity_no_component(self):
        entity_1 = Entity()
        with self.assertRaises(ValueError):
            self.component_pool.add_entity(entity_1)

    def test_contains_entity(self):
        entity_1 = Entity()
        entity_1._add_component(HealthComponent(100))
        entity_2 = Entity()
        self.component_pool.add_entity(entity_1)

        does_contain_entity_1 = self.component_pool.contains_entity(entity_1)
        does_contain_entity_2 = self.component_pool.contains_entity(entity_2)

        self.assertTrue(does_contain_entity_1)
        self.assertFalse(does_contain_entity_2)

    def test_remove_entity(self):
        entity_1 = Entity()
        entity_2 = Entity()
        entity_1._add_component(HealthComponent(100))
        entity_2._add_component(HealthComponent(100))
        self.component_pool.add_entity(entity_1)
        self.component_pool.add_entity(entity_2)

        entity_id_size = len(self.component_pool.entity_ids)
        self.assertEqual(entity_id_size, 2)
        self.component_pool.remove_entity(entity_2)

        entity_id_size = len(self.component_pool.entity_ids)
        self.assertEqual(entity_id_size, 1)

        does_contain_entity_1 = self.component_pool.contains_entity(entity_1)
        does_contain_entity_2 = self.component_pool.contains_entity(entity_2)

        self.assertTrue(does_contain_entity_1)
        self.assertFalse(does_contain_entity_2)
    
class PositionSystem(System):
    required_components = [PositionComponent]

    @subscribe_to_event('update_time_step')
    def update(self, timestep: float):
        entities = self.get_required_entities()
        for entity in entities:
            position_comp = entity.get_component(PositionComponent)
            input_comp = self.get_singleton_component(InputComponent)

            position_comp.x += input_comp.mouse_pos[0]
            position_comp.y += input_comp.mouse_pos[1]

            if input_comp.clicked:
                self.publish_event('test_publish', test=123)

class HealthSystem(System):
    required_components = [HealthComponent]
    updated = False 

    @subscribe_to_event('test_publish')
    def handle_event_test(self, test: int):
        self.updated = test

class World(EcsAdmin):
    init_systems = [PositionSystem, HealthSystem]
    events = ['test_publish', 'update_time_step']

    def run_one_timestep(self):
        timestep = 1/60
        self.event_bus.publish('update_time_step', timestep)

class TestSystem(unittest.TestCase):
    def setUp(self) -> None:
        Entity.reset_attributes()
        self.world = World()
        self.world.create_entity([PositionComponent(0, 0)])
        self.world.add_singleton_component(InputComponent((10,10)))
        self.pos_system: PositionSystem = self.world.systems[0] 
        self.health_system: HealthSystem = self.world.systems[1]
        
    def test_event_subscriptions(self):
        event_bus = self.world.event_bus
        self.assertTrue(self.pos_system.update in event_bus.events['update_time_step'])
        self.assertTrue(self.health_system.handle_event_test in event_bus.events['test_publish'])

    def test_subscribe_to_events(self):
        entities = self.pos_system.get_required_entities()
        for entity in entities:
            pos_component = entity.get_component(PositionComponent)
            self.assertEqual(pos_component.x, 0)
            self.assertEqual(pos_component.y, 0)

        self.world.event_bus.publish('update_time_step', timestep=1/60)

        for entity in entities:
            pos_component = entity.get_component(PositionComponent)
            self.assertEqual(pos_component.x, 10)
            self.assertEqual(pos_component.y, 10)

    def test_publish_event(self):
        # Trigger the event
        self.world.event_bus.publish('update_time_step', timestep=1/60)
        self.assertFalse(self.health_system.updated)

        input_component = self.world.get_singleton_component(InputComponent)
        input_component.clicked = True
        
        self.world.event_bus.publish('update_time_step', timestep=1/60)
        self.assertTrue(self.health_system.updated)

    def test_get_component_pools(self):
        required_component_pools = self.pos_system.get_component_pools()
        self.assertTrue(any(component_pool.component_type in self.pos_system.required_components for component_pool in required_component_pools))

    def test_get_singleton_component(self):
        singleton_component = self.pos_system.get_singleton_component(InputComponent)
        self.assertIsInstance(singleton_component, InputComponent)

    def test_get_entity(self):
        entity = self.world.create_entity()
        expected_entity = self.pos_system.get_entity(entity.id)
        self.assertEqual(entity, expected_entity)

    def test_get_required_entities(self):
        entity_1 = self.world.create_entity([PositionComponent(0,0)])
        entity_2 = self.world.create_entity([HealthComponent(100)])
        entities = self.pos_system.get_required_entities()
        self.assertIn(entity_1, entities)
        self.assertNotIn(entity_2, entities)        

class TestEcsAdmin(unittest.TestCase):
    def setUp(self) -> None:
        self.world = World(1400)
        self.world.add_singleton_component(InputComponent((0,0)))

    def test_initialization(self):
        self.assertEqual(self.world.max_entities, 1400)

        n_created_systems = len(self.world.systems)
        self.assertEqual(n_created_systems, 2)
        self.assertTrue(any(isinstance(item, PositionSystem) for item in self.world.systems))
        self.assertTrue(any(isinstance(item, HealthSystem) for item in self.world.systems))
    
    def test_create_component_pool(self):
        component_pool = self.world.create_component_pool(HealthComponent)
        self.assertIsInstance(component_pool,ComponentPool)
        expected_component_pools = {HealthComponent: component_pool}
        self.assertEqual(expected_component_pools, self.world.component_pools)

    def test_get_component_pool(self):
        expected_component_pool = self.world.create_component_pool(HealthComponent)
        component_pool = self.world.get_component_pool(HealthComponent)
        self.assertEqual(expected_component_pool, component_pool)

    def test_create_entity(self):
        entity_1 = self.world.create_entity()
        self.assertIsInstance(entity_1, Entity)
        self.assertEqual(self.world.entity_map[entity_1.id], entity_1)

        entity_2 = self.world.create_entity([HealthComponent(100)])
        self.assertTrue(entity_2.has_component(HealthComponent))

    def test_get_entity(self):
        expected_entity = self.world.create_entity()
        entity = self.world.get_entity(expected_entity.id)
        self.assertEqual(entity, expected_entity)

    def test_get_entity_error(self):
        entity = Entity()
        with self.assertRaises(KeyError):
            self.world.get_entity(entity)

    def test_attach_component(self):
        entity = Entity()
        component = HealthComponent(100)
        self.world.attach_component_to_entity(entity, component)

        health_component_pool = self.world.get_component_pool(HealthComponent)
        self.assertIsInstance(health_component_pool, ComponentPool)
        self.assertEqual(health_component_pool.component_type, HealthComponent)
        self.assertTrue(health_component_pool.contains_entity(entity))
         

if __name__ == '__main__':
    unittest.main()