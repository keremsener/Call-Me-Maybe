# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  parsing.py                                        :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/28 14:23:07 by ksener          #+#    #+#               #
#  Updated: 2026/09/28 16:57:10 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

import json
from .models import FuncDef, FuncCall

def parse_functions_definition(file_path:str) -> list[FuncDef]:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return [FuncDef(**item) for item in data]

def parse_test_inputs(file_path: str) -> list[FuncCall]:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return [FuncCall(**item) for item in data]
