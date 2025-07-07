@echo off
echo VET-ASSISTANT-CLI セットアップを開始します...
echo.

REM 依存関係のインストール
echo 依存関係をインストール中...
pip install google-generativeai
if %errorlevel% neq 0 (
    echo ❌ インストールに失敗しました。Pythonとpipがインストールされていることを確認してください。
    pause
    exit /b 1
)

echo.
echo ✅ セットアップが完了しました！
echo.
echo 使用方法:
echo 1. ペルソナ学習: python main.py learn "C:\Users\souhe\Desktop\X過去投稿"
echo 2. 投稿生成: python main.py x-post --type specialty --day mon --topic "猫の熱中症"
echo.
pause