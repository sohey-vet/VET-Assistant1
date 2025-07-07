@echo off
echo VET-ASSISTANT-CLI ペルソナ学習を開始します...
echo.

python main.py learn "C:\Users\souhe\Desktop\X過去投稿"

echo.
echo 学習が完了しました。投稿生成を試してみてください。
echo 例: python main.py x-post --type specialty --day mon --topic "猫の熱中症"
echo.
pause