from random import randint
import struct
import leb128
import numpy as np


class value_holder:
    const_op = None
    def __init__(self, constant=None, type_str=None, generated_value=None, *args, **kwads):
        assert constant is not None or type_str is not None
        self.constant = constant
        self.type_str =type_str
        self.generated_value = generated_value

    @property
    def encode(self):
        raise ValueError('Have not implemented the method encode')

    def __repr__(self):
        fmt = '{}:{}:{}'
        type_str = '' if self.type_str is None else self.type_str
        constant = '' if self.constant is None else self.constant
        generated_value = '' if self.generated_value is None else self.generated_value
        return fmt.format(repr(type_str), repr(constant), repr(generated_value))

    def __hash__(self) -> int:
        return hash((self.type_str, repr(self.encode)))

    def __eq__(self, __o: object) -> bool:
        return hash(self) == hash(__o)

    @property
    def const_line(self):
        result = bytearray()
        if isinstance(self.const_op, int):
            result.append(self.const_op)
        else:
            assert isinstance(self.const_op, list)
            result.extend(self.const_op)
        result.extend(self.encode)
        return result


class i32_holder(value_holder):
    const_op = 65

    @property
    def encode(self):
        if self.generated_value is not None:
            return self.generated_value
        else:
            assert self.constant is not None
            # ! ，， type_str 
            # !  ，
            # ! 
            assert self.type_str == 'i32'
            # TODOunsigned int，uint
            return leb128.i.encode(self.constant)


class ref_null_holder(value_holder):
    const_op = 0xD0
    @property
    def encode(self):
        assert self.constant in [0x70, 0x6F]
        return bytearray([self.constant])


class i64_holder(value_holder):
    const_op = 66

    @property
    def encode(self):
        if self.generated_value is not None:
            return self.generated_value
        else:
            assert self.constant is not None
            assert self.type_str == 'i64'
            # TODOunsigned int，uint
            return leb128.i.encode(self.constant)


class f32_holder(value_holder):
    const_op = 67

    @property
    def encode(self):
        if self.generated_value is not None:
            return self.generated_value
        else:
            assert self.constant is not None
            assert self.type_str == 'f32'
            return bytearray(struct.pack('<f', self.constant))


class f64_holder(value_holder):
    const_op = 68

    @property
    def encode(self):
        if self.generated_value is not None:
            return self.generated_value
        else:
            assert self.constant is not None
            assert self.type_str == 'f64'
            return bytearray(struct.pack('<d', self.constant))


class v128_holder(value_holder):
    const_op = [0xfd, 12]
    def __init__(self, *args, **kwads):
        super().__init__(*args, **kwads)
        if self.generated_value is None:
            assert isinstance(self.constant, (list, int)), print(self.constant)
            if isinstance(self.constant, list):
                assert len(self.constant) == 16

    @property
    def encode(self):
        if self.generated_value is not None:
            return self.generated_value
        elif self.constant is not None and isinstance(self.constant, list):
            return bytearray([x for x in self.constant])
        elif self.constant is not None and isinstance(self.constant, int):
            return bytearray(int.to_bytes(self.constant, 16, byteorder='little'))
        else:
            raise ValueError('self.constant should not be none')


class ref_holder(value_holder):
    const_op = 0xD2  # ref.func
    @property
    def encode(self):
        if self.generated_value is not None:
            return self.generated_value
        elif self.constant is not None:
            return leb128.u.encode(self.constant)
        else:
            raise ValueError('self.constant should not be none')
