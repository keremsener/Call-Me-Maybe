# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  __main__.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:09 by ksener          #+#    #+#               #
#  Updated: 2026/09/29 14:43:33 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from argparse import ArgumentParser
from .parsing import parse_test_inputs


def terminal_parsing() -> tuple[str, str, str]:
    parser = ArgumentParser()
    parser.add_argument('--functions_definition', type=str, required=True)
    parser.add_argument('--input', type=str, required=True)
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()

    return (args.functions_definition, args.input, args.output)


def read_prompt(input_path: str) -> list:
    init_prompt_list = parse_test_inputs(terminal_parsing()[1])
    prompt_list = [item.prompt for item in init_prompt_list]
    return prompt_list


read_prompt()
