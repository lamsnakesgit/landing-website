#!/bin/bash
# Run B2B Sales OS Orchestrator
cd /root/sales_os
export $(grep -v '^#' .env | xargs)
export PYTHONPATH=/root/sales_os
source src/venv/bin/activate
python3 src/orchestrator/main.py
