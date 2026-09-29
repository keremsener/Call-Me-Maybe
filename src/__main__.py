# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  __main__.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:09 by ksener          #+#    #+#               #
#  Updated: 2026/09/29 14:46:29 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from argparse import ArgumentParser
from .parsing import parse_test_inputs


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


def read_prompt() -> list:
    init_prompt_list = parse_test_inputs(terminal_parsing()[1])
    prompt_list = [item.prompt for item in init_prompt_list]
    return prompt_list


read_prompt()
