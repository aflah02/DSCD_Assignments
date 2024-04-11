from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MapDataRequest(_message.Message):
    __slots__ = ("mapper_id", "ip")
    MAPPER_ID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    mapper_id: int
    ip: str
    def __init__(self, mapper_id: _Optional[int] = ..., ip: _Optional[str] = ...) -> None: ...

class MapDataResponse(_message.Message):
    __slots__ = ("input_split", "centroids", "input_path")
    INPUT_SPLIT_FIELD_NUMBER: _ClassVar[int]
    CENTROIDS_FIELD_NUMBER: _ClassVar[int]
    INPUT_PATH_FIELD_NUMBER: _ClassVar[int]
    input_split: _containers.RepeatedScalarFieldContainer[int]
    centroids: _containers.RepeatedCompositeFieldContainer[Point]
    input_path: str
    def __init__(self, input_split: _Optional[_Iterable[int]] = ..., centroids: _Optional[_Iterable[_Union[Point, _Mapping]]] = ..., input_path: _Optional[str] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ("x", "y")
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: float
    y: float
    def __init__(self, x: _Optional[float] = ..., y: _Optional[float] = ...) -> None: ...

class ReduceDataRequest(_message.Message):
    __slots__ = ("reducers", "ip")
    REDUCERS_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    reducers: int
    ip: str
    def __init__(self, reducers: _Optional[int] = ..., ip: _Optional[str] = ...) -> None: ...

class ReduceDataResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class MapperDataRequest(_message.Message):
    __slots__ = ("mapper_id", "ip")
    MAPPER_ID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    mapper_id: int
    ip: str
    def __init__(self, mapper_id: _Optional[int] = ..., ip: _Optional[str] = ...) -> None: ...

class MapperDataResponse(_message.Message):
    __slots__ = ("data_points",)
    DATA_POINTS_FIELD_NUMBER: _ClassVar[int]
    data_points: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, data_points: _Optional[_Iterable[float]] = ...) -> None: ...

class DataPointRequest(_message.Message):
    __slots__ = ("data_point", "ip")
    DATA_POINT_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    data_point: float
    ip: str
    def __init__(self, data_point: _Optional[float] = ..., ip: _Optional[str] = ...) -> None: ...

class DataPointResponse(_message.Message):
    __slots__ = ("centroid_index",)
    CENTROID_INDEX_FIELD_NUMBER: _ClassVar[int]
    centroid_index: int
    def __init__(self, centroid_index: _Optional[int] = ...) -> None: ...

class PartitionRequest(_message.Message):
    __slots__ = ("reducer_id", "pairs", "ip")
    REDUCER_ID_FIELD_NUMBER: _ClassVar[int]
    PAIRS_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    reducer_id: int
    pairs: _containers.RepeatedCompositeFieldContainer[KeyValue]
    ip: str
    def __init__(self, reducer_id: _Optional[int] = ..., pairs: _Optional[_Iterable[_Union[KeyValue, _Mapping]]] = ..., ip: _Optional[str] = ...) -> None: ...

class PartitionResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class KeyValue(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: float
    value: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, key: _Optional[float] = ..., value: _Optional[_Iterable[float]] = ...) -> None: ...
