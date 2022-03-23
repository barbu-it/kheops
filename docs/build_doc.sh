#!/bin/bash

make clean

sphinx-apidoc -f -M -o ./api ../kheops/
#sphinx-apidoc -M -o ./api ../kheops/

mkdir -p learn
jupyter nbconvert --to markdown --output=../learn/learn101.md jupyter/learn101.ipynb

# See: https://www.datacamp.com/community/tutorials/jinja2-custom-export-templates-jupyter

make html
