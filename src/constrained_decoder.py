# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  constrained_decoder.py                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:11 by ksener          #+#    #+#               #
#  Updated: 2026/10/01 15:27:20 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from numpy import argmax

from llm_sdk import Small_LLM_Model
from .models import FuncDef
from .prompt_builder import prompt_builder
from .get_allowed_ids import get_allowed_ids


def validate(logits: list[float], allowed_ids: list[int]) -> list[float]:
    for i in range(len(logits)):
        if i not in allowed_ids:
            logits[i] = -float("inf")

    return logits


def constrained_decoder(user_prompt: str, parsed_funcs: list[FuncDef], small_llm_model: Small_LLM_Model) -> str:
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

    current_state = "EXPECT_BRACKET"
    current_index = 0
    for step in range(max_token):
        logits = small_llm_model.get_logits_from_input_ids(
            encode_list
        )

        generated_text = small_llm_model.decode(
            encode_list[encode_list_init_len:])

        allowed_ids = get_allowed_ids(
            generated_text,
            current_state,
            small_llm_model,
            all_functions,
            current_index
        )

        if allowed_ids is not None:
            logits = validate(logits, allowed_ids)

        next_word_id = int(argmax(logits))
        print(small_llm_model.decode([next_word_id]), end="", flush=True)
        # sonra sil bu printi

        if current_state == "EXPECT_BRACKET" and next_word_id in allowed_ids:
            current_state = "EXPECT_NAME_KEY"
            current_index = -1
        elif current_state == "EXPECT_NAME_KEY" and next_word_id == allowed_ids[-1]:
            if current_index == name_key_len - 1:
                current_state = "EXPECT_FUNC_NAME"
                current_index = -1
        elif current_state == "EXPECT_FUNC_NAME" and next_word_id in allowed_ids:
            test_text = small_llm_model.decode(encode_list + [next_word_id])
            valid_func_names = [fn["name"] for fn in all_functions]

            if any(test_text.endswith(fname) for fname in valid_func_names):
                current_state = "EXPECT_PARAM_KEY"
                current_index = -1
        elif current_state == "EXPECT_PARAM_KEY" and next_word_id == allowed_ids[-1]:
            if current_index == param_key_len - 1:
                current_state = "EXPECT_PARAM_NAME"
                current_index = -1
        elif current_state == "EXPECT_PARAM_NAME" and next_word_id == allowed_ids[-1]:
            selected_fn = next(
                (fn for fn in all_functions if fn["name"] in generated_text), None)
            param_names = list(
                selected_fn["parameters"].keys()) if selected_fn else []
            written = [p for p in param_names if f'"{p}": ' in generated_text]
            remaining = [p for p in param_names if p not in written]

            if remaining:
                target_param = remaining[0]
                param_name_len = len(small_llm_model.encode(
                    f'"{target_param}": ').tolist()[0])

                if current_index == param_name_len - 1:
                    current_state = "EXPECT_PARAM_VALUE"
                    current_index = -1
        elif current_state == "EXPECT_PARAM_VALUE":
            comma_ids = small_llm_model.encode(", ").tolist()[0]
            close_params_ids = small_llm_model.encode("}").tolist()[0]

            if next_word_id in comma_ids:
                current_state = "EXPECT_PARAM_NAME"
                current_index = -1
            elif next_word_id in close_params_ids:
                current_state = "EXPECT_MAIN_CLOSE"
                current_index = -1
        elif current_state == "EXPECT_MAIN_CLOSE":
            close_main_id = small_llm_model.encode("}").tolist()[0]
            if next_word_id in close_main_id:
                encode_list.append(next_word_id)
                break

        if next_word_id == eos_id:
            break

        encode_list.append(next_word_id)
        current_index += 1
    print()
    return small_llm_model.decode(encode_list[encode_list_init_len:])
