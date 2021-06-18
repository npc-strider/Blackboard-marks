import os
from pathlib import Path

BASE_URL = "https://lms.uwa.edu.au" # Include protocol.

DL_DIR = os.getcwd()+os.path.sep+"tmp"+os.path.sep
Path(DL_DIR).mkdir(parents=True, exist_ok=True)