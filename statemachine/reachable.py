import functools
from typing import Iterable

from statemachine import MachineError


def reachable(*, from_states: Iterable[str]):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            machine = self.machine
            machine._add_state(fn.__name__)
            [machine._add_state(i) for i in from_states]
            [machine._add_transition(i, fn.__name__) for i in from_states]
            if not any(i == machine.current_state for i in from_states):
                raise MachineError("No such move")
            machine.current_state = fn.__name__
            assert fn.__name__ in machine.states
            return fn(self, *args, **kwargs)

        return wrapper

    return decorator
