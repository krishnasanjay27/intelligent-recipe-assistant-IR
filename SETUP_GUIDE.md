# Setup Guide for Windows Users

## Quick Start (5 minutes)

1. **Run setup script:**
   - Double-click `setup.bat`
   - Wait for all installations to complete

2. **Download dataset:**
   - Download data from [https://drive.google.com/file/d/1M74qCt0Kq566XsdwCfboARwEmIJCXrEY/view?usp=sharing]
   - Place in `data/` folder

3. **Start the application:**
   - Terminal 1: run `python -m uvicorn app:app --reload` in /backend directory
   - Terminal 2: run `npm start` in /frontend directory
   - Open http://localhost:3000 in browser

## Troubleshooting

**"Python not found"**
- Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH"

**"Node.js not found"**
- Install Node.js from https://nodejs.org/

**"Module not found"**
- Delete `venv` folder
- Run `setup.bat` again