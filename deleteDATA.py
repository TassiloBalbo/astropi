# 🔧 script for removing captured images and data, used for testing
# scp filip@4.2.0.169:~/code/astropi/deleteDATA.py ~/stratopi
# scp filip@4.2.0.169:~/code/astropi/program.py ~/stratopi
# scp *.jpg filip@4.2.0.169:~/code/astropi/data/

import os
from pathlib import Path

path = Path(__file__).parent.resolve()

for entry in os.scandir(path):
	if (entry.path.endswith(".jpg") or entry.path.endswith(".jpg") or entry.path.endswith(".csv") or entry.path.endswith(".log") and entry.is_file()):
		os.remove(entry)