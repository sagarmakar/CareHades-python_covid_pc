# CareHades-python_covid_pc
use tmux if available

sudo su
cd python_covid
pip3 install -r requirments.txt
python3 server.py
python3 clientDoctor.py
python3 client.py     ----- if you want to use terminal for client
python3 heatmap.py    ----- if you want to create heatmap manually
python3 gui.py        ------ if you want an interactive client window
