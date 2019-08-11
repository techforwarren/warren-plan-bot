#!/bin/sh

# Sort imports
isort -rc --atomic src

# Format code
black src
