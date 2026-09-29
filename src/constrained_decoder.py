# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  constrained_decoder.py                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:11 by ksener          #+#    #+#               #
#  Updated: 2026/09/29 13:05:27 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import json

from numpy import argmax
import torch

from llm_sdk import Small_LLM_Model
from parsing import get_functions


def validate(logits: list[float], allowed_ids: list[int]) -> list[float]:
    for i in range(len(logits)):
        if i not in allowed_ids:
            logits[i] = -float("inf")

    return logits


def get_allowed_ids(
    generated_text: str,
    current_state: str,
    small_llm_model: Small_LLM_Model,
) -> list[int]:
    all_functions = get_functions()
    valid_func_names = [fn["name"] for fn in all_functions]

    param_names = []

    for fn in all_functions:
        if fn["name"] in generated_text:
            selected_fn = fn
            param_names = list(fn["parameters"].keys())
            break

    bracket_id = small_llm_model.encode("{")[0]
    name_key_ids = small_llm_model.encode('"name": "').tolist()

    valid_func_ids = [
        small_llm_model.encode(name)[0]
        for name in valid_func_names
    ]

    params_key_ids = small_llm_model.encode(
        '", "parameters": {'
    ).tolist()

    if current_state == "EXPECT_BRACKET":
        return [bracket_id]
    elif current_state == "EXPECT_NAME_KEY":
        return name_key_ids
    elif current_state == "EXPECT_FUNC_NAME":
        return valid_func_ids
    elif current_state == "EXPECT_PARAM_KEY":
        return params_key_ids
    elif current_state == "EXPECT_PARAM_NAME":
        encoded_param_list = [small_llm_model.encode(
            f'"{p}": ')[0] for p in param_names]
        return encoded_param_list
    elif current_state == "EXPECT_PARAM_VALUE":
        current_param = None
        for p in param_names:
            if generated_text.endswith(f'"{p}": '):
                current_param = p
                break      
        if current_param:
            param_type = selected_fn["parameters"][current_param]["type"]
            if param_type == "number":
                return [small_llm_model.encode(str(i))[0] for i in range(10)]
            elif param_type == "string":
                return [small_llm_model.encode('"')[0]]
        


def constrained_decoder() -> None:
    max_token = 50

    small_llm_model = Small_LLM_Model(dtype=torch.float16)

    test_input = (
        "Question: What is the sum of 5 and 10?\n"
        "Answer:"
    )

    encode_list = small_llm_model.encode(test_input).tolist()[0]

    eos_id = small_llm_model.encode(
        "<|endoftext|>"
    ).tolist()[0]

    if isinstance(eos_id, list):
        eos_id = eos_id[0]
    current_state = "EXPECT_BRACKET"
    for step in range(max_token):
        logits = small_llm_model.get_logits_from_input_ids(
            encode_list
        )

        generated_text = small_llm_model.decode(encode_list)

        allowed_ids = get_allowed_ids(
            generated_text,
            current_state,
            small_llm_model,
        )

        if allowed_ids is not None:
            logits = validate(logits, allowed_ids)

        next_word_id = int(argmax(logits))
        if current_state == "EXPECT_BRACKET" and next_word_id in allowed_ids:
            current_state = "EXPECT_NAME_KEY"
        elif current_state == "EXPECT_NAME_KEY" and next_word_id == allowed_ids[-1]:
            current_state = "EXPECT_FUNC_NAME"
        elif current_state == "EXPECT_FUNC_NAME" and next_word_id in allowed_ids:
            current_state = "EXPECT_PARAM_KEY"
        elif current_state == "EXPECT_PARAM_KEY" and next_word_id == allowed_ids[-1]:
            current_state = "EXPECT_PARAM_NAME"
        elif current_state == "EXPECT_PARAM_NAME" and next_word_id in allowed_ids:
                current_state = "EXPECT_PARAM_VALUE"
        if next_word_id == eos_id:
            break

        encode_list.append(next_word_id)

        print(
            small_llm_model.decode([next_word_id]),
            end="",
            flush=True,
        )


if __name__ == "__main__":
    constrained_decoder()
