#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from thatsoundapi.utils.hashing import hash_telegram_id

print(hash_telegram_id(sys.argv[1]))
