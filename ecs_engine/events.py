from typing import Callable
from .interfaces import IEventBus

class EventBus(IEventBus):
    '''
    Implements a simple event bus for an event-driven architecture, facilitating communication
    between different parts of the application through events.

    The EventBus allows components to subscribe to specific events and be notified when those
    events are published. This decouples the event publishers from the subscribers, improving
    modularity and flexibility.

    Attributes:
        events (dict[str, list[Callable]]): A dictionary mapping event names to lists of callback functions
        (subscribers) that should be invoked when the event is published.
    '''
    def __init__(self):
        self.events: dict[str, list[Callable]] = {} # event_names : listeners

    def register_event(self, event_name: str):
        '''
        Registers a new event type in the event bus. Each event type is identified by a unique name.

        Args:
            event_name (str): The unique name of the event to register.

        Raises:
            KeyError: If the event_name already exists in the events dictionary.
        '''
        if event_name in self.events:
            raise KeyError(f'{event_name} already exists as an event.')
        self.events[event_name] = []

    def subscribe(self, event_name: str, callback: Callable):
        '''
        Subscribes a callback function to a specific event type. The callback will be invoked
        when the event is published.

        Args:
            event_name (str): The name of the event to subscribe to.
            callback (Callable): The callback function that should be invoked when the event is published.
        '''
        self.events[event_name].append(callback)

    def publish(self, event_name: str, **kwargs):      
        '''
        Publishes an event of a specific type, invoking all subscribed callback functions.

        Args:
            event_name (str): The name of the event to publish.
            **kwargs: Arbitrary keyword arguments that will be passed to the callback functions.

        Raises:
            KeyError: If the event_name does not exist in the events dictionary.
        '''  
        for callback in self.events[event_name]:
            callback(**kwargs)


