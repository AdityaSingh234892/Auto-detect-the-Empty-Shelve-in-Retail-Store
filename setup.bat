@echo off
echo =================================
echo Shelf Monitoring System Setup
echo =================================
echo.

echo Installing required packages...
pip install -r requirements.txt

echo.
echo Running setup test...
python test_setup.py

echo.
echo Setup complete!
echo.
echo Quick start options:
echo 1. python demo.py          - Run demo with sample images
echo 2. python main.py          - Start real-time monitoring
echo 3. python test_setup.py    - Test system setup
echo.
pause
