# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  constrained_decoder.py                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:11 by ksener          #+#    #+#               #
#  Updated: 2026/10/21 17:00:28 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Constrained decoding for valid JSON function-call generation."""

from numpy import argmax

from llm_sdk import Small_LLM_Model
from .models import FuncDef, ExpectState
from .prompt_builder import prompt_builder
from .get_allowed_ids import get_allowed_ids


def validate(logits: list[float], allowed_ids: list[int]) -> list[float]:
    """Mask invalid logits and keep only the allowed token ids.

    Args:
        logits: Raw next-token logits.
        allowed_ids: Token ids allowed for the current state.

    Returns:
        The masked logits array.
    """
    for i in range(len(logits)):
        if i not in allowed_ids:
            logits[i] = -float("inf")

    return logits


def constrained_decoder(
        user_prompt: str,
        parsed_funcs: list[FuncDef],
        small_llm_model: Small_LLM_Model) -> str:
    """Generate a function-call JSON object under structured decoding rules.

    Args:
        user_prompt: Natural-language request from the user.
        parsed_funcs: Available function definitions.
        small_llm_model: Local model wrapper used for encoding and decoding.

    Returns:
        The generated JSON string representing the function call.
    """
    max_token = 50

    all_functions = [f.model_dump() for f in parsed_funcs]

    text_input = prompt_builder(parsed_funcs, user_prompt)

    encode_list = small_llm_model.encode(text_input).tolist()[0]
    encode_list_init_len = len(encode_list)
    name_key_len = len(small_llm_model.encode('"name": "').tolist()[0])
    param_key_len = len(small_llm_model.encode(
        '", "parameters": {').tolist()[0])
    eos_id = small_llm_model.encode(
        "<|endoftext|>"
    ).tolist()[0]

    if isinstance(eos_id, list):
        eos_id = eos_id[0]

    current_state = ExpectState.BRACKET
    current_index = 0
    for _ in range(max_token):
        logits = small_llm_model.get_logits_from_input_ids(
            encode_list
        )

        generated_text = small_llm_model.decode(
            encode_list[encode_list_init_len:])

        if generated_text.count("{") > 0 and generated_text.count("{") == generated_text.count("}"):
            break
        allowed_ids = get_allowed_ids(
            generated_text,
            current_state,
            small_llm_model,
            all_functions,
            current_index
        )

        if allowed_ids is not None:
            logits = validate(logits, allowed_ids)

        # assert allowed_ids is not None

        next_word_id = int(argmax(logits))
        print(small_llm_model.decode([next_word_id]), end="", flush=True)

        if (current_state == ExpectState.BRACKET and
                next_word_id in allowed_ids):
            current_state = ExpectState.NAME_KEY
            current_index = -1
        elif (current_state == ExpectState.NAME_KEY and
              next_word_id == allowed_ids[-1]):
            if current_index == name_key_len - 1:
                current_state = ExpectState.FUNC_NAME
                current_index = -1
        elif (current_state == ExpectState.FUNC_NAME and
              next_word_id in allowed_ids):
            test_text = small_llm_model.decode(encode_list + [next_word_id])
            valid_func_names = [fn["name"] for fn in all_functions]

            if any(test_text.endswith(fname) for fname in valid_func_names):
                current_state = ExpectState.PARAM_KEY
                current_index = -1
        elif (current_state == ExpectState.PARAM_KEY and
              next_word_id == allowed_ids[-1]):
            if current_index == param_key_len - 1:
                current_state = ExpectState.PARAM_NAME
                current_index = -1
        elif (current_state == ExpectState.PARAM_NAME and
              next_word_id == allowed_ids[-1]):
            selected_fn = next(
                (fn for fn in all_functions if fn["name"] in generated_text),
                None,
            )
            param_names = list(
                selected_fn["parameters"].keys()) if selected_fn else []
            param_text = generated_text.split('"parameters":')[-1]
            written = [p for p in param_names if f'"{p}": ' in param_text]
            remaining = [p for p in param_names if p not in written]

            if remaining:
                target_param = remaining[0]
                param_name_len = len(
                    small_llm_model.encode(
                        f'"{target_param}": '
                    ).tolist()[0]
                )

                if current_index == param_name_len - 1:
                    current_state = ExpectState.PARAM_VALUE
                    current_index = -1
        elif current_state == ExpectState.PARAM_VALUE:
            comma_ids = small_llm_model.encode(", ").tolist()[0]
            close_params_ids = small_llm_model.encode("}").tolist()[0]

            if next_word_id in comma_ids:
                current_state = ExpectState.PARAM_NAME
                current_index = -1
            elif next_word_id in close_params_ids:
                current_state = ExpectState.MAIN_CLOSE
                current_index = -1
        elif current_state == ExpectState.MAIN_CLOSE:
            close_main_id = small_llm_model.encode("}").tolist()[0]
            if next_word_id in close_main_id:
                encode_list.append(next_word_id)
                break

        if next_word_id == eos_id:
            break

        encode_list.append(next_word_id)
        current_index += 1

    print()
    return str(small_llm_model.decode(encode_list[encode_list_init_len:]))

# NEW ERROR:
# Warning: Could not decode model output for prompt'Replace all numbers in "Hello 34 I'm 233 years old" with NUMBERS': Expecting ',' delimiter: line 1 column 86 (char 85)
# EVE GEÇİNCE FİXLENECEK