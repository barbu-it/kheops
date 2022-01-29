#!/bin/bash

make clean

#sphinx-apidoc -f -M -o ./api ../kheops/
sphinx-apidoc -M -o ./api ../kheops/

make html
