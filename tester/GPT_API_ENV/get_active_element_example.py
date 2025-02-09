def get_active_element_example():
    s = '''Given the following **Background Information**:

```
Given the quesiton is "What is the definition of the active element segment" and the background information is as follows:

\\begin{array}{llclll}
element section & elemsec &::=&
  seg^\\ast:section_9(vec(elem)) &\\Rightarrow& seg^\\ast \\\\
element segment & elem &::=&
  0:u32~~e:expr~~y^\\ast:vec(funcidx)
    &\\Rightarrow& \\\\&&&\\quad
    \\{ type~funcref, init~((ref{.func}~y)~end)^\\ast, mode~active~\\{ table~0, offset~e \\} \\} \\\\ &&|&
  1:u32~~et:elemkind~~y^\\ast:vec(funcidx)
    &\\Rightarrow& \\\\&&&\\quad
    \\{ type~et, init~((ref{.func}~y)~end)^\\ast, mode~passive \\} \\\\ &&|&
  2:u32~~x:tableidx~~e:expr~~et:elemkind~~y^\\ast:vec(funcidx)
    &\\Rightarrow& \\\\&&&\\quad
    \\{ type~et, init~((ref{.func}~y)~end)^\\ast, mode~active~\\{ table~x, offset~e \\} \\} \\\\ &&|&
  3:u32~~et:elemkind~~y^\\ast:vec(funcidx)
    &\\Rightarrow& \\\\&&&\\quad
    \\{ type~et, init~((ref{.func}~y)~end)^\\ast, mode~declarative \\} \\\\ &&|&
  4:u32~~e:expr~~el^\\ast:vec(expr)
    &\\Rightarrow& \\\\&&&\\quad
    \\{ type~funcref, init~el^\\ast, mode~active~\\{ table~0, offset~e \\} \\} \\\\ &&|&
  5:u32~~et:reftype~~el^\\ast:vec(expr)
    &\\Rightarrow& \\\\&&&\\quad
    \\{ type~et, init~el^\\ast, mode~passive \\} \\\\ &&|&
  6:u32~~x:tableidx~~e:expr~~et:reftype~~el^\\ast:vec(expr)
    &\\Rightarrow& \\\\&&&\\quad
    \\{ type~et, init~el^\\ast, mode~active~\\{ table~x, offset~e \\} \\} \\\\ &&|&
  7:u32~~et:reftype~~el^\\ast:vec(expr)
    &\\Rightarrow& \\\\&&&\\quad
    \\{ type~et, init~el^\\ast, mode~declarative \\} \\\\
element kind & elemkind &::=&
  0x00 &\\Rightarrow& funcref \\\\
\\end{array}


The expected response should look like this:

```json
[
    {
        "active_element_segment": [
            {
                "name": "segment",
                "type": "<Union:active_segment_implicit:active_segment_explicit:active_segment_expr_implicit:active_segment_expr_explicit>",
                "description": "Represents an element segment, which can be active, passive, or declarative, with variations based on the use of table index, element kind, and element initialization data."
            }
        ]
    },
    {
        "active_segment_implicit": [
            {
                "name": "bitfield",
                "type": "<Fix:0:u32>",
                "description": "An integer indicating an active element segment with an implicit table index (default table = 0)."
            },
            {
                "name": "offset",
                "type": "expr",
                "description": "An expression that calculates the starting offset in the table where the elements are initialized."
            },
            {
                "name": "init",
                "type": "<Vec:funcidx>",
                "description": "A vector of function indices used to initialize the table starting at the calculated offset."
            }
        ]
    },
    {
        "active_segment_explicit": [
            {
                "name": "bitfield",
                "type": "<Fix:2:u32>",
                "description": "An integer indicating an active element segment with an explicit table index."
            },
            {
                "name": "table",
                "type": "tableidx",
                "description": "The table index explicitly specified for this segment."
            },
            {
                "name": "offset",
                "type": "expr",
                "description": "An expression that calculates the starting offset in the table where the elements are initialized."
            },
            {
                "name": "init",
                "type": "<Vec:funcidx>",
                "description": "A vector of function indices used to initialize the table starting at the calculated offset."
            }
        ]
    },
    {
        "active_segment_expr_implicit": [
            {
                "name": "bitfield",
                "type": "<Fix:4:u32>",
                "description": "An integer indicating an active element segment with an implicit table index (default table = 0) and element expressions."
            },
            {
                "name": "offset",
                "type": "expr",
                "description": "An expression that calculates the starting offset in the table where the elements are initialized."
            },
            {
                "name": "init",
                "type": "<Vec:expr>",
                "description": "A vector of expressions used to initialize the table starting at the calculated offset."
            }
        ]
    },
    {
        "active_segment_expr_explicit": [
            {
                "name": "bitfield",
                "type": "<Fix:6:u32>",
                "description": "An integer indicating an active element segment with an explicit table index and element expressions."
            },
            {
                "name": "table",
                "type": "tableidx",
                "description": "The table index explicitly specified for this segment."
            },
            {
                "name": "offset",
                "type": "expr",
                "description": "An expression that calculates the starting offset in the table where the elements are initialized."
            },
            {
                "name": "init",
                "type": "<Vec:expr>",
                "description": "A vector of expressions used to initialize the table starting at the calculated offset."
            }
        ]
    },
    {
        "elemkind": [
            {
                "name": "value",
                "type": "<Fix:0x00:hex>",
                "description": "Indicates the element kind `funcref`."
            }
        ]
    }
]


```
'''