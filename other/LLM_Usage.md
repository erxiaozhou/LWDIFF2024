# LLM Usage
## Pre-requisites
1. Build the docker container environment as described in [Tester Usage](#tester-usage)
2. Update the `api_key` and `base_url` in [api_util.py](./tester/GPT_API_ENV/api_util.py) for OPENAI API service.

## Generation
1. Generate the knowledge about the control flow construct grammar.
    ```
    python script_ask_cfg.py
    ```
2. Generate the knowledge about the module definitions.
    ```
    python script_ask_module_def.py
    ```
3. Generate the knowledge about the instructions.
    ```
    python script_ask_insts.py
    ```

## Details of LLM setup
Our implementation is built on GPT-4, accessed through the API.
We set the temperature parameter to zero. We justify the design choice to modulate the randomness and creativity of the LLM to mitigate the LLM’s hallucination problem.

To retrieve the specification knowledge for LLM, we build a knowledge retriever by parsing the Wasm specification with the help of Docutils. 

In our implementation, we combine the four instruction-related tasks into a single prompt, enabling the LLM to complete all tasks together. This approach avoids the inefficiency of using separate prompts, which would require repeatedly providing the same background information and wasting tokens.

We introduce how we use the knowledge at: [Knowledge Usage](./Knowledge_Usage.pdf).

## Prompt
- Prompt template for querying the binary format of a module definiiton: [binary_module_definition_prompt_template.txt](../tester/GPT_API_ENV/prompt_templates/binary_module_definition_prompt_template.txt). [An example](./tester/GPT_API_ENV/prompt_examples/query_memory_definition_binary_format_prompt.txt).

- Prompt template for querying the information about an instruction: [inst_prompt_template.txt](../tester/GPT_API_ENV/prompt_templates/inst_prompt_template.txt). [An example](../tester/GPT_API_ENV/prompt_examples/query_select_prompt.txt).

- Prompt template for querying the grammar describing the control flow constructs: [control_flow_construct_prompt_template.txt](../tester/GPT_API_ENV/prompt_templates/control_flow_construct_prompt_template.txt). [An example](../tester/GPT_API_ENV/prompt_examples/query_control_flow_construct_prompt.txt).
