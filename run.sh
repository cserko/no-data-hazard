#!/bin/bash

#cd $HOME/Documents/no-data-hazard/
echo with no forwarding. . .
python src/mips_yacc.py --noforward=yes --path=files/input.txt
echo with forwarding. . .
python src/mips_yacc.py --forward=yes --path=files/input.txt
echo scheduling. . .
python src/mips_yacc.py --schedule=yes --path=files/forward.txt
python src/mips_yacc.py --schedule=yes --path=files/scheduled.txt
python src/mips_yacc.py --schedule=yes --path=files/scheduled.txt
python src/mips_yacc.py --schedule=yes --path=files/scheduled.txt
python src/mips_yacc.py --schedule=yes --path=files/scheduled.txt
python src/mips_yacc.py --check_dependency=yes --path=files/scheduled.txt
echo done!