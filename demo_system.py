#!/usr/bin/env python3
"""
VET-ASSISTANT-CLI: デモ版自動投稿システム
ライブラリ依存なしでローカル動作確認用
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

class DemoAutoPostSystem:
    def __init__(self):
        self.config_file = Path("config.json")
        self.persona_file = Path("persona_data.json")
        self.persona_data = {}
        self.load_config()
        self.load_persona()
        
    def load_config(self):
        """設定ファイルを読み込み"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "learned": False,
                "current_week_type": "specialty"
            }
    
    def load_persona(self):
        """ペルソナデータを読み込み"""
        if self.persona_file.exists():
            with open(self.persona_file, 'r', encoding='utf-8') as f:
                self.persona_data = json.load(f)
                return True
        else:
            # デモ用ペルソナデータ
            self.persona_data = {
                "基本プロフィール": "19年目の犬猫専門救急獣医師、FP2級取得",
                "よく使う絵文字": ["🐱", "✅", "💡", "🐾", "🚨"],
                "投稿総数": 7581
            }
            return True
    
    def count_characters(self, text):
        """文字数カウント（改行除外）"""
        return len(text.replace('\n', ''))
    
    def get_week_schedule(self):
        """週間投稿スケジュールを決定"""
        week_type = self.config.get("current_week_type", "specialty")
        
        if week_type == "cat-breed":
            return {
                "mon": ("cat-breed", "概要紹介"),
                "tue": ("cat-breed", "歴史・起源"),
                "wed": ("cat-breed", "性格"),
                "thu": ("cat-breed", "身体的特徴"),
                "fri": ("cat-breed", "健康上の注意点"),
                "sat": ("cat-breed", "ケアのポイント"),
                "sun": ("interactive", "参加型投稿")
            }
        elif week_type == "specialty":
            return {
                "mon": ("specialty", "概要"),
                "tue": ("specialty", "原因・初期症状"),
                "wed": ("specialty", "進行症状・合併症"),
                "thu": ("specialty", "診断方法"),
                "fri": ("specialty", "治療・管理方法"),
                "sat": ("specialty", "家庭でのケア"),
                "sun": ("specialty", "予防・総括")
            }
        else:  # interactive
            return {
                "mon": ("interactive", "クイズ"),
                "tue": ("interactive", "クイズ解説"),
                "wed": ("interactive", "アンケート"),
                "thu": ("interactive", "アンケート結果"),
                "fri": ("interactive", "事例紹介"),
                "sat": ("specialty", "豆知識"),
                "sun": ("interactive", "体験談募集")
            }
    
    def generate_week_posts(self, start_date=None, base_topic=None):
        """1週間分の投稿を生成"""
        print("📝 1週間分の投稿を生成中...")
        
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # 次の月曜日から開始
            days_ahead = 0 - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            start_date += timedelta(days=days_ahead)
        
        week_schedule = self.get_week_schedule()
        posts_data = []
        
        day_names = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        japanese_days = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
        
        print(f"📅 生成期間: {start_date.strftime('%Y-%m-%d')} ～ {(start_date + timedelta(days=6)).strftime('%Y-%m-%d')}")
        print(f"📊 投稿サイクル: {self.config.get('current_week_type', 'specialty')}週")
        print()
        
        for i, day in enumerate(day_names):
            post_date = start_date + timedelta(days=i)
            post_type, theme = week_schedule[day]
            
            # トピックを決定
            if base_topic:
                if post_type == "cat-breed":
                    topic = f"{base_topic}（{theme}）"
                elif post_type == "specialty":
                    topic = f"{base_topic}（{theme}）"
                else:
                    topic = base_topic
            else:
                # デフォルトトピック
                if post_type == "cat-breed":
                    topic = f"アメリカンショートヘア（{theme}）"
                elif post_type == "specialty":
                    topic = f"猫の腎臓病（{theme}）"
                else:
                    topic = "猫の健康管理"
            
            # 投稿内容を生成
            content = self.generate_single_post(post_type, day, topic)
            char_count = self.count_characters(content)
            
            posts_data.append({
                "日付": post_date.strftime("%Y-%m-%d"),
                "曜日": japanese_days[i],
                "投稿タイプ": post_type,
                "テーマ": theme,
                "トピック": topic,
                "投稿内容": content,
                "文字数": char_count,
                "ステータス": "編集待ち",
                "投稿時間": "07:00"
            })
            
            print(f"✅ {japanese_days[i]}: {topic} ({char_count}文字)")
        
        return posts_data
    
    def generate_single_post(self, post_type, day, topic):
        """単一投稿を生成"""
        emojis = self.persona_data.get("よく使う絵文字", ["🐱", "✅", "💡"])
        main_emoji = emojis[0] if emojis else "🐱"
        
        if post_type == "specialty":
            if "概要" in topic:
                content = f"""獣医師が教える！【{topic}】{main_emoji}

{topic.split('（')[0]}について大切なポイントをお話しします。

✅ まずは基本的な知識から
💡 早期発見が重要です
{main_emoji} 愛猫の健康を守りましょう

#猫のあれこれ"""
            
            elif "初期症状" in topic:
                content = f"""獣医師が教える！【{topic}】{main_emoji}

初期症状を見逃さないために：

✅ こんな症状があったら要注意
💡 早めの対処が大切
🚨 気になったらすぐ受診を

#猫のあれこれ"""
            
            elif "診断" in topic:
                content = f"""獣医師が教える！【{topic}】{main_emoji}

正確な診断のために：

✅ 獣医師による検査が必要
💡 症状の詳細を伝えることが大切
{main_emoji} 早期診断で適切な治療を

#猫のあれこれ"""
            
            elif "治療" in topic:
                content = f"""獣医師が教える！【{topic}】{main_emoji}

治療方法について：

✅ 獣医師の指示に従いましょう
💡 継続的な管理が重要
{main_emoji} 愛猫の回復を支えましょう

#猫のあれこれ"""
            
            elif "ケア" in topic:
                content = f"""獣医師が教える！【{topic}】{main_emoji}

お家でできるケア：

✅ 日常的な観察が大切
💡 環境づくりを工夫しましょう
{main_emoji} 愛猫が快適に過ごせるように

#猫のあれこれ"""
            
            else:
                content = f"""獣医師が教える！【{topic}】{main_emoji}

{topic.split('（')[0]}について：

✅ 重要なポイント
💡 予防が何より大切
{main_emoji} 愛猫の健康を守りましょう

#猫のあれこれ"""
        
        elif post_type == "cat-breed":
            content = f"""獣医師が教える！【{topic}】{main_emoji}

{topic.split('（')[0]}の特徴について：

✅ 性格と特徴
💡 健康管理のポイント
{main_emoji} 飼育のコツ

#猫のあれこれ"""
        
        elif post_type == "interactive":
            if "クイズ" in topic:
                content = f"""獣医師が教える！【猫の健康クイズ】{main_emoji}

今日はクイズです！

✅ 愛猫の健康チェック
💡 正解は明日発表します
{main_emoji} コメントで回答をお待ちしています

#猫のあれこれ"""
            
            elif "アンケート" in topic:
                content = f"""獣医師が教える！【愛猫アンケート】{main_emoji}

みなさんの愛猫について教えてください：

✅ どんな猫種ですか？
💡 皆さんの回答を集計します
{main_emoji} コメントでお聞かせください

#猫のあれこれ"""
            
            else:
                content = f"""獣医師が教える！【愛猫の体験談】{main_emoji}

みなさんの愛猫はどうですか？

✅ こんな経験ありませんか？
💡 皆さんの体験談をお聞かせください
{main_emoji} コメントでお待ちしています

#猫のあれこれ"""
        
        return content
    
    def save_to_csv(self, posts_data):
        """CSVファイルに保存（Excel代替）"""
        try:
            csv_file = Path("投稿スケジュール.csv")
            
            # CSVヘッダー
            headers = ["日付", "曜日", "投稿タイプ", "テーマ", "トピック", "投稿内容", "文字数", "ステータス", "投稿時間"]
            
            with open(csv_file, 'w', encoding='utf-8-sig') as f:
                # ヘッダー書き込み
                f.write(','.join(headers) + '\n')
                
                # データ書き込み
                for post in posts_data:
                    row = []
                    for header in headers:
                        value = str(post.get(header, ''))
                        # CSVエスケープ処理
                        if ',' in value or '"' in value or '\n' in value:
                            value = '"' + value.replace('"', '""') + '"'
                        row.append(value)
                    f.write(','.join(row) + '\n')
            
            print(f"✅ CSVファイルに保存しました: {csv_file}")
            return True
            
        except Exception as e:
            print(f"❌ CSV保存エラー: {e}")
            return False
    
    def display_posts(self, posts_data):
        """投稿内容を表示"""
        print("\n" + "="*80)
        print("📋 生成された週間投稿スケジュール")
        print("="*80)
        
        for post in posts_data:
            print(f"\n📅 【{post['日付']} ({post['曜日']})】")
            print(f"🏷️  タイプ: {post['投稿タイプ']} | テーマ: {post['テーマ']}")
            print(f"📝 トピック: {post['トピック']}")
            print("-" * 50)
            print(post['投稿内容'])
            print("-" * 50)
            print(f"📊 文字数: {post['文字数']}文字 | ステータス: {post['ステータス']}")
        
        print("\n" + "="*80)
        print("✅ 週間投稿生成完了！")
        print("💡 投稿スケジュール.csv を確認して編集してください")
        print("📌 #猫のあれこれ ハッシュタグが含まれている投稿が自動投稿対象です")
        print("="*80)

def main():
    parser = argparse.ArgumentParser(description="VET-ASSISTANT-CLI: デモ版自動投稿システム")
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # generate-weekコマンド
    week_parser = subparsers.add_parser('generate-week', help='1週間分の投稿を生成')
    week_parser.add_argument('--topic', help='基本トピック（例: 猫の腎臓病）')
    week_parser.add_argument('--start-date', help='開始日（YYYY-MM-DD）')
    
    # infoコマンド
    info_parser = subparsers.add_parser('info', help='システム情報表示')
    
    args = parser.parse_args()
    
    if not args.command:
        print("🐾 VET-ASSISTANT-CLI デモ版自動投稿システム")
        print("==========================================")
        print()
        print("利用可能なコマンド:")
        print("  generate-week  - 1週間分の投稿を生成")
        print("  info          - システム情報表示")
        print()
        print("使用例:")
        print("  python demo_system.py generate-week")
        print("  python demo_system.py generate-week --topic '猫の夏対策'")
        print()
        return
    
    app = DemoAutoPostSystem()
    
    if args.command == 'generate-week':
        start_date = None
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        
        posts_data = app.generate_week_posts(start_date, args.topic)
        
        if posts_data:
            app.display_posts(posts_data)
            app.save_to_csv(posts_data)
        else:
            print("❌ 投稿生成に失敗しました")
    
    elif args.command == 'info':
        print("🐾 VET-ASSISTANT-CLI システム情報")
        print("=================================")
        print(f"ペルソナ学習状況: {'学習済み' if app.persona_data else '未学習'}")
        print(f"投稿データ数: {app.persona_data.get('投稿総数', 0)}件")
        print(f"よく使う絵文字: {', '.join(app.persona_data.get('よく使う絵文字', []))}")
        print(f"現在のサイクル: {app.config.get('current_week_type', 'specialty')}週")

if __name__ == "__main__":
    main()