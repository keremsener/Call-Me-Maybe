# ************************************************************************* #
#                                                                           #
#                                                      :::      ::::::::    #
#  __main__.py                                       :+:      :+:    :+:    #
#                                                  +:+ +:+         +:+      #
#  By: ksener <ksener@student.42kocaeli.com.tr   +#+  +:+       +#+         #
#                                              +#+#+#+#+#+   +#+            #
#  Created: 2026/09/24 16:29:09 by ksener          #+#    #+#               #
#  Updated: 2026/10/23 12:50:53 by ksener          ###   ########.fr        #
#                                                                           #
# ************************************************************************* #


"""Command-line entry point for the function-calling pipeline."""

from json import JSONDecodeError, dump, loads
import sys
from argparse import ArgumentParser
from .constrained_decoder import constrained_decoder
import os

try:
    from llm_sdk import Small_LLM_Model
except ImportError as exc:
    print(f"Error: Required dependency is missing: {exc}", file=sys.stderr)
    Small_LLM_Model = None

from .parsing import parse_functions_definition, parse_test_inputs


def terminal_parsing() -> tuple[str, str, str]:
    """Parse CLI arguments for the project entry point.

    Returns:
    A tuple of function definition path, input prompt path, and output path.
    """
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
    """Run the full function-calling evaluation pipeline."""
    if Small_LLM_Model is None:
        return

    try:
        func_path, input_path, output_path = terminal_parsing()
        init_prompt_list = parse_test_inputs(input_path)
        prompt_list = [item.prompt for item in init_prompt_list]
        load_function_schemas = parse_functions_definition(func_path)
        small_llm_model = Small_LLM_Model()
    except (OSError,
            RuntimeError,
            TypeError,
            ValueError,
            JSONDecodeError) as e:
        print(f"Error: Pipeline initialization failed: {e}", file=sys.stderr)
        return

    results = []
    for prompt in prompt_list:
        try:
            text = constrained_decoder(prompt, load_function_schemas,
                                       small_llm_model)
            parsed_json = loads(text)
        except (RuntimeError, TypeError, ValueError, JSONDecodeError) as exc:
            print(
                "Warning: Could not decode model output for "
                f"prompt'{prompt}': {exc}",
                file=sys.stderr,
            )
            continue

        ordered_result = {"prompt": prompt}
        ordered_result.update(parsed_json)
        results.append(ordered_result)

    try:
        folder_path = os.path.dirname(output_path)
        if folder_path:
            os.makedirs(folder_path, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as file:
            dump(results, file, indent=2)
        # sys.stdout.write("\033[H\033[2J")
        # sys.stdout.flush()
        print("\nSuccessfully written:", output_path)
    except OSError as exc:

        print(
            f"Error: Could not write results to '{output_path}': {exc}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
