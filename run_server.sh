uv venv server_venv --clear
source server_venv/bin/activate

uv pip install -r requirements.txt

flask --app program_server run --port 1289

deactivate
