from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class buyer(_message.Message):
    __slots__ = ("name", "ip")
    NAME_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    name: str
    ip: str
    def __init__(self, name: _Optional[str] = ..., ip: _Optional[str] = ...) -> None: ...

class regSeller(_message.Message):
    __slots__ = ("uuid", "ip")
    UUID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    ip: str
    def __init__(self, uuid: _Optional[str] = ..., ip: _Optional[str] = ...) -> None: ...

class sellerMarketResponse(_message.Message):
    __slots__ = ("status", "product_id")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[sellerMarketResponse.Status]
        FAILED: _ClassVar[sellerMarketResponse.Status]
    SUCCESS: sellerMarketResponse.Status
    FAILED: sellerMarketResponse.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    status: sellerMarketResponse.Status
    product_id: int
    def __init__(self, status: _Optional[_Union[sellerMarketResponse.Status, str]] = ..., product_id: _Optional[int] = ...) -> None: ...

class soldItem(_message.Message):
    __slots__ = ("ip", "product_name", "category", "quantity", "description", "price_per_unit")
    class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ELECTRONICS: _ClassVar[soldItem.Category]
        FASHION: _ClassVar[soldItem.Category]
        OTHERS: _ClassVar[soldItem.Category]
    ELECTRONICS: soldItem.Category
    FASHION: soldItem.Category
    OTHERS: soldItem.Category
    IP_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    product_name: str
    category: soldItem.Category
    quantity: int
    description: str
    price_per_unit: float
    def __init__(self, ip: _Optional[str] = ..., product_name: _Optional[str] = ..., category: _Optional[_Union[soldItem.Category, str]] = ..., quantity: _Optional[int] = ..., description: _Optional[str] = ..., price_per_unit: _Optional[float] = ...) -> None: ...

class sellItem(_message.Message):
    __slots__ = ("item", "uuid")
    ITEM_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    item: soldItem
    uuid: str
    def __init__(self, item: _Optional[_Union[soldItem, _Mapping]] = ..., uuid: _Optional[str] = ...) -> None: ...

class updateItem(_message.Message):
    __slots__ = ("product_id", "uuid", "ip", "quantity", "price_per_unit")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    uuid: str
    ip: str
    quantity: int
    price_per_unit: float
    def __init__(self, product_id: _Optional[int] = ..., uuid: _Optional[str] = ..., ip: _Optional[str] = ..., quantity: _Optional[int] = ..., price_per_unit: _Optional[float] = ...) -> None: ...

class delete(_message.Message):
    __slots__ = ("product_id", "uuid", "ip")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    uuid: str
    ip: str
    def __init__(self, product_id: _Optional[int] = ..., uuid: _Optional[str] = ..., ip: _Optional[str] = ...) -> None: ...

class requestDisplayItems(_message.Message):
    __slots__ = ("uuid", "ip")
    UUID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    ip: str
    def __init__(self, uuid: _Optional[str] = ..., ip: _Optional[str] = ...) -> None: ...

class displaySellerItems(_message.Message):
    __slots__ = ("item", "product_id", "rating")
    ITEM_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    item: _containers.RepeatedCompositeFieldContainer[soldItem]
    product_id: _containers.RepeatedScalarFieldContainer[int]
    rating: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, item: _Optional[_Iterable[_Union[soldItem, _Mapping]]] = ..., product_id: _Optional[_Iterable[int]] = ..., rating: _Optional[_Iterable[float]] = ...) -> None: ...

class reqSearch(_message.Message):
    __slots__ = ("name", "category")
    class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ELECTRONICS: _ClassVar[reqSearch.Category]
        FASHION: _ClassVar[reqSearch.Category]
        OTHERS: _ClassVar[reqSearch.Category]
        ANY: _ClassVar[reqSearch.Category]
    ELECTRONICS: reqSearch.Category
    FASHION: reqSearch.Category
    OTHERS: reqSearch.Category
    ANY: reqSearch.Category
    NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    name: str
    category: reqSearch.Category
    def __init__(self, name: _Optional[str] = ..., category: _Optional[_Union[reqSearch.Category, str]] = ...) -> None: ...

class BuyItem(_message.Message):
    __slots__ = ("quantity", "product_id", "ip")
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    product_id: int
    ip: str
    def __init__(self, quantity: _Optional[int] = ..., product_id: _Optional[int] = ..., ip: _Optional[str] = ...) -> None: ...

class wishlist(_message.Message):
    __slots__ = ("product_id", "ip")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    ip: str
    def __init__(self, product_id: _Optional[int] = ..., ip: _Optional[str] = ...) -> None: ...

class rate(_message.Message):
    __slots__ = ("rating", "product_id", "ip")
    RATING_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    rating: int
    product_id: int
    ip: str
    def __init__(self, rating: _Optional[int] = ..., product_id: _Optional[int] = ..., ip: _Optional[str] = ...) -> None: ...
