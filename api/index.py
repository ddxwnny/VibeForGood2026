import os
import sys
from pathlib import Path

# Add project root and recollect/src to sys.path
_current_dir = Path(__file__).resolve().parent
_root_dir = _current_dir.parent
_recollect_src = _root_dir / "recollect" / "src"

for p in [str(_recollect_src), str(_root_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

os.environ.setdefault("RECOLLECT_ENV", "dev")
os.environ.setdefault("SEED_DEMO_DATA", "true")

from recollect.edge.api.main import app
