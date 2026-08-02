uv venv photo_venv || echo "venv exists"
source photo_venv/bin/activate

uv pip install -r requirements.txt

flask --app photo-server run

deactivate
