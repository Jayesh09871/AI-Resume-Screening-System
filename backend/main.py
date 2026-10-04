"""
Entrypoint allowing the application to run directly from within the backend directory.
"""
import sys
import os

_cur_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_cur_dir)

for _p in [_parent_dir, _cur_dir]:
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

from backend.app.main import app  # noqa: F401
