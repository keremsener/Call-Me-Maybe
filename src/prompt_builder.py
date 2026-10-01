# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  prompt_builder.py                                 :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:15 by ksener          #+#    #+#               #
#  Updated: 2026/10/01 17:05:11 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #

"""Prompt-building helpers for function-calling requests."""

import json

from .models import FuncDef


def prompt_builder(funcs: list[FuncDef], user_prompt: str) -> str:
    """Build the instruction prompt for the local model.

    Args:
        funcs: Available function schemas.
        user_prompt: User request to translate into a function call.

    Returns:
        A prompt string that instructs the model to return valid JSON.
    """
    funcs_json = json.dumps([item.model_dump() for item in funcs], indent=2)
    final_prompt = f"""
You are a function calling assistant.
Select the most appropriate function from the list below based
on the user's request. Respond ONLY with a valid JSON object.
Do not include any explanation or conversational text.
Available Functions: {funcs_json}
User Request: {user_prompt}
JSON Response:
"""
    return final_prompt
