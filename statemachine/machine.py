from typing import Set, Dict

from statemachine.transitions import TransitionMap


def Machine(*, init_state: str):
    class _Machine:
        def __init__(self, cls):
            old_new = getattr(cls, '__new__')
            old_init = getattr(cls, '__init__')

            conflict_msg = 'Class {!r} has member `{!r}` which is overwritten by Machine. ' \
                           f'Rename this method to something else to use @Machine'

            for i in ['find_all_states', 'machine', 'get_all_states']:
                if hasattr(cls, i):
                    raise TypeError(conflict_msg.format(repr(cls.__name__), repr(i)))

            def __new__(*args, **kwargs):
                instance = old_new(cls)
                setattr(instance, 'machine', self)
                return instance

            def __init__(cls_self, *args, **kwargs):
                for k in dir(cls_self):
                    v = getattr(cls_self, k)
                    if hasattr(v, '_machine_do_init_steps'):
                        v._machine_do_init_steps(cls_self)
                old_init(cls_self, *args, **kwargs)

            def get_all_states(cls_self, source: str) -> Dict[str, Set[str]]:
                return {'to_states': set(self.transitions[source]), 'from_states': set(self.rtransitions[source])}

            setattr(cls, '__new__', __new__)
            setattr(cls, '__init__', __init__)
            setattr(cls, 'get_all_states', get_all_states)
            self.current_state = init_state
            self.states: Set[str] = set()
            self.transitions: TransitionMap = TransitionMap()
            self.rtransitions: TransitionMap = TransitionMap()

        def _add_state(self, state: str):
            if not state in self.states:
                self.states.add(state)

        def _add_transition(self, source: str, destination: str):
            if source not in self.states or destination not in self.states:
                raise ValueError(f'Transition contains states which the machine does not know about')
            st = self.transitions.get(source, set())
            st.add(destination)
            self.transitions[source] = st

            # reverse transition map for lookup
            rst = self.rtransitions.get(destination, set())
            rst.add(source)
            self.rtransitions[destination] = rst

    def decorator(cls):
        setattr(cls, 'machine', _Machine(cls))
        return cls

    return decorator
