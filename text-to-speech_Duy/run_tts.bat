@echo off
chcp 65001 >nul
echo ============================================================
echo   HỆ THỐNG TỔNG HỢP TIẾNG NÓI MATCHA-TTS TIẾNG VIỆT
echo ============================================================
echo.
echo [1] Đọc câu trắc nghiệm từ file test_sentence.txt (Matcha-TTS 150k + Vocoder 50k)
echo [2] Nhập văn bản tiếng Việt từ bàn phím để đọc
echo [3] Đọc bằng giọng nơ-ron Edge-TTS Nữ (Hoài My)
echo [4] Đọc bằng giọng nơ-ron Edge-TTS Nam (Nam Minh)
echo [5] Khởi động cả dự án (Backend FastAPI :8000 + Frontend Angular :4200)
echo.
set /p opt="Chọn tùy chọn [1-5] (Mặc định: 1): "
if "%opt%"=="" set opt=1

if "%opt%"=="1" (
    echo.
    echo [Đang tổng hợp] Matcha-TTS đang đọc test_sentence.txt...
    python synthesize.py -f test_sentence.txt -o outputs/test_vimmrc_cau_c.wav
    if exist outputs\test_vimmrc_cau_c.wav (
        echo [Thành công] Đang mở file audio để nghe...
        start outputs\test_vimmrc_cau_c.wav
    )
    goto end
)

if "%opt%"=="2" (
    echo.
    set /p user_text="Nhập câu văn bản cần đọc: "
    python synthesize.py -t "%user_text%"
    goto end
)

if "%opt%"=="3" (
    echo.
    echo [Đang tổng hợp] Edge-TTS (Hoài My)...
    python synthesize.py -f test_sentence.txt -e edge -v vi-VN-HoaiMyNeural -o outputs/test_edge_hoaimy.mp3
    if exist outputs\test_edge_hoaimy.mp3 (
        echo [Thành công] Đang mở file audio để nghe...
        start outputs\test_edge_hoaimy.mp3
    )
    goto end
)

if "%opt%"=="4" (
    echo.
    echo [Đang tổng hợp] Edge-TTS (Nam Minh)...
    python synthesize.py -f test_sentence.txt -e edge -v vi-VN-NamMinhNeural -o outputs/test_edge_namminh.mp3
    if exist outputs\test_edge_namminh.mp3 (
        echo [Thành công] Đang mở file audio để nghe...
        start outputs\test_edge_namminh.mp3
    )
    goto end
)

if "%opt%"=="5" (
    echo.
    echo [Đang khởi động] Mở Backend và Frontend trong 2 cửa sổ mới...
    start "ViMMRC Backend API (:8000)" cmd /k "cd .. && python -m uvicorn scripts.api_server:app --host 127.0.0.1 --port 8000"
    start "ViMMRC Frontend UI (:4200)" cmd /k "cd ..\web-interface_Luong && npm start"
    echo.
    echo Đã mở máy chủ! Truy cập Web UI tại: http://localhost:4200/
    goto end
)

:end
echo.
pause

