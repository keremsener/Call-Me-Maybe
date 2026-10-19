# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  models.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:13 by ksener          #+#    #+#               #
#  Updated: 2026/10/08 11:36:47 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Data models for function definitions and function-calling payloads."""

from typing import Any
from enum import Enum
from pydantic import BaseModel, Field


class ExpectState(Enum):
    BRACKET = "BRACKET"
    NAME_KEY = "NAME_KEY"
    FUNC_NAME = "FUNC_NAME"
    PARAM_KEY = "PARAM_KEY"
    PARAM_NAME = "PARAM_NAME"
    PARAM_VALUE = "PARAM_VALUE"
    MAIN_CLOSE = "MAIN_CLOSE"


class ParamDef(BaseModel):
    """Definition of a function parameter."""

    type: str


class ReturnDef(BaseModel):
    """Definition of a function return value."""

    type: str


class FuncDef(BaseModel):
    """Schema definition for a callable function."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, ParamDef]
    returns: ReturnDef


class FuncCall(BaseModel):
    """Single user prompt used for function-calling evaluation."""

    prompt: str


class FuncRes(BaseModel):
    """Result object returned after the model selects a function."""

    name: str
    prompt: str
    parameters: dict[str, Any]
