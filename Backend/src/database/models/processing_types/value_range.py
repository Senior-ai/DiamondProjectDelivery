from typing import NamedTuple, Optional


class ValueRange[T](NamedTuple):
    from_value: Optional[T]
    to_value: Optional[T]

    def is_valid(self) -> bool:
        return not (self.from_value is None and self.to_value is None)
