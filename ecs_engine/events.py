from typing import Callable
from .interfaces import IEventBus

class EventBus(IEventBus):
    def __init__(self):
        self.events: dict[str, list[Callable]] = {} # event_names : listeners

    def register_event(self, event_name: str):
        if event_name in self.events:
            raise KeyError(f'{event_name} already exists as an event.')
        self.events[event_name] = []

    def subscribe(self, event_name: str, callback: Callable):
        self.events[event_name].append(callback)

    def publish(self, event_name: str, **kwargs):        
        for callback in self.events[event_name]:
            callback(**kwargs)


