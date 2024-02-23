# ECS Engine
This ECS Engine is a lightweight and dependancyless "Entity Component System" (ECS). ECSs are architectures that are most commonly used in video game because it allows you to manage a lot of concurrent states (components) and mutate these states efficently (systems).  

## Getting Started
### Prerequisites
* Python 3.6 or newers
  
### Installation
To install this ECS Engine: 
```
pip install ecs-engine==0.1
```

### Features
* **Entity, Components, System, and Admin**: Includes all of the features needed for a baseline ECS.
* **Singleton Component**: A singleton component to manage singular state that is used by 1 or more systems but not owned by any entities. Check out the [GDC talk by Overwatch's Tim Ford](https://www.youtube.com/watch?v=W3aieHjyNvw) for more info.
* **Component Pool**: An Object Pool for fast and efficient component creation. As well as using a "Sparse Set" data structure to improve entity caching and entity querying. [More on the Sparse Set here](https://stackoverflow.com/questions/23721645/designs-of-an-entity-component-system).

  <sub>It is worth noting that the sparse set will increase memory overhead in exchange for performance.<sub>
* **EventBus**: An event bus to help provide system to system and admin to system communication.


### Quick start
Here is a quick example to get you started!
```
from ecs_engine import EcsAdmin, Entity, Component, SingletonComponent, System, subscribe_to_event
from dataclasses import dataclass

@dataclass
class PositionComponent(Component):
    x: int
    y: int

class UserComponent(Component):
  ...

@dataclass
class InputSingletonComponent(SingletonComponent):
    input: KEY_PRESS

class UserMovementSystem(System):
    required_components = [PositionComponent, UserComponent]

    @subscribe_to_event('update_time_step')
    def update(self, timestep: float):
        entities = self.get_required_entities()
        input_component = self.get_singleton_component(InputSingletonComponent)

        for entity in entities:
            if input_component.input == ['W']:
              position_component = entity.get_component(PositionComponent)
              position_component.y -= 1

class InputSystem(System):
    @subscribe_to_event('keyboard_input')
    def update(self, inputs):
        input_singleton_component = self.get_singleton_component(InputSingletonComponent)
        input_singleton_component.input = inputs

class World(EcsAdmin):
    init_systems = [UserMovementSystem]
    events = ['update_time_step', 'keyboard_input']

    def timestep(self, time_step: float):
        self.event_bus.publish('update_time_step', time_step)

    def input(self, inputs: list[KeyboardEvent]):
        self.event_bus.publish('keyboard_input', inputs)

# game loop
world = World()
world.add_singleton_component(InputComponent())
time_step = 1/TICK

while True:
    keyboard_input = get_input()
    world.input(keyboard_input)
    world.timestep(time_step)
    ...
            
```      
          
## Why use an ECS?
ECSs are considered highly performant and encourage decoupling. 

There are many reasons that ECS are consider highly performant:
* Caching Efficiency
* Batch Processing
* Object Pooling
* Parallelism (GIL :sweat_smile:)

Decoupling is a natural and comfortable thing within an ECS, so much so that even if you saw performance loss compared to pure OOP architectures I'd still prefer ECS as it reducing bugs and spaghetti. Because you're force to make everything either a component (data structure) or a system (procedure) then they're all interchangeable. If I every need a new system that for combat I don't have to go and change any previous systems, I can just take the components and mutate them in an additional way.

## Definitions
### Components
Components are simply data structures that are used by the systems and entities to convey information. These components are dumb data structures the only methods they include are for serialization and deserialization. 

Ex: You can have components to store infomration about position and health.
```
@dataclass
class PositionComponent(Component):
    def init(self, x, y):
        self.x = x
        self.y = y
```

### Entities
An 'Entity' is an object that has and id and components attached to it. These components make up the features of the entity and define what it is. Without components an Entity is literally just an id with no attrbitutes at all.

Ex: You want to create a character. So you create an Entity and attach the following components: Position, Sprite, Health, Attack
```
character = Entity()
character.add_component(PositionComponent)
character.add_component(SpriteComponent)
character.add_component(HealthComponent)
character.add_component(AttackComponent)
```

### Systems
Systems process groups of entities but they don't process the entity obj but rather the components attached the the entity. A system will typically query for all of the entities that have components the system works with and then mutates the components inside.

Ex: You have an attacking system where you deal 10 damage and heal 5
```
class AttackSystem(System):
    required_components = [AttackComponent]
  
    @subscribe_to_event('update_time_step')
    def update(self, timestep: float):
        entities = self.get_required_entities()
        for entity in entities:
            attack_component = entity.get_component(AttackComponent)
            entity_hit: Entity = self.check_collision_w_enemy(attack_component)
  
            if entity_hit:
                enemy_health_component = enemy_hit.get_component(HealthComponent)
                entity_health_component = entity.get_component(HealthComponent)
                enemy_health_component.health -= 10
                entity_health_component.health += 5
  
                self.event_bus.publish('check_for_death', opponent_hit)
```

### Events
While not always used in ECS systems; this engine here does use events and listeners to communicate between the Admin and System to System. These events could be as common as timesteps of timedeltas for new frames to events triggered by systems like setting off a tnt in the game world.

Ex: In the previous system example you get two exapmles of event system. The system is updated by the time_step that happens every frame in the game. At the end it publishes and event to alert any subscribers that this character may die.

## 
### Documentation
[Documentation can be found here](https://jsimerly.github.io/ecs_engine/). It's built using sphinx and everything in the documentation can be found in the comments of the source code.

### License 
ECS Engine is licensed under the MIT License
