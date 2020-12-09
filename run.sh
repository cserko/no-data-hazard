#!/bin/bash

cd $HOME/Documents/no-data-hazard/
echo with no forwarding. . .
python mips_yacc.py --noforward=yes --path=input.txt
echo with forwarding. . .
python mips_yacc.py --forward=yes --path=input.txt
echo scheduling. . .
python mips_yacc.py --schedule=yes --path=forward.txt
python mips_yacc.py --schedule=yes --path=scheduled.txt
python mips_yacc.py --schedule=yes --path=scheduled.txt
python mips_yacc.py --schedule=yes --path=scheduled.txt
python mips_yacc.py --schedule=yes --path=scheduled.txt
python mips_yacc.py --check_dependency=yes --path=scheduled.txt
