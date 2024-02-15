from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class itemBought(_message.Message):
    __slots__ = ("product_id", "quantity")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    quantity: int
    def __init__(self, product_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class soldItems(_message.Message):
    __slots__ = ("ip", "product_name", "category", "quantity", "description", "price_per_unit")
    class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ELECTRONICS: _ClassVar[soldItems.Category]
        FASHION: _ClassVar[soldItems.Category]
        OTHERS: _ClassVar[soldItems.Category]
    ELECTRONICS: soldItems.Category
    FASHION: soldItems.Category
    OTHERS: soldItems.Category
    IP_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_NAME_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_UNIT_FIELD_NUMBER: _ClassVar[int]
    ip: str
    product_name: str
    category: soldItems.Category
    quantity: int
    description: str
    price_per_unit: float
    def __init__(self, ip: _Optional[str] = ..., product_name: _Optional[str] = ..., category: _Optional[_Union[soldItems.Category, str]] = ..., quantity: _Optional[int] = ..., description: _Optional[str] = ..., price_per_unit: _Optional[float] = ...) -> None: ...

class displaySellerItem(_message.Message):
    __slots__ = ("item", "product_id", "rating")
    ITEM_FIELD_NUMBER: _ClassVar[int]
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    item: soldItems
    product_id: int
    rating: float
    def __init__(self, item: _Optional[_Union[soldItems, _Mapping]] = ..., product_id: _Optional[int] = ..., rating: _Optional[float] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
