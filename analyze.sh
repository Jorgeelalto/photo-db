uv venv photo_venv --clear
source photo_venv/bin/activate

uv pip install -r requirements.txt

uv run photo-analyze.py

deactivate
