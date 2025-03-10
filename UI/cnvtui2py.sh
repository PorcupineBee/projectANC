#!/bin/bash
if [ $1 ==  0 ]; then
    pyuic5 -x main_c.ui -o InteractiveDisplay.py
    sed -i 's|icons/|UI/icons/|g' InteractiveDisplay.py  
elif [ $1 ==  1 ]; then
    pyuic5 -x startup.ui -o startup.py
elif [ $1 ==  2 ]; then
    pyuic5 -x main_c.ui -o InteractiveDisplay.py
    sed -i 's|icons/|UI/icons/|g' InteractiveDisplay.py  
    pyuic5 -x startup.ui -o startup.py
else
    echo "Invalid argument"
fi