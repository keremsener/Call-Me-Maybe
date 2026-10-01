*This project has been created as part of the 42 curriculum by ksener.*

# Call Me Maybe

## Description

This project explores function calling with a local large language model using constrained decoding. The goal is to make the model generate a valid JSON object that references one of the predefined functions and provides the required arguments in the expected format.

The system reads a list of available function schemas, builds a prompt, and then restricts the model's next-token choices to a valid subset of tokens. This prevents malformed output and keeps generation aligned with the required structured output format.

The project is designed to help understand how a model can be steered toward tool use without losing the flexibility of natural language interaction. It combines local model inference, schema validation, and constrained output generation in a compact workflow.

---

## Project structure

```text
.
├── data/
│   ├── input/
│   │   ├── function_calling_tests.json
│   │   └── functions_definition.json
│   └── output/
│       └── function_calling_results.json
├── llm_sdk/
│   └── llm_sdk/
├── src/
│   ├── __main__.py
│   ├── constrained_decoder.py
│   ├── get_allowed_ids.py
│   ├── models.py
│   ├── parsing.py
│   └── prompt_builder.py
├── Makefile
├── mypy.ini
├── pyproject.toml
├── README.md
└── .venv/
```

---

## Instructions

### Installation and environment setup

The following environment variables were added to solve a local environment issue encountered while running the project in a restricted shared filesystem:

```bash
export UV_CACHE_DIR=/sgoinfre/ksener/.cache/uv
uv sync --active
export HF_HOME="/sgoinfre/ksener/huggingface_cache"
```

These settings are not part of the project logic itself, but they were essential for a stable setup in this environment:

- `UV_CACHE_DIR` keeps the `uv` dependency cache away from shared storage and prevents cache-related disk issues.
- `HF_HOME` redirects the Hugging Face model and tokenizer cache to a dedicated folder, which is especially useful when downloading or reusing large model files.

### Run the project

To start the program with the default input files:

```bash
make run
```

Or directly with Python:

```bash
uv run python -m src
```

### Use custom input and output files

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

### Linting and strict type checking

```bash
make lint
make lint-strict
```

This project is validated with `flake8` and `mypy --strict` to keep the code readable, maintainable, and typed consistently.

---

## Algorithm explanation

The constrained decoding approach is the core mechanism of this project.

### 1. Function schema loading

The project reads function definitions from a JSON file and maps them to Pydantic models. Each function includes:

- its name,
- a description,
- parameter definitions,
- and the expected return type.

This schema is later used both to build the prompt and to constrain token generation.

### 2. Prompt construction

The prompt contains:

- the task description,
- the available function signatures,
- and the user request.

The model is instructed to output only valid JSON and nothing else.

### 3. State-based constrained generation

The decoder does not simply accept model output freely. Instead, it tracks a current generation state such as:

- `EXPECT_BRACKET`
- `EXPECT_NAME_KEY`
- `EXPECT_FUNC_NAME`
- `EXPECT_PARAM_KEY`
- `EXPECT_PARAM_NAME`
- `EXPECT_PARAM_VALUE`
- `EXPECT_MAIN_CLOSE`

These states correspond to the expected shape of a function-call JSON object. For each state, the code computes which token IDs are allowed next and masks the rest.

### 4. Logit masking

The key logic lives in `get_allowed_ids()` and `validate()`:

- the model yields logits for the next token,
- allowed IDs are determined from the current generation state,
- all disallowed logits are set to `-inf`,
- and the highest remaining logit is selected via `numpy.argmax`.

This effectively forces the model to remain within the valid grammar of the JSON function-call structure.

### 5. Parameter-aware token restrictions

When a parameter value is being generated, the allowed tokens depend on the parameter type:

- numeric values may include digits, `-`, and `.`
- string values start with a quote and then continue in a controlled way
- separators such as `, ` and `}` are allowed only in the appropriate moments

This approach helps prevent invalid JSON like missing commas, wrong parameter ordering, or incomplete nested structures.

---

## Design decisions

Several design choices were made intentionally:

### Local-first architecture

The project is built around a local model rather than an external API. This keeps the workflow self-contained and makes experimentation easier in constrained environments.

### Schema-driven generation

Each function definition is treated as a contract. Instead of allowing free-form output, the system restricts generation to the valid function names and parameter structures defined in the input.

### Minimal model wrapper

The `llm_sdk` layer wraps the tokenizer and model in a small interface that exposes only the functionality required by the project: encoding, decoding, and access to logits.

### Type-safe validation

The project uses Pydantic models for the function definitions and runtime objects, and it is checked with `mypy --strict` to reduce subtle typing errors and improve maintainability.

### JSON as the final output contract

The project assumes the final output should always be a valid JSON object. This makes downstream processing simple and reliable when writing results to a file or integrating with another system.

---

## Performance analysis

This solution provides a useful balance between reliability and speed, although it depends heavily on the model and hardware.

### Accuracy

Accuracy is improved because the model is prevented from generating structurally invalid calls. The constrained mask helps the model stay inside the valid JSON and function-parameter schema, which is especially important for function-calling tasks.

### Speed

The decoding loop is token-by-token, which is slower than generating a full completion in one pass. However, the overhead remains acceptable for small function sets and short prompts because the token space is heavily restricted.

### Reliability

The approach is significantly more reliable than unconstrained generation for structured outputs, but it is still limited by the underlying model quality. If the model does not understand the user request well, the generated function could still be wrong even if the output is syntactically valid.

In practice, this solution is reliable for controlled and small-scale function-calling examples, especially when the function list is compact and the expected JSON structure is well-defined.

---

## Challenges faced

Several issues were encountered during implementation:

### 1. Environment and cache constraints

The project was run in a shared environment with limited and non-standard storage paths. This caused setup issues related to dependency caching and Hugging Face model cache placement. Solving that required explicit `UV_CACHE_DIR` and `HF_HOME` configuration.

### 2. Strict typing issues

The project initially failed under `mypy --strict` because of `Any`-typed outputs and missing Pydantic type resolution. This required cleaning up token encoding helpers and stabilizing the runtime typing around model output.

### 3. Constrained decoding logic complexity

Tracking the current JSON generation state and mapping it to allowed token IDs was the most complex part of the implementation. A small error in state transitions could produce invalid JSON or the wrong next function parameter. This was solved by designing a deterministic state machine and validating the generated output at each step.

### 4. Model output consistency

Even with constraints, the model sometimes produced near-valid but incomplete output. The project addressed this by emphasizing valid token filtering and by validating JSON output after generation.

---

## Testing strategy

The validation strategy combined runtime checks with static quality checks.

### Functional validation

The project was run with predefined prompts from `data/input/function_calling_tests.json` and the generated outputs were checked to ensure they still parse as valid JSON and match the expected function-calling structure.

### Type validation

The project was checked with:

```bash
mypy --strict .
```

This was important for catching missing types and unsafe `Any` returns.

### Style validation

The project also used `flake8` to keep the codebase clean and readable.

### Output verification

The program writes results into `data/output/function_calling_results.json`, which allows a quick inspection of whether the function name and parameters were extracted correctly for each input example.

---

## Example usage

### Example 1: arithmetic operation

Input prompt:

```text
What is the sum of 2 and 3?
```

A valid output may look like:

```json
{
  "name": "fn_add_numbers",
  "parameters": {
    "a": 2,
    "b": 3
  }
}
```

### Example 2: greeting

Input prompt:

```text
Greet john
```

A valid output may look like:

```json
{
  "name": "fn_greet",
  "parameters": {
    "name": "john"
  }
}
```

### Example 3: string replacement

Input prompt:

```text
Replace all numbers in "Hello 34 I'm 233 years old" with NUMBERS
```

A valid output may look like:

```json
{
  "name": "fn_substitute_string_with_regex",
  "parameters": {
    "source_string": "Hello 34 I'm 233 years old",
    "regex": "[0-9]+",
    "replacement": "NUMBERS"
  }
}
```

---

## Resources

### References

- [UV environments](https://docs-astral-sh.translate.goog/uv/pip/environments/?_x_tr_sl=en&_x_tr_tl=tr&_x_tr_hl=tr&_x_tr_pto=tc)
- [NumPy argmax in Python](https://www-geeksforgeeks-org.translate.goog/python/numpy-argmax-python/?_x_tr_sl=en&_x_tr_tl=tr&_x_tr_hl=tr&_x_tr_pto=tc&_x_tr_hist=true)
- [Difference between json.loads and json.load](https://medium-com.translate.goog/@gadallah.hatem/the-difference-between-json-loads-and-json-load-2dbd30065f26?_x_tr_sl=en&_x_tr_tl=tr&_x_tr_hl=tr&_x_tr_pto=tc&_x_tr_hist=true)
- [BaseModel.model_dump](https://reference.langchain.com/python/langsmith/_openapi_client/_models/BaseModel/model_dump)

### AI usage and transparency

AI was used as a collaborative assistant throughout the project, not as a replacement for the author’s decisions.

It was used for:

- debugging `mypy` and `flake8` issues,
- reviewing typing and refactoring suggestions,
- improving the clarity of the README,
- and discussing implementation ideas during debugging.

No part of the project logic was delegated to AI in a way that removed human responsibility for the code. The core design, validation, and final implementation decisions were made by the project author.

---

## Summary

This project demonstrates how a local LLM can be guided to produce structured function calls by restricting token generation to valid JSON and function-specific parameter formats. It combines practical model inference, controlled decoding, and schema-aware output generation in a compact and reproducible setup.
