# 🐾 VET-ASSISTANT-CLI

**@souhei1219の完全自動投稿システム**

19年目の救急獣医師のペルソナを学習し、X（旧Twitter）への投稿を完全自動化するCLIアプリケーション

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Twitter](https://img.shields.io/badge/Twitter-@souhei1219-1DA1F2.svg)](https://twitter.com/souhei1219)

## 🚀 特徴

- **完全自動化**: 指示一つで1週間分の記事を生成
- **ペルソナ学習**: 7,581件の過去投稿から文体・特徴を学習
- **Excel編集**: 生成後にExcelで内容を確認・修正可能
- **自動投稿**: 毎朝7時に`#猫のあれこれ`ハッシュタグ付き記事を自動投稿
- **投稿サイクル管理**: 猫種特集週・専門テーマ週・参加型強化週の自動ローテーション
- **140文字制限**: 改行除外の正確な文字数管理

## 📋 システムフロー

```
指示 → AI記事生成 → Excel確認・編集 → 毎朝7時自動投稿
```

## 🛠️ クイックスタート

### 1. セットアップ
```bash
# リポジトリをクローン
git clone https://github.com/souhei1219/VET-ASSISTANT-CLI.git
cd VET-ASSISTANT-CLI

# 依存関係をインストール（Windows）
setup_auto.bat

# 依存関係をインストール（Linux/Mac）
pip install -r requirements_auto.txt
```

### 2. ペルソナ学習
```bash
python main.py learn "path/to/x-archive"
```

## 使い方

### 投稿生成

```bash
python main.py x-post --type specialty --day mon --topic "猫の熱中症"
```

#### パラメータ

- `--type`: 投稿タイプ
  - `cat-breed`: 猫種特集
  - `specialty`: 専門テーマ
  - `interactive`: 参加型コンテンツ
  
- `--day`: 曜日
  - `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`
  
- `--topic`: 投稿トピック（文字列）

### 使用例

```bash
# 月曜日の専門テーマ投稿
python main.py x-post --type specialty --day mon --topic "猫の腎臓病"

# 火曜日の猫種特集投稿
python main.py x-post --type cat-breed --day tue --topic "アメリカンショートヘア"

# 水曜日の参加型投稿
python main.py x-post --type interactive --day wed --topic "猫の変な癖"
```

## 投稿サイクル

### 猫種特集週（4週に1回）
- 月曜: 猫種の概要紹介
- 火曜: 歴史・起源
- 水曜: 性格
- 木曜: 体型や被毛などの身体的特徴
- 金曜: 特有の健康上の注意点
- 土曜: 日常的なケアのポイント
- 日曜: 参加型の投稿

### 専門テーマ週（1.5～2ヶ月に1回）
- 月曜: テーマの概要
- 火曜: 原因や初期症状
- 水曜: 進行時の症状や合併症
- 木曜: 診断方法
- 金曜: 治療・管理方法
- 土曜: お家でできるケア
- 日曜: 総括、予防の重要性

### 参加型コンテンツ強化週
- 平日: 質問→回答のペア投稿
- 土日: 単発の緩い内容

## 投稿ルール

1. **文字数**: 140文字以内（改行除く、絵文字・記号・ハッシュタグ含む）
2. **ハッシュタグ**: 必ず `#猫のあれこれ` を含める
3. **タイトル**: 「獣医師が教える！【トピック名】【絵文字】」形式
4. **言葉遣い**: 高校生でも理解できる平易な表現
5. **構成**: 箇条書き（✅、💡、🐾など）を効果的に使用

## ファイル構成

```
VET-ASSISTANT-CLI/
├── main.py              # メインアプリケーション
├── requirements.txt     # 依存関係
├── config.json         # 設定ファイル（自動生成）
├── persona_data.json   # ペルソナデータ（自動生成）
└── README.md           # このファイル
```

## 作者

@souhei1219 - 19年目の救急獣医師（犬猫専門）