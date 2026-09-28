# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  models.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:13 by ksener          #+#    #+#               #
#  Updated: 2026/09/28 14:28:47 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

from pydantic import BaseModel, Field
from typing import Any

class ParamDef(BaseModel):
    type: str


class ReturnDef(BaseModel):
    type: str


class FuncDef(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, ParamDef]
    returns: ReturnDef


class FuncCall(BaseModel):
    prompt: str

class FuncRes(BaseModel):
    name: str
    prompt: str
    parameters: dict[str, Any]