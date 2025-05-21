
@echo off

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Print instructions
echo.
echo Setup complete! To run the UXAgent backend:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Set your OpenAI API key:
echo    set OPENAI_API_KEY=your-api-key
echo.
echo 3. Start the API server:
echo    python api.py
echo.
echo The API will be available at: http://localhost:8000
