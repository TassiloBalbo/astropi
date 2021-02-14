# 🔧 script for removing captured images and data, used for testing
# scp deleteDATA.py pi@4.2.0.224:~/bigbrain
# scp program.py pi@4.2.0.224:~/bigbrain

import os
from pathlib import Path

path = Path(__file__).parent.resolve()

for entry in os.scandir(path):
	if (entry.path.endswith(".jpg") or entry.path.endswith(".jpg") or entry.path.endswith(".csv") and entry.is_file()):
		os.remove(entry)