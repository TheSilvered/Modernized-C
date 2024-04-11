from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto


class NCMut(Enum):
    READONLY = auto()
    WRITEONLY = auto()
    READWRITE = auto()


class NCTypeError(Exception):
    pass


class NCType(ABC):
    def __init__(self, mut: NCMut):
        self.read = False
        self.write = False
        if mut == NCMut.READONLY:
            self.read = True
        elif mut == NCMut.WRITEONLY:
            self.write = True
        elif mut == NCMut.READWRITE:
            self.read = True
            self.write = True
        else:
            raise NCTypeError("invalid type mutability")

    @abstractmethod
    def var_c_type(self) -> str:
        pass

    @abstractmethod
    def decl_c_type(self) -> str:
        pass

    @abstractmethod
    def ret_c_type(self) -> str:
        pass

    @abstractmethod
    def compatible(self, other: NCType) -> bool:
        pass

    @abstractmethod
    def exact(self, other: NCType) -> bool:
        pass


class NCBaseType(NCType, ABC):
    def __init__(self, signed: bool, byte_size: int, mut: NCMut):
        super().__init__(mut)
        self.signed = signed
        self.byte_size = byte_size

        if (byte_size & (byte_size - 1)) != 0 or byte_size <= 0:
            raise NCTypeError("byte_size is not a power of 2")

    @abstractmethod
    def c_type(self) -> str:
        pass

    def var_c_type(self) -> str:
        if self.write and not self.read:
            raise NCTypeError("write-only type used in variable declaration")

        c_str = ""
        if not self.write:
            c_str += "const "
        c_str += self.c_type()
        return c_str

    def ret_c_type(self) -> str:
        if self.write:
            raise NCTypeError("writable type used as return type")
        return self.c_type()

    def decl_c_type(self) -> str:
        c_str = self.c_type()
        if self.write:
            c_str += "*"
        else:
            c_str = "const " + c_str
        return c_str

    def exact(self, other: NCType) -> bool:
        if type(self) is type(other):
            other: NCBaseType
            return self.byte_size == other.byte_size \
                and self.signed == other.signed
        return False

    def compatible(self, other: NCType) -> bool:
        if type(self) is not type(other):
            return False
        other: NCBaseType
        if self.signed != other.signed:
            return False
        return self.byte_size <= other.byte_size


class NCInt(NCBaseType):
    def __init__(self, signed: bool, byte_size: int, mut: NCMut):
        super().__init__(signed, byte_size, mut)
        if self.byte_size not in (1, 2, 4, 8):
            raise NCTypeError(f"invalid byte size of {self.byte_size} bytes for int")

    def c_type(self) -> str:
        match self.byte_size:
            case 1: return "char"
            case 2: return "short"
            case 4: return "int"
            case 8: return "long long"


class NCFloat(NCBaseType):
    def __init__(self, signed: bool, byte_size: int, mut: NCMut):
        super().__init__(signed, byte_size, mut)
        if self.byte_size not in (4, 8):
            raise NCTypeError(f"invalid byte size of {self.byte_size} bytes for int")

    def c_type(self) -> str:
        match self.byte_size:
            case 4: return "float"
            case 8: return "double"
