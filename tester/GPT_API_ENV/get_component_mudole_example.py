def get_numeric_type_example():
    s = '''Given the following **Background Information**:

```
binary types Types Number Types
Number types are encoded by a single byte.

\\begin{array}{llclll@{\\qquad\\qquad}l}
number type & numtype &::=&
  0x7F &\\Rightarrow& i32 \\\\ &&|&
  0x7E &\\Rightarrow& i64 \\\\ &&|&
  0x7D &\\Rightarrow& f32 \\\\ &&|&
  0x7C &\\Rightarrow& f64 \\\\
\\end{array}
```

### Expected JSON Response

The expected response should look like this:

```json
[
    {
        "number_type": [
            {
                "name": "number_type",
                "type": "<Union:i32:i64:f32:f64>",
                "description": "Represents a scalar numeric type, which can be one of `i32`, `i64`, `f32`, or `f64`."
            }
        ]
    },
    {
        "i32": [
            {
                "name": "i32",
                "type": "<Fix:7F:hex>",
                "description": "Represents the 32-bit integer type `i32`, encoded as the byte 0x7F."
            }
        ]
    },
    {
        "i64": [
            {
                "name": "i64",
                "type": "<Fix:7E:hex>",
                "description": "Represents the 64-bit integer type `i64`, encoded as the byte 0x7E."
            }
        ]
    },
    {
        "f32": [
            {
                "name": "f32",
                "type": "<Fix:7D:hex>",
                "description": "Represents the 32-bit floating-point type `f32`, encoded as the byte 0x7D."
            }
        ]
    },
    {
        "f64": [
            {
                "name": "f64",
                "type": "<Fix:7C:hex>",
                "description": "Represents the 64-bit floating-point type `f64`, encoded as the byte 0x7C."
            }
        ]
    }
]
```
'''