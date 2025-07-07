@echo off
echo VET-ASSISTANT-CLI 投稿生成
echo.

REM デフォルト値を設定
set POST_TYPE=specialty
set DAY=mon
set TOPIC=猫の健康管理

REM ユーザー入力を受け取る
echo 投稿タイプを選択してください:
echo 1. cat-breed (猫種特集)
echo 2. specialty (専門テーマ)
echo 3. interactive (参加型)
set /p TYPE_CHOICE="選択 (1-3): "

if "%TYPE_CHOICE%"=="1" set POST_TYPE=cat-breed
if "%TYPE_CHOICE%"=="2" set POST_TYPE=specialty
if "%TYPE_CHOICE%"=="3" set POST_TYPE=interactive

echo.
echo 曜日を選択してください:
echo 1. mon (月曜) 2. tue (火曜) 3. wed (水曜) 4. thu (木曜)
echo 5. fri (金曜) 6. sat (土曜) 7. sun (日曜)
set /p DAY_CHOICE="選択 (1-7): "

if "%DAY_CHOICE%"=="1" set DAY=mon
if "%DAY_CHOICE%"=="2" set DAY=tue
if "%DAY_CHOICE%"=="3" set DAY=wed
if "%DAY_CHOICE%"=="4" set DAY=thu
if "%DAY_CHOICE%"=="5" set DAY=fri
if "%DAY_CHOICE%"=="6" set DAY=sat
if "%DAY_CHOICE%"=="7" set DAY=sun

echo.
set /p TOPIC="トピックを入力してください (例: 猫の熱中症): "

echo.
echo 投稿を生成中...
python main.py x-post --type %POST_TYPE% --day %DAY% --topic "%TOPIC%"

echo.
pause