@echo off
echo VET-ASSISTANT-CLI 週間記事生成
echo ==============================
echo.

REM 学習状況確認
if not exist "persona_data.json" (
    echo ❌ ペルソナデータが見つかりません
    echo 先に以下のコマンドを実行してください:
    echo python main.py learn "C:\Users\souhe\Desktop\X過去投稿"
    echo.
    pause
    exit /b 1
)

echo 📝 1週間分の記事を生成します...
echo.

REM ユーザー入力
echo トピックを指定しますか？（何も入力しなければデフォルト）
set /p TOPIC="トピック（例: 猫の腎臓病）: "

echo.
echo 生成中...

if "%TOPIC%"=="" (
    python auto_post_system.py generate-week
) else (
    python auto_post_system.py generate-week --topic "%TOPIC%"
)

if %errorlevel% equ 0 (
    echo.
    echo ✅ 週間記事生成完了！
    echo 📊 投稿スケジュール.xlsx を開いて内容を確認・編集してください
    echo.
    echo 📋 次のステップ:
    echo 1. Excelファイルで記事内容を確認・修正
    echo 2. #猫のあれこれ ハッシュタグがあることを確認
    echo 3. 自動投稿を開始: start_scheduler.bat
    echo.
    
    REM Excelファイルを開くか確認
    set /p OPEN_EXCEL="Excelファイルを開きますか？ (y/n): "
    if /i "%OPEN_EXCEL%"=="y" (
        start "投稿スケジュール.xlsx"
    )
) else (
    echo ❌ 記事生成に失敗しました
)

echo.
pause