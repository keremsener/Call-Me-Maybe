# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  constrained_decoder.py                            :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:11 by ksener          #+#    #+#               #
#  Updated: 2026/09/29 14:14:09 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from numpy import argmax
import torch

from llm_sdk import Small_LLM_Model
from .models import FuncDef
from .prompt_builder import prompt_builder
from .get_allowed_ids import get_allowed_ids


def validate(logits: list[float], allowed_ids: list[int]) -> list[float]:
    for i in range(len(logits)):
        if i not in allowed_ids:
            logits[i] = -float("inf")

    return logits


def constrained_decoder(user_prompt: str, parsed_funcs: list[FuncDef]) -> str:
    max_token = 50

    small_llm_model = Small_LLM_Model(dtype=torch.float16)

    all_functions = [f.model_dump() for f in parsed_funcs]

    text_input = prompt_builder(parsed_funcs, user_prompt)

    encode_list = small_llm_model.encode(text_input).tolist()[0]

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
            all_functions
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
        elif current_state == "EXPECT_PARAM_VALUE":
            comma_id = small_llm_model.encode(", ")[0]
            close_params_id = small_llm_model.encode("}")[0]

            if next_word_id == comma_id:
                current_state = "EXPECT_PARAM_NAME"
            elif next_word_id == close_params_id:
                current_state = "EXPECT_MAIN_CLOSE"
        elif current_state == "EXPECT_MAIN_CLOSE":
            close_main_id = small_llm_model.encode("}")[0]
            if next_word_id == close_main_id:
                break

        if next_word_id == eos_id:
            break

        encode_list.append(next_word_id)

    return small_llm_model.decode(encode_list)
