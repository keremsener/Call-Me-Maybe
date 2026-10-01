# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parsing.py                                        :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 14:23:07 by ksener          #+#    #+#               #
#  Updated: 2026/10/01 17:05:12 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Parsing helpers for JSON data files used by the project."""

import json

from .models import FuncCall, FuncDef


def parse_functions_definition(file_path: str) -> list[FuncDef]:
    """Load and validate the function definition schema file.

    Args:
        file_path: Path to the JSON function schema file.

    Returns:
        A list of validated function definitions.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return [FuncDef(**item) for item in data]


def parse_test_inputs(file_path: str) -> list[FuncCall]:
    """Load prompt examples from a JSON test file.

    Args:
        file_path: Path to the JSON test input file.

    Returns:
        A list of prompt objects to evaluate.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return [FuncCall(**item) for item in data]
