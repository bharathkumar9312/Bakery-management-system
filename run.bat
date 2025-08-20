@echo off
REM Activate virtual environment
call bakeryvenv\Scripts\activate

REM Run Django development server
python manage.py runserver

REM Keep the window open after execution
pause
