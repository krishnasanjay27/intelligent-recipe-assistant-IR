#!/usr/bin/env bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r backend/requirements.txt

echo "=== Downloading dataset (if not cached) ==="
python -c "
import os, gdown
os.makedirs('data', exist_ok=True)
path = 'data/preprocessed_60000.csv'
if not os.path.exists(path):
    gdown.download('https://drive.google.com/uc?id=1M74qCt0Kq566XsdwCfboARwEmIJCXrEY', path, quiet=False)
    print('Dataset downloaded.')
else:
    print('Dataset already cached.')
"

echo "=== Downloading NLTK data ==="
python -c "
import os, nltk
d = '/opt/render/nltk_data'
os.makedirs(d, exist_ok=True)
for pkg in ['wordnet', 'omw-1.4', 'stopwords']:
    nltk.download(pkg, download_dir=d)
print('NLTK data ready.')
"

echo "=== Build complete ==="
