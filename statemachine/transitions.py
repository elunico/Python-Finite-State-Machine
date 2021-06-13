from typing import Dict, Iterable


class TransitionMap(dict):
    def __init__(self, dct: Dict[str, Iterable[str]] = None):
        if dct is None:
            dct = {}
        if not (all(type(k) is str and all(type(i) is str for i in v) for (k, v) in dct.items())):
            raise TypeError("TransitionMap must be a Dict[str, Iterable[str]]")
        super(TransitionMap, self).__init__(dct)

    def add_transition(self, source: str, destination: str):
        if source in super(TransitionMap, self):
            super(TransitionMap, self)[source].add(destination)
        else:
            super(TransitionMap, self)[source] = [destination]