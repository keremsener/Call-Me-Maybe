# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  __main__.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:09 by ksener          #+#    #+#               #
#  Updated: 2026/10/01 15:58:24 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import json

from argparse import ArgumentParser

import torch  # pushlarken sil çünkü istenmiyor.

from .constrained_decoder import constrained_decoder
from .parsing import parse_functions_definition, parse_test_inputs
from llm_sdk import Small_LLM_Model


def terminal_parsing() -> tuple[str, str, str]:
    parser = ArgumentParser()
    parser.add_argument('--functions_definition', type=str,
                        default="data/input/functions_definition.json")
    parser.add_argument('--input', type=str,
                        default="data/input/function_calling_tests.json")
    parser.add_argument('--output', type=str,
                        default="data/output/function_calling_results.json")
    args = parser.parse_args()

    return (args.functions_definition, args.input, args.output)


def main() -> None:
    func_path, input_path, output_path = terminal_parsing()
    init_prompt_list = parse_test_inputs(input_path)
    prompt_list = [item.prompt for item in init_prompt_list]
    load_function_schemas = parse_functions_definition(func_path)
    small_llm_model = Small_LLM_Model(dtype=torch.float16)
    results = []
    for prompt in prompt_list:
        text = constrained_decoder(prompt, load_function_schemas,
                                   small_llm_model)
        parsed_json = json.loads(text)
        ordered_result = {"prompt": prompt}
        ordered_result.update(parsed_json)
        results.append(ordered_result)
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(results, file, indent=2)


if __name__ == "__main__":
    main()
