# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  models.py                                         :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:13 by ksener          #+#    #+#               #
#  Updated: 2026/10/01 17:05:11 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Data models for function definitions and function-calling payloads."""

from typing import Any

from pydantic import BaseModel, Field


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
