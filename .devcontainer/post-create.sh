#!/usr/bin/env bash
set -euo pipefail
cd /workspaces/rothstein-storage-workshop-2026
python -m pip install -r requirements.txt
python -m ipykernel install --user --name rothstein-storage-workshop-2026 --display-name "Python (rothstein-storage-workshop-2026)"
python scripts/verify_setup.py --wait 120
