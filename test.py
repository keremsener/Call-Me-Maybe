# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  test.py                                           :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:17:28 by ksener          #+#    #+#               #
#  Updated: 2026/09/24 16:20:36 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import json
from numpy import argmax
import torch
from src.llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    max_token = 50
    small_llm_model = Small_LLM_Model(dtype=torch.float16)
    test_input = "Question: What is the sum of 5 and 10?\nAnswer:"
    encode_list = small_llm_model.encode(test_input).tolist()[0]
    eos_id = small_llm_model.encode("<|endoftext|>").tolist()[0]
    if isinstance(eos_id, list):
        eos_id = eos_id[0]
    for _ in range(max_token):
        logits = small_llm_model.get_logits_from_input_ids(encode_list)
        next_word_id = int(argmax(logits))
        if next_word_id == eos_id:
            break

        encode_list.append(next_word_id)
        print(small_llm_model.decode([next_word_id]), end="", flush=True)


if __name__ == "__main__":
    main()
