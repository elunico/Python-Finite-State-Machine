from typing import Set

from statemachine.transitions import TransitionMap


def Machine(*, init_state: str):
    class _Machine:
        def __init__(self, cls):
            old_new = getattr(cls, '__new__')

            if hasattr(cls, 'find_all_states'):
                raise TypeError(f'Class {cls.__name__!r} has member `find_all_states` which is overwritten by Machine. '
                                f'Rename this method to something else to use @Machine')

            def __new__(*args, **kwargs):
                instance = old_new(cls)
                setattr(instance, 'machine', self)
                return instance

            def find_all_states(self1, source: str) -> Set[str]:
                return set(self.transitions[source])

            setattr(cls, '__new__', __new__)
            setattr(cls, 'find_all_states', find_all_states)
            self.current_state = init_state
            self.states: Set[str] = set()
            self.transitions: TransitionMap = TransitionMap()

        def _add_state(self, state: str):
            if not state in self.states:
                self.states.add(state)

        def _add_transition(self, source: str, destination: str):
            if source not in self.states or destination not in self.states:
                raise ValueError(f'Transition contains states which the machine does not know about')
            st = self.transitions.get(source, set())
            st.add(destination)
            self.transitions[source] = st

    def decorator(cls):
        setattr(cls, 'machine', _Machine(cls))
        return cls

    return decorator
