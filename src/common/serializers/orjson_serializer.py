"""
OrJSON serializer for fast JSON encoding/decoding.

OrJSON is significantly faster than standard json module
and supports more Python types out of the box.
"""

import orjson
from typing import Any, Union


class OrjsonSerializer:
    """
    Fast JSON serializer using orjson library.
    
    Features:
    - 2-3x faster than standard json
    - Native support for datetime, UUID, dataclass, numpy types
    - Produces compact output
    - Thread-safe
    """

    @staticmethod
    def dumps(obj: Any) -> bytes:
        """
        Serialize object to JSON bytes.
        
        Args:
            obj: Python object to serialize
            
        Returns:
            bytes: JSON encoded as bytes
            
        Example:
            >>> serializer = OrjsonSerializer()
            >>> serializer.dumps({"hello": "world"})
            b'{"hello":"world"}'
        """
        return orjson.dumps(obj)

    @staticmethod
    def loads(data: Union[bytes, str]) -> Any:
        """
        Deserialize JSON bytes/string to Python object.
        
        Args:
            data: JSON as bytes or string
            
        Returns:
            Python object
            
        Example:
            >>> serializer = OrjsonSerializer()
            >>> serializer.loads(b'{"hello":"world"}')
            {'hello': 'world'}
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return orjson.loads(data)

    @staticmethod
    def dumps_str(obj: Any) -> str:
        """
        Serialize object to JSON string (not bytes).
        
        Args:
            obj: Python object to serialize
            
        Returns:
            str: JSON encoded as string
            
        Example:
            >>> serializer = OrjsonSerializer()
            >>> serializer.dumps_str({"hello": "world"})
            '{"hello":"world"}'
        """
        return orjson.dumps(obj).decode('utf-8')
