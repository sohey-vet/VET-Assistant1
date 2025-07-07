# VET-ASSISTANT-CLI 完全自動投稿システム

@souhei1219の完全自動投稿システム - 週間記事生成からExcel編集、毎朝7時自動投稿まで

## 🚀 特徴

- **完全自動化**: 指示一つで1週間分の記事を生成
- **Excel編集**: 生成後にExcelで内容を確認・修正可能
- **自動投稿**: 毎朝7時に`#猫のあれこれ`ハッシュタグ付き記事を自動投稿
- **投稿サイクル管理**: 猫種特集週・専門テーマ週・参加型強化週の自動ローテーション
- **ステータス管理**: 投稿状況をExcelで管理

## 📋 システムフロー

```
1. 週間記事生成 → 2. Excel確認・編集 → 3. 自動投稿開始 → 4. 毎朝7時投稿
```

## 🛠️ セットアップ

### 1. 初期セットアップ
```bash
setup_auto.bat
```

### 2. ペルソナ学習（初回のみ）
```bash
python main.py learn "C:\Users\souhe\Desktop\X過去投稿"
```

### 3. Twitter API設定（初回のみ）
```bash
setup_twitter.bat
```
または
```bash
python auto_post_system.py setup-twitter
```

## 📝 使い方

### 週間記事生成
```bash
# 簡単実行
generate_week.bat

# コマンドライン
python auto_post_system.py generate-week
python auto_post_system.py generate-week --topic "猫の腎臓病"
```

### Excel編集
1. `投稿スケジュール.xlsx` を開く
2. 記事内容を確認・修正
3. `#猫のあれこれ` ハッシュタグが含まれていることを確認
4. ステータスを「編集待ち」から「予約中」に変更

### 自動投稿開始
```bash
# 簡単実行
start_scheduler.bat

# コマンドライン
python auto_post_system.py start-scheduler
```

## 📊 Excelファイル構成

| 列 | 内容 | 説明 |
|---|---|---|
| 日付 | 2025-07-08 | 投稿予定日 |
| 曜日 | 月曜日 | 曜日 |
| 投稿タイプ | specialty | specialty/cat-breed/interactive |
| テーマ | 概要 | 曜日別テーマ |
| トピック | 猫の腎臓病（概要） | 投稿トピック |
| 投稿内容 | 獣医師が教える！【...】 | 実際の投稿文 |
| 文字数 | 85文字 | 文字数カウント |
| ステータス | 予約中 | 編集待ち/予約中/投稿済み |
| 投稿時間 | 07:00 | 投稿予定時刻 |

## 🗓️ 投稿サイクル

### 猫種特集週（4週に1回）
- **月曜**: 猫種の概要紹介
- **火曜**: 歴史・起源
- **水曜**: 性格
- **木曜**: 身体的特徴
- **金曜**: 健康上の注意点
- **土曜**: ケアのポイント
- **日曜**: 参加型投稿

### 専門テーマ週（1.5～2ヶ月に1回）
- **月曜**: テーマの概要
- **火曜**: 原因・初期症状
- **水曜**: 進行症状・合併症
- **木曜**: 診断方法
- **金曜**: 治療・管理方法
- **土曜**: 家庭でのケア
- **日曜**: 予防・総括

### 参加型コンテンツ強化週
- **月曜**: クイズ
- **火曜**: クイズ解説
- **水曜**: アンケート
- **木曜**: アンケート結果
- **金曜**: 事例紹介
- **土曜**: 豆知識
- **日曜**: 体験談募集

## ⚙️ 設定

### Twitter API設定
```json
{
  "twitter_api_key": "あなたのAPIキー",
  "twitter_api_secret": "あなたのAPIシークレット",
  "twitter_access_token": "あなたのアクセストークン",
  "twitter_access_token_secret": "あなたのアクセストークンシークレット",
  "twitter_bearer_token": "あなたのベアラートークン"
}
```

### 投稿ルール
- **文字数**: 140文字以内（改行除く）
- **ハッシュタグ**: `#猫のあれこれ` 必須
- **投稿時間**: 毎朝7時
- **フィルタ**: ハッシュタグ付きのみ投稿

## 🔧 コマンドリファレンス

### 記事生成
```bash
python auto_post_system.py generate-week [--topic トピック] [--start-date YYYY-MM-DD]
```

### スケジューラー
```bash
python auto_post_system.py start-scheduler
```

### Twitter設定
```bash
python auto_post_system.py setup-twitter
```

### テスト投稿
```bash
python auto_post_system.py test-post "テスト投稿内容"
```

## 📁 ファイル構成

```
VET-ASSISTANT-CLI/
├── auto_post_system.py          # メインシステム
├── main.py                      # 基本機能
├── requirements_auto.txt        # 依存関係
├── setup_auto.bat              # 初期セットアップ
├── generate_week.bat           # 週間記事生成
├── start_scheduler.bat         # スケジューラー開始
├── setup_twitter.bat           # Twitter API設定
├── config.json                 # 設定ファイル（自動生成）
├── persona_data.json           # ペルソナデータ（自動生成）
├── 投稿スケジュール.xlsx        # 投稿スケジュール（自動生成）
└── README_AUTO.md              # このファイル
```

## 🚨 注意事項

1. **Twitter API制限**: 投稿頻度に注意
2. **Excel編集**: 必ず`#猫のあれこれ`ハッシュタグを含める
3. **文字数制限**: 140文字以内（改行除く）
4. **バックアップ**: 重要な投稿は手動でバックアップ

## 🔍 トラブルシューティング

### よくある問題

**Q: 投稿されない**
A: Excelで`#猫のあれこれ`ハッシュタグとステータスを確認

**Q: Twitter API エラー**
A: `setup_twitter.bat`でAPI認証情報を再設定

**Q: 文字数オーバー**
A: Excelで投稿内容を140文字以内に修正

**Q: スケジューラーが停止**
A: `start_scheduler.bat`を再実行

## 📞 サポート

システムに関する質問や改善要望があれば、お気軽にお知らせください。

---

**作者**: @souhei1219 - 19年目の救急獣医師（犬猫専門）