# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  get_allowed_ids.py                                :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/29 14:12:55 by ksener          #+#    #+#               #
#  Updated: 2026/10/01 16:18:33 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from typing import Any

from llm_sdk import Small_LLM_Model


def _encode_token_ids(model: Small_LLM_Model, text: str) -> list[int]:
    encoded = model.encode(text).tolist()
    if isinstance(encoded, list) and encoded and isinstance(encoded[0], list):
        encoded = encoded[0]
    if not isinstance(encoded, list):
        return []
    return [int(value) for value in encoded]


def get_allowed_ids(
    generated_text: str,
    current_state: str,
    small_llm_model: Small_LLM_Model,
    all_functions: list[dict[str, Any]],
    current_index: int,
) -> list[int] | None:
    valid_func_names = [str(fn["name"]) for fn in all_functions]

    param_names: list[str] = []
    selected_fn: dict[str, Any] | None = None

    for fn in all_functions:
        if fn["name"] in generated_text:
            selected_fn = fn
            param_names = list(str(key) for key in fn["parameters"].keys())
            break

    bracket_id = _encode_token_ids(small_llm_model, "{")
    name_key_ids = _encode_token_ids(small_llm_model, '"name": "')

    valid_func_ids: list[int] = []
    for name in valid_func_names:
        valid_func_ids.extend(_encode_token_ids(small_llm_model, name))

    params_key_ids = _encode_token_ids(
        small_llm_model,
        '", "parameters": {',
    )

    if current_state == "EXPECT_BRACKET":
        return bracket_id
    if current_state == "EXPECT_NAME_KEY":
        return [name_key_ids[current_index]]
    if current_state == "EXPECT_FUNC_NAME":
        return valid_func_ids
    if current_state == "EXPECT_PARAM_KEY":
        return [params_key_ids[current_index]]
    if current_state == "EXPECT_PARAM_NAME":
        written_params = [
            p for p in param_names if f'"{p}": ' in generated_text
        ]
        remaining_params = [p for p in param_names if p not in written_params]

        if remaining_params:
            target_param = remaining_params[0]
            encoded_param = _encode_token_ids(
                small_llm_model,
                f'"{target_param}": ',
            )
            return [encoded_param[current_index]]
        return _encode_token_ids(small_llm_model, "}")
    if current_state == "EXPECT_PARAM_VALUE":
        written_params = [
            p for p in param_names if f'"{p}":' in generated_text
        ]
        current_param = written_params[-1] if written_params else None

        remaining_params = [p for p in param_names if p not in written_params]
        if remaining_params:
            exit_id = _encode_token_ids(small_llm_model, ", ")
        else:
            exit_id = _encode_token_ids(small_llm_model, "}")

        if current_param and selected_fn:
            param_type = str(
                selected_fn["parameters"][current_param].get("type", "")
            )
            has_value_started = not generated_text.rstrip().endswith(
                f'"{current_param}":'
            )
            if param_type == "number":
                digit_ids: list[int] = []
                for i in range(10):
                    digit_ids.extend(_encode_token_ids(
                        small_llm_model, str(i)))
                dot_id = _encode_token_ids(small_llm_model, ".")
                minus_id = _encode_token_ids(small_llm_model, "-")
                allowed_tokens = digit_ids + dot_id + minus_id
                if has_value_started:
                    allowed_tokens.extend(exit_id)

                return allowed_tokens

            if param_type == "string":
                allowed_tokens = _encode_token_ids(small_llm_model, '"')

                if has_value_started:
                    allowed_tokens.extend(exit_id)

                return allowed_tokens
    elif current_state == "EXPECT_MAIN_CLOSE":
        return _encode_token_ids(small_llm_model, "}")

    return None
