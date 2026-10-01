# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  get_allowed_ids.py                                :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/29 14:12:55 by ksener          #+#    #+#               #
#  Updated: 2026/10/01 12:59:25 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from llm_sdk import Small_LLM_Model


def get_allowed_ids(
    generated_text: str,
    current_state: str,
    small_llm_model: Small_LLM_Model,
    all_functions: list[dict],
    current_index: int
) -> list[int]:
    valid_func_names = [fn["name"] for fn in all_functions]

    param_names = []
    selected_fn = None

    for fn in all_functions:
        if fn["name"] in generated_text:
            selected_fn = fn
            param_names = list(fn["parameters"].keys())
            break

    bracket_id = small_llm_model.encode("{").tolist()[0]
    name_key_ids = small_llm_model.encode('"name": "').tolist()[0]

    valid_func_ids = []
    for name in valid_func_names:
        valid_func_ids.extend(small_llm_model.encode(name).tolist()[0])

    params_key_ids = small_llm_model.encode(
        '", "parameters": {'
    ).tolist()[0]

    if current_state == "EXPECT_BRACKET":
        return bracket_id
    elif current_state == "EXPECT_NAME_KEY":
        return [name_key_ids[current_index]]
    elif current_state == "EXPECT_FUNC_NAME":
        return valid_func_ids
    elif current_state == "EXPECT_PARAM_KEY":
        return [params_key_ids[current_index]]
    elif current_state == "EXPECT_PARAM_NAME":
        encoded_param_list = []
        for p in param_names:
            encoded_param_list.extend(
                small_llm_model.encode(f'"{p}": ').tolist()[0])
        return encoded_param_list
    elif current_state == "EXPECT_PARAM_VALUE":
        written_params = [
            p for p in param_names if f'"{p}":' in generated_text]
        current_param = written_params[-1] if written_params else None

        remaining_params = [p for p in param_names if p not in written_params]
        if remaining_params:
            exit_id = small_llm_model.encode(", ").tolist()[0]
        else:
            exit_id = small_llm_model.encode("}").tolist()[0]

        if current_param and selected_fn:
            param_type = selected_fn["parameters"][current_param]["type"]
            if param_type == "number":
                digit_ids = []
                for i in range(10):
                    digit_ids.extend(
                        small_llm_model.encode(str(i)).tolist()[0])
                dot_id = small_llm_model.encode(".").tolist()[0]
                minus_id = small_llm_model.encode("-").tolist()[0]
                return digit_ids + dot_id + minus_id + exit_id
            elif param_type == "string":
                return small_llm_model.encode('"')[0].tolist() + exit_id
    elif current_state == "EXPECT_MAIN_CLOSE":
        return small_llm_model.encode("}").tolist()[0]
