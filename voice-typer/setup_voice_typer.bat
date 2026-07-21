@echo off
cd /d "%~dp0"
echo ============================================================
echo  voice-typer setup (installing Python packages)
echo  Do NOT run this as administrator - just double-click it.
echo  This may take several minutes on the first run.
echo ============================================================
echo.
py -m pip install -r requirements.txt
py -m pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
echo.
echo ============================================================
echo  Setup finished. If you see "Successfully installed" or
echo  "Requirement already satisfied" above with no red errors,
echo  you are ready. Now double-click run_voice_typer to start.
echo ============================================================
pause
