python3 -m venv photo_venv || echo "venv exists"
source photo_venv/bin/activate

pip3 install -r requirements.txt

python3 main.py

deactivate
