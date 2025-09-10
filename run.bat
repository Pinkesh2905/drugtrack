@echo off
REM Check if virtual environment exists
IF NOT EXIST "myenv" (
    echo Creating virtual environment...
    python -m venv myenv
)

echo Activating virtual environment...
call myenv\Scripts\activate

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo Running migrations...
python manage.py migrate

REM Optional: create superuser automatically (requires manual input)
REM python manage.py createsuperuser

echo Starting Django server...
python manage.py runserver

pause
