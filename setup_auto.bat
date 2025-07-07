@echo off
echo VET-ASSISTANT-CLI 自動投稿システム セットアップ
echo ================================================
echo.

REM 依存関係のインストール
echo 📦 依存関係をインストール中...
pip install -r requirements_auto.txt
if %errorlevel% neq 0 (
    echo ❌ インストールに失敗しました。
    pause
    exit /b 1
)

echo.
echo ✅ セットアップが完了しました！
echo.
echo 🚀 使用方法:
echo ================================
echo 1. ペルソナ学習:
echo    python main.py learn "C:\Users\souhe\Desktop\X過去投稿"
echo.
echo 2. 週間記事生成:
echo    python auto_post_system.py generate-week
echo    python auto_post_system.py generate-week --topic "猫の腎臓病"
echo.
echo 3. Twitter API設定:
echo    python auto_post_system.py setup-twitter
echo.
echo 4. 自動投稿開始:
echo    python auto_post_system.py start-scheduler
echo.
echo 💡 詳細は README.md をご確認ください
echo.
pause