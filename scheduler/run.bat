cd ../backend
start python app.py
cd ../scheduler
timeout /t 10 /nobreak
start python main.py
timeout /t 10 /nobreak
taskkill /f /im python.exe