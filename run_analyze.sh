uv venv server_venv --clear
source server_venv/bin/activate

uv pip install -r requirements.txt

uv run program_analyze.py

deactivate
