#!/bin/bash
set -e
# Set the environment variables
export DATA_PROVIDER_HOST=localhost:50051;
# Install the dependencies
pip install -r simulator/requirements.txt

pip install coverage

# Generate the coverage report
coverage run -m unittest discover -s N2KClient/test -p "*.py"
coverage html