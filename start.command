#!/bin/bash
# Nhấp đúp file này để chạy trang chấm điểm.
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "Lần đầu chạy: đang tạo môi trường Python..."
  python3 -m venv .venv
fi
.venv/bin/python -c "import openpyxl, segno" 2>/dev/null || .venv/bin/pip install -q openpyxl segno
.venv/bin/python server.py
