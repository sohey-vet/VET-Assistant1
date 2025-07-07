#!/usr/bin/env python3
"""
VET-ASSISTANT-CLI: AI投稿生成アプリケーション (簡易版)
Geminiライブラリが利用できない環境でのテスト用
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path

class VetAssistantCLI:
    def __init__(self):
        self.config_file = Path("config.json")
        self.persona_file = Path("persona_data.json")
        self.persona_data = {}
        self.load_config()
    
    def load_config(self):
        """設定ファイルを読み込み"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "x_archive_path": "",
                "learned": False,
                "last_post_type": "",
                "current_week": 1,
                "current_cycle": 1
            }
            self.save_config()
    
    def save_config(self):
        """設定ファイルを保存"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def count_characters(self, text):
        """
        文字数カウント（改行除外）
        """
        text_without_newlines = text.replace('\n', '')
        return len(text_without_newlines)
    
    def load_x_archive(self, archive_path):
        """Xアーカイブデータを読み込み"""
        try:
            tweets_file = Path(archive_path) / "data" / "tweets.js"
            if not tweets_file.exists():
                print(f"❌ tweets.jsファイルが見つかりません: {tweets_file}")
                return None
            
            with open(tweets_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # JavaScriptファイルからJSONデータを抽出
                json_start = content.find('[')
                json_data = content[json_start:]
                tweets = json.loads(json_data)
                print(f"✅ {len(tweets)}件の投稿データを読み込みました")
                return tweets
        except Exception as e:
            print(f"❌ アーカイブの読み込みに失敗しました: {e}")
            return None
    
    def analyze_persona_simple(self, tweets):
        """投稿データからペルソナを簡易分析（Gemini無し版）"""
        print("🔍 ペルソナ分析を開始します...")
        
        # 投稿テキストを結合
        tweet_texts = []
        emoji_count = {}
        for tweet in tweets:
            if 'tweet' in tweet and 'full_text' in tweet['tweet']:
                text = tweet['tweet']['full_text']
                tweet_texts.append(text)
                
                # 絵文字パターンを分析
                emojis = re.findall(r'[🐾💡✅🚨🤔🏥🏆😊😺🐱🩺📚⚠️🔥💯👨‍⚕️]', text)
                for emoji in emojis:
                    emoji_count[emoji] = emoji_count.get(emoji, 0) + 1
        
        # よく使われる絵文字トップ5
        top_emojis = sorted(emoji_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # ペルソナデータを構築
        self.persona_data = {
            "基本プロフィール": "19年目の犬猫専門救急獣医師、FP2級取得",
            "文体特徴": "です・ます調、丁寧で親しみやすい",
            "専門性": "専門用語を平易な言葉に言い換える",
            "よく使う絵文字": [emoji for emoji, count in top_emojis],
            "文章構成": "結論ファースト、箇条書き活用",
            "投稿総数": len(tweets),
            "分析日": datetime.now().isoformat()
        }
        
        self.save_persona()
        print("✅ ペルソナ分析完了（簡易版）")
        print(f"   - 投稿総数: {len(tweets)}件")
        print(f"   - よく使う絵文字: {', '.join([emoji for emoji, count in top_emojis[:3]])}")
        return True
    
    def save_persona(self):
        """ペルソナデータを保存"""
        with open(self.persona_file, 'w', encoding='utf-8') as f:
            json.dump(self.persona_data, f, ensure_ascii=False, indent=2)
    
    def load_persona(self):
        """ペルソナデータを読み込み"""
        if self.persona_file.exists():
            with open(self.persona_file, 'r', encoding='utf-8') as f:
                self.persona_data = json.load(f)
                return True
        return False
    
    def learn_command(self, archive_path):
        """learnコマンドの実行"""
        print("🎓 ペルソナ学習を開始します...")
        
        # Xアーカイブを読み込み
        tweets = self.load_x_archive(archive_path)
        if not tweets:
            return False
        
        # ペルソナを分析（簡易版）
        if self.analyze_persona_simple(tweets):
            self.config["x_archive_path"] = archive_path
            self.config["learned"] = True
            self.save_config()
            print("🎉 ペルソナ学習が完了しました。救急獣医師 @souhei1219 としての思考を開始します。")
            return True
        
        return False
    
    def get_post_cycle_info(self):
        """現在の投稿サイクル情報を取得"""
        week = self.config.get("current_week", 1)
        
        if week == 1:
            return "猫種特集週"
        elif week == 2:
            return "専門テーマ週"
        else:
            return "参加型コンテンツ強化週"
    
    def generate_post_template(self, post_type, day, topic):
        """投稿テンプレートを生成（Gemini無し版）"""
        if not self.config.get("learned", False):
            print("❌ 先にlearnコマンドを実行してください")
            return None
        
        if not self.load_persona():
            print("❌ ペルソナデータが見つかりません")
            return None
        
        # 曜日を日本語に変換
        day_map = {
            "mon": "月曜日", "tue": "火曜日", "wed": "水曜日", 
            "thu": "木曜日", "fri": "金曜日", "sat": "土曜日", "sun": "日曜日"
        }
        day_jp = day_map.get(day, day)
        
        # よく使う絵文字を取得
        emojis = self.persona_data.get("よく使う絵文字", ["🐾", "💡", "✅"])
        main_emoji = emojis[0] if emojis else "🐾"
        
        # テンプレート生成
        if post_type == "specialty":
            if day == "mon":
                template = f"""獣医師が教える！【{topic}】{main_emoji}

{topic}について大切なポイントをお話しします。

✅ まずは基本的な知識から
💡 早期発見が重要です
{main_emoji} 愛猫の健康を守りましょう

#猫のあれこれ"""
            
            elif day == "tue":
                template = f"""獣医師が教える！【{topic}の原因と初期症状】{main_emoji}

{topic}の初期症状を見逃さないために：

✅ こんな症状があったら要注意
💡 早めの対処が大切
🚨 気になったらすぐ受診を

#猫のあれこれ"""
            
            else:
                template = f"""獣医師が教える！【{topic}】{main_emoji}

{topic}について獣医師が解説します。

✅ 重要なポイント
💡 お家でできること
{main_emoji} 愛猫の健康管理

#猫のあれこれ"""
        
        elif post_type == "cat-breed":
            template = f"""獣医師が教える！【{topic}】{main_emoji}

{topic}の特徴について：

✅ 性格の特徴
💡 健康管理のポイント
{main_emoji} 飼育のコツ

#猫のあれこれ"""
        
        elif post_type == "interactive":
            template = f"""獣医師が教える！【{topic}】{main_emoji}

みなさんの愛猫はどうですか？

✅ こんな経験ありませんか？
💡 皆さんの体験談をお聞かせください
{main_emoji} コメントでお待ちしています

#猫のあれこれ"""
        
        else:
            template = f"""獣医師が教える！【{topic}】{main_emoji}

{topic}について大切なお話です。

✅ 知っておくべきポイント
💡 日頃のケアが重要
{main_emoji} 愛猫の健康を守りましょう

#猫のあれこれ"""
        
        return template
    
    def x_post_command(self, post_type, day, topic):
        """x-postコマンドの実行"""
        print(f"📝 投稿を生成中... (タイプ: {post_type}, 曜日: {day}, トピック: {topic})")
        
        post_content = self.generate_post_template(post_type, day, topic)
        if post_content:
            char_count = self.count_characters(post_content)
            
            print("\n" + "="*50)
            print("📋 生成された投稿:")
            print("="*50)
            print(post_content)
            print("="*50)
            print(f"文字数: ({char_count}文字)")
            if char_count > 140:
                print("⚠️ 140文字を超過しています。内容を調整してください。")
            print("="*50)
            
            # 設定更新
            self.config["last_post_type"] = post_type
            self.save_config()
            
            return post_content
        else:
            print("❌ 投稿生成に失敗しました")
            return None

def main():
    parser = argparse.ArgumentParser(description="VET-ASSISTANT-CLI: AI投稿生成アプリケーション")
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # learnコマンド
    learn_parser = subparsers.add_parser('learn', help='ペルソナ学習')
    learn_parser.add_argument('archive_path', help='Xアーカイブフォルダのパス')
    
    # x-postコマンド
    xpost_parser = subparsers.add_parser('x-post', help='投稿生成')
    xpost_parser.add_argument('--type', choices=['cat-breed', 'specialty', 'interactive'], 
                             required=True, help='投稿タイプ')
    xpost_parser.add_argument('--day', choices=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], 
                             required=True, help='曜日')
    xpost_parser.add_argument('--topic', required=True, help='トピック')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    app = VetAssistantCLI()
    
    if args.command == 'learn':
        app.learn_command(args.archive_path)
    elif args.command == 'x-post':
        app.x_post_command(args.type, args.day, args.topic)

if __name__ == "__main__":
    main()