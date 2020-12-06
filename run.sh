#!/bin/bash

cd $HOME/Documents/no-data-hazard/

python mips_yacc.py --noforward=yes --path=input.txt
python mips_yacc.py --forward=yes --path=input.txt
python mips_yacc.py --schedule=yes --path=forward.txt
python mips_yacc.py --check_dependency=yes --path=scheduled.txt
