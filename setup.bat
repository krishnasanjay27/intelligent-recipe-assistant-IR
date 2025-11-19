@echo off
REM filepath: c:\Users\krish\Downloads\IR_Project\intelligent_recipe_assistant\setup.bat

echo.
echo ========================================
echo Intelligent Recipe Assistant Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Python and Node.js detected. Proceeding...
echo.

REM Create virtual environment
echo [STEP 1/6] Creating Python virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install backend dependencies
echo [STEP 2/6] Installing backend dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)
echo [OK] Backend dependencies installed
echo.

REM Download spaCy model
echo [STEP 3/6] Downloading spaCy language model...
python -m spacy download en_core_web_sm
if errorlevel 1 (
    echo [WARNING] spaCy download may have failed, but continuing...
)
echo [OK] spaCy setup complete
echo.

REM Download NLTK data
echo [STEP 4/6] Downloading NLTK stopwords...
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
if errorlevel 1 (
    echo [WARNING] NLTK download may have failed, but continuing...
)
echo [OK] NLTK data complete
echo.

REM Install frontend dependencies
echo [STEP 5/6] Installing frontend dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo [ERROR] Failed to install frontend dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo [OK] Frontend dependencies installed
echo.

REM Check dataset
echo [STEP 6/6] Checking dataset...
if not exist "data\raw\RAW_recipes.csv" (
    echo [WARNING] Dataset not found at data/raw/RAW_recipes.csv
    echo Please download it from Google Drive and place it there
) else (
    echo [OK] Dataset found
)
echo.
pause