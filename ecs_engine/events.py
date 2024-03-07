from typing import Callable
from .interfaces import IEventBus

def subscribe_to_event(event_name):
    '''
    Decorator to mark a System method for subscription to a specific event.
    
    Args:
        event_name (str): The name of the event to subscribe to.
        
    Returns:
        The decorated function with an added '_event_subscriptions' attribute.
    '''
    def decorator(func):
        if not hasattr(func, '_event_subscriptions'):
            func._event_subscriptions = []
        func._event_subscriptions.append(event_name)
        return func
    return decorator

def subscribe_to_events(cls):
    '''
    Subscribes the system to events based on methods decorated with `subscribe_to_event`.
    '''
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and hasattr(attr, '_event_subscriptions'):
            for event_name in attr._event_subscriptions:
                cls.event_bus.subscribe(event_name, getattr(cls, attr_name))
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


