uv venv photo_venv --clear
source photo_venv/bin/activate

uv pip install -r requirements.txt

flask --app photo-server run --port 1289

deactivate
