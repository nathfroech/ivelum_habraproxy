#!/usr/bin/env python

"""
Script for .env file generating.

Usage:
`python helpers/generate_env_file.py`

If you need to add a new setting, update `TEMPLATE` constant with line that looks like `SETTING_NAME = setting_value`.
In `TEMPLATE` you may use `{base_dir}` placeholder to substitute base project path. If you want to add more
substitutions - update the returning dict of the function `create_context`.
"""

import argparse
import pathlib
from typing import Any, Dict

# TODO: Add your settings into this template like `SETTING_NAME = setting_value`
TEMPLATE = """
"""

Context = Dict[str, Any]


def create_arguments_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser('Generate .env file')
    parser.add_argument('--name', dest='file_name', action='store', default='.env')
    parser.add_argument('--rewrite', dest='rewrite', action='store_true')
    return parser


def create_context(base_dir: pathlib.Path) -> Context:
    return {
        'base_dir': str(base_dir),
    }


def render_to_string(context: Context) -> str:
    return TEMPLATE.format(**context)


if __name__ == '__main__':
    arguments_parser = create_arguments_parser()
    args = arguments_parser.parse_args()

    file_name = args.file_name
    project_dir = pathlib.Path(__file__).parents[1]
    file_path: pathlib.Path = project_dir / file_name
    if file_path.is_file() and not args.rewrite:
        raise ValueError('File {file_name} already exists!'.format(file_name=file_name))

    file_context = create_context(project_dir)
    generated_file = render_to_string(file_context)
    file_path.write_text(generated_file)
