import json
import os

DATA_FILE = os.getenv('DATA_FILE', 'voyages.json')
ARCHIVE_FILE = os.getenv('ARCHIVE_FILE', 'archives.json')

if os.path.exists(DATA_FILE):
    voyages = json.load(open(DATA_FILE))
else:
    voyages = []

if os.path.exists(ARCHIVE_FILE):
    archives = json.load(open(ARCHIVE_FILE))
else:
    archives = {}


def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(voyages, f, indent=4)

def save_archives():
    with open(ARCHIVE_FILE, 'w') as f:
        json.dump(archives, f, indent=4)