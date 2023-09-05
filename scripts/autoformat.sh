#!/bin/sh

# Sort imports
isort --atomic src

# Format code
black src
