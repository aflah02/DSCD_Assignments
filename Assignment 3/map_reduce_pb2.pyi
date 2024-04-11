from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MapDataRequest(_message.Message):
    __slots__ = ("input_split", "centroids")
    INPUT_SPLIT_FIELD_NUMBER: _ClassVar[int]
    CENTROIDS_FIELD_NUMBER: _ClassVar[int]
    input_split: _containers.RepeatedScalarFieldContainer[float]
    centroids: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, input_split: _Optional[_Iterable[float]] = ..., centroids: _Optional[_Iterable[float]] = ...) -> None: ...

class MapDataResponse(_message.Message):
    __slots__ = ("pairs",)
    PAIRS_FIELD_NUMBER: _ClassVar[int]
    pairs: _containers.RepeatedCompositeFieldContainer[KeyValue]
    def __init__(self, pairs: _Optional[_Iterable[_Union[KeyValue, _Mapping]]] = ...) -> None: ...

class ReduceDataRequest(_message.Message):
    __slots__ = ("reducers",)
    REDUCERS_FIELD_NUMBER: _ClassVar[int]
    reducers: int
    def __init__(self, reducers: _Optional[int] = ...) -> None: ...

class ReduceDataResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class MapperDataRequest(_message.Message):
    __slots__ = ("mapper_id",)
    MAPPER_ID_FIELD_NUMBER: _ClassVar[int]
    mapper_id: int
    def __init__(self, mapper_id: _Optional[int] = ...) -> None: ...

class MapperDataResponse(_message.Message):
    __slots__ = ("data_points",)
    DATA_POINTS_FIELD_NUMBER: _ClassVar[int]
    data_points: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, data_points: _Optional[_Iterable[float]] = ...) -> None: ...

class DataPointRequest(_message.Message):
    __slots__ = ("data_point",)
    DATA_POINT_FIELD_NUMBER: _ClassVar[int]
    data_point: float
    def __init__(self, data_point: _Optional[float] = ...) -> None: ...

class DataPointResponse(_message.Message):
    __slots__ = ("centroid_index",)
    CENTROID_INDEX_FIELD_NUMBER: _ClassVar[int]
    centroid_index: int
    def __init__(self, centroid_index: _Optional[int] = ...) -> None: ...

class PartitionRequest(_message.Message):
    __slots__ = ("reducer_id", "pairs")
    REDUCER_ID_FIELD_NUMBER: _ClassVar[int]
    PAIRS_FIELD_NUMBER: _ClassVar[int]
    reducer_id: int
    pairs: _containers.RepeatedCompositeFieldContainer[KeyValue]
    def __init__(self, reducer_id: _Optional[int] = ..., pairs: _Optional[_Iterable[_Union[KeyValue, _Mapping]]] = ...) -> None: ...

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
