#!/bin/bash
# filepath: c:\Users\krish\Downloads\IR_Project\intelligent_recipe_assistant\setup.sh

echo ""
echo "========================================"
echo "Intelligent Recipe Assistant Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed"
    echo "Install from: https://www.python.org/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Install from: https://nodejs.org/"
    exit 1
fi

echo "[INFO] Python and Node.js detected. Proceeding..."
echo ""

# Create virtual environment
echo "[STEP 1/6] Creating Python virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi
source venv/bin/activate
echo "[OK] Virtual environment activated"
echo ""

# Install backend dependencies
echo "[STEP 2/6] Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install backend dependencies"
    exit 1
fi
echo "[OK] Backend dependencies installed"
echo ""

# Download spaCy model
echo "[STEP 3/6] Downloading spaCy language model..."
python -m spacy download en_core_web_sm
echo "[OK] spaCy setup complete"
echo ""

# Download NLTK data
echo "[STEP 4/6] Downloading NLTK stopwords..."
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
echo "[OK] NLTK data complete"
echo ""

# Install frontend dependencies
echo "[STEP 5/6] Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install frontend dependencies"
    cd ..
    exit 1
fi
cd ..
echo "[OK] Frontend dependencies installed"
echo ""

# Check dataset
echo "[STEP 6/6] Checking dataset..."
if [ ! -f "data/raw/RAW_recipes.csv" ]; then
    echo "[WARNING] Dataset not found at data/raw/RAW_recipes.csv"
    echo "Please download it from Google Drive and place it there"
else
    echo "[OK] Dataset found"
fi
echo ""

