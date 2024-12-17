@echo off

REM Check if the virtual environment folder exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

REM Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate

REM Install requirements
if exist "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    echo No requirements.txt found. Skipping package installation.
)

REM Run the main Python script
echo Launching main.py...
python main.py

REM Deactivate the virtual environment
echo Deactivating virtual environment...
deactivate
