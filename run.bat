@echo off
chcp 65001 > nul
title LINE Sticker Studio - LINE Creators Market Tool
cls
echo ======================================================================
echo    🟢 LINE Sticker Studio - เครื่องมือเตรียมภาพทำสติกเกอร์ LINE ขาย
echo ======================================================================
echo.
echo [1/2] กำลังตรวจสอบความพร้อมของระบบ...

where streamlit >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [2/2] กำลังเปิดเว็บแอพพลิเคชันผ่าน Browser...
    echo.
    streamlit run app.py
    goto end
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [2/2] กำลังเปิดเว็บแอพพลิเคชันด้วยคำสั่ง python -m streamlit run app.py...
    echo.
    python -m streamlit run app.py
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [2/2] กำลังเปิดเว็บแอพพลิเคชันด้วยคำสั่ง py -m streamlit run app.py...
    echo.
    py -m streamlit run app.py
    goto end
)

echo.
echo [ERROR] ไม่พบคำสั่ง streamlit หรือ python ในระบบ
echo กรุณาตรวจสอบการติดตั้ง Python หรือเปิดใช้งาน Virtual Environment
echo.
pause

:end
