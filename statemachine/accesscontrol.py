import functools
from typing import Iterable

from statemachine.machineerror import MachineError


def allows_access(*, from_states: Iterable[str] = None, to_states: Iterable[str] = None):
    if to_states is None:
        to_states = []

    if from_states is None:
        from_states = []

    def decorator(fn):
        def do_instance(self):
            machine = self.machine
            machine._add_state(fn.__name__)
            [machine._add_state(i) for i in from_states]
            [machine._add_state(i) for i in to_states]
            [machine._add_transition(i, fn.__name__) for i in from_states]
            [machine._add_transition(fn.__name__, i) for i in to_states]

        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            machine = self.machine
            if not any(i == machine.current_state for i in from_states) \
                    and not any(i == fn.__name__ for i in machine.transitions[machine.current_state]):
                raise MachineError(f"Transition from state {machine.current_state!r} to {fn.__name__!r} is illegal")
            machine.current_state = fn.__name__
            assert fn.__name__ in machine.states
            return fn(self, *args, **kwargs)

        setattr(wrapper, '_machine_do_init_steps', do_instance)
        return wrapper

    return decorator
