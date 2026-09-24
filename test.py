import json
from numpy import argmax
import torch
from src.llm_sdk.llm_sdk import Small_LLM_Model


def main() -> None:
    small_llm_model = Small_LLM_Model(dtype=torch.float16)
    test_input = "Question: What is the sum of 5 and 10?\nAnswer:"
    encode_list = small_llm_model.encode(test_input).tolist()[0]
    for i in range(10):
        logits = small_llm_model.get_logits_from_input_ids(encode_list)
        next_word_id = argmax(logits)
        encode_list.append(next_word_id)
        print(small_llm_model.decode([next_word_id]), end="", flush=True)


if __name__ == "__main__":
    main()
