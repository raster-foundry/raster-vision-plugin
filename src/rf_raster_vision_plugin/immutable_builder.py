from copy import deepcopy
from typing import List, TypeVar


class ImmutableBuilder(object):

    _properties = []  # type: List[str]
    T = TypeVar("T")

    def with_property(self, property_name: str, property_value: T):
        b = deepcopy(self)
        setattr(b, property_name, property_value)
        return b

    @property
    def config(self):
        return {
            k: getattr(self, k)
            for k in self._properties
            if getattr(self, k, None) is not None
        }
