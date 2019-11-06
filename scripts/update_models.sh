#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python $DIR/update_gensim_models_v1.py
python $DIR/update_gensim_models_v2.py
python $DIR/update_gensim_models_v3.py