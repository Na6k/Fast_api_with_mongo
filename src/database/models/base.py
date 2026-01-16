from typing import Any, Dict, TypeVar, Mapping
from pydantic import BaseModel
ModelType = TypeVar("ModelType", bound="Base", covariant=True)


class Base(BaseModel):
    """
    Base class for MongoDB document models.  Provides common functionality such
    as converting the object to a dictionary.
    """
    def __repr__(self) -> str:
        """
        Provides a string representation of the object.
        """
        params = ", ".join(
            f"{attr}={value!r}"
            for attr, value in self.__dict__.items()
            if not attr.startswith("_")
        )
        return f"{type(self).__name__}({params})"

    def as_dict(self) -> Dict[str, Any]:
        """
        Converts the object to a dictionary.  Handles nested Base objects and lists/tuples of Base objects.
        """
        result: Dict[str, Any] = {}
        for attr, value in self.__dict__.items():
            if attr.startswith("_"):
                continue
            if isinstance(value, Base):
                result[attr] = value.as_dict()
            elif isinstance(value, (list, tuple)):
                result[attr] = type(value)(
                    v.as_dict() if isinstance(v, Base) else v for v in value
                )
            else:
                result[attr] = value

        return result