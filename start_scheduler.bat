@echo off
echo VET-ASSISTANT-CLI 自動投稿スケジューラー
echo =====================================
echo.

REM 必要ファイルの確認
if not exist "投稿スケジュール.xlsx" (
    echo ❌ 投稿スケジュールファイルが見つかりません
    echo 先に週間記事を生成してください: generate_week.bat
    echo.
    pause
    exit /b 1
)

if not exist "config.json" (
    echo ❌ 設定ファイルが見つかりません
    echo 先にTwitter API設定を行ってください: setup_twitter.bat
    echo.
    pause
    exit /b 1
)

echo 🔐 Twitter API設定を確認中...
python -c "import json; config=json.load(open('config.json')); exit(0 if config.get('twitter_bearer_token') else 1)"
if %errorlevel% neq 0 (
    echo ❌ Twitter API設定が不完全です
    echo setup_twitter.bat を実行してAPIキーを設定してください
    echo.
    pause
    exit /b 1
)

echo ✅ 設定確認完了
echo.
echo 🚀 自動投稿スケジューラーを開始します
echo ⏰ 毎朝7時に #猫のあれこれ ハッシュタグ付きの投稿をチェックします
echo 💡 停止するには Ctrl+C を押してください
echo.
echo 投稿予定を確認していますか？
pause

echo.
echo スケジューラー開始中...
python auto_post_system.py start-scheduler

echo.
echo 🛑 スケジューラーが停止しました
pause