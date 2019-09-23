#!/bin/bash

set -e

requirements_dir="requirements"

# It is possible that developer has conflicting versions of pip and pip-tools installed. (Installed pip version is too
# old for installed pip-tools or vice versa.) For avoiding such cases both tools are being updated manually before doing
# anything else with requirements. And `--upgrade-package pip-tools` in pip-compile call is still needed, because
# otherwise pip-tools may downgrade itself in output requirements file.
# Be aware, that if conflict is in the latest versions of both tools, it should be fixed manually by freezing pip-tools
# version in requirements.
pip install -U pip pip-tools
pip-compile "${requirements_dir}/dev.in" -o "${requirements_dir}/dev.txt" --upgrade-package pip-tools --no-header -q
pip-compile "${requirements_dir}/base.in" -o "${requirements_dir}/production.txt" --no-header -q
pip-sync "${requirements_dir}/dev.txt"
