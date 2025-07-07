@echo off
echo VET-ASSISTANT-CLI Twitter API設定
echo =================================
echo.

echo Twitter Developer Accountが必要です
echo https://developer.twitter.com/en/portal/dashboard
echo.
echo 必要な認証情報を入力してください:
echo.

python auto_post_system.py setup-twitter

if %errorlevel% equ 0 (
    echo.
    echo ✅ Twitter API設定完了！
    echo 次は週間記事を生成してください: generate_week.bat
) else (
    echo.
    echo ❌ 設定に失敗しました
    echo APIキーを確認してください
)

echo.
pause