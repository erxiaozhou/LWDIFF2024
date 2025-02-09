The test cases can trigger the bugs in the runtimes speficied in [runtime_info](../runtime_info/README.md).
Each `case` with Id `n` is the file `n.wasm` under this folder. 

| Case Id     |  Runtime    |   Root Cause   |
| ----| ---- | ---- | 
| 1  | WAMR-JIT    |  Fail to detect a test case with illegal opcode.    |
|  2    | All WAMR     |  Fail to drop the active segments before executing the function.    |
|  3    |  WAMR-FINTERP    | A bug in stack implementation     |
|  4   | WAMR-FINTERP    | A flaw in optimization  |
|  5   |WAMR-FINTERP | A bug in handling control flow     |
|  6   |WAMR-FINTERP| A bug in the implementation of local.set     |
|  7   |WAMR-JIT | A bug in processing reference value     |
|  8   | WAMR-FINTERP| A bug in coping an i64-bit variable  |
|  9   |WAMR-FINTERP| A bug in handling control flow  |
| 10   |WAMR-FJIT / WAMR-MJIT  | A bug in the implementation of table.init |
|   11   |WAMR-FJIT / WAMR-MJIT | A bug in processing operands of type i64     |
|  12 | All WAMR| A bug in validate ref.func     |
|  13  |WAMR-FINTERP| A bug in the implementation of ref.is-null     |
|  14  |WAMR-FINTERP |A bug in handling control flow  |
|  15  |WAMR-FINTERP |A bug in handling control flow    |
|  16  |WAMR-FINTERP |A bug in handling control flow  |
| 17 | WAMR-JIT    |  Fail to detect a test case with illegal opcode.    |
|  18  |WasmEdge| Fail to detect a test case with illegal opcode.  |
|  19  |  All WAMR    | A bug in validation     |
|  20  |WAMR-FINTERP |A bug in handling control flow |
|  21  |  All WAMR | A bug in handling control flow     |
|  22  |All WAMR| A bug in validting the control flow     |
|  23  |WAMR-FINTERP|A bug in handling control flow |
|  24  |WAMR-FINTERP|A bug in handling control flow |
|  25  |WAMR-FINTERP|A bug in handling control flow|
|  26  |WAMR-JIT / WAMR-MJIT|Incorrect default value for local variable  |
|  27  |WAMR-FINTERP | A bug in processing local     |
|  28  | All WAMR|A bug in decoding the string|
|  29  |WasmEdge|Fail to detect a test case with an illegally encoded local variable|
|  30  |WAMR-FINTERP| A bug in handling control flow     |
|  31  | All WAMR | Fail to detect invalid data count section  |
