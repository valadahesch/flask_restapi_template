from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserPermission(_message.Message):
    __slots__ = ("user_id", "permission")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    permission: str
    def __init__(self, user_id: _Optional[str] = ..., permission: _Optional[str] = ...) -> None: ...

class UserRole(_message.Message):
    __slots__ = ("user_id", "role_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    role_id: str
    def __init__(self, user_id: _Optional[str] = ..., role_id: _Optional[str] = ...) -> None: ...

class Rule(_message.Message):
    __slots__ = ("rule",)
    RULE_FIELD_NUMBER: _ClassVar[int]
    rule: str
    def __init__(self, rule: _Optional[str] = ...) -> None: ...

class RoleId(_message.Message):
    __slots__ = ("role_id",)
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    role_id: str
    def __init__(self, role_id: _Optional[str] = ...) -> None: ...

class UserId(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class EmptyResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class VerifyResult(_message.Message):
    __slots__ = ("verify_result",)
    VERIFY_RESULT_FIELD_NUMBER: _ClassVar[int]
    verify_result: bool
    def __init__(self, verify_result: bool = ...) -> None: ...

class PermissionResponse(_message.Message):
    __slots__ = ("row",)
    class Row(_message.Message):
        __slots__ = ("items",)
        ITEMS_FIELD_NUMBER: _ClassVar[int]
        items: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, items: _Optional[_Iterable[str]] = ...) -> None: ...
    ROW_FIELD_NUMBER: _ClassVar[int]
    row: _containers.RepeatedCompositeFieldContainer[PermissionResponse.Row]
    def __init__(self, row: _Optional[_Iterable[_Union[PermissionResponse.Row, _Mapping]]] = ...) -> None: ...

class StringList(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, items: _Optional[_Iterable[str]] = ...) -> None: ...
