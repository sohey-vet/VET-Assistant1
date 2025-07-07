#!/usr/bin/env python3
"""
VET-ASSISTANT-CLI: AI投稿生成アプリケーション
@souhei1219のX投稿を半自動生成するCLIツール
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime
from pathlib import Path
import google.generativeai as genai

class VetAssistantCLI:
    def __init__(self):
        self.config_file = Path("config.json")
        self.persona_file = Path("persona_data.json")
        self.api_key = "AIzaSyAA0eEtEXToBEtZSrdllKJYZdkHQDrfgik"
        self.persona_data = {}
        self.load_config()
        self.setup_gemini()
    
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
    
    def setup_gemini(self):
        """Gemini APIの設定"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def count_characters(self, text):
        """
        文字数カウント（改行除外）
        絵文字・記号・ハッシュタグ含む全角文字を1文字としてカウント
        """
        # 改行を除外
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
    
    def analyze_persona(self, tweets):
        """投稿データからペルソナを分析"""
        print("🔍 ペルソナ分析を開始します...")
        
        # 投稿テキストを結合
        tweet_texts = []
        for tweet in tweets:
            if 'tweet' in tweet and 'full_text' in tweet['tweet']:
                tweet_texts.append(tweet['tweet']['full_text'])
        
        # 最新の1000件を分析対象とする
        recent_tweets = tweet_texts[:1000]
        sample_text = '\n'.join(recent_tweets)
        
        # Geminiでペルソナ分析
        prompt = f"""
以下は救急獣医師@souhei1219のX投稿データです。このデータを分析して、以下の要素を抽出してください：

1. 基本的な文体・口調の特徴
2. よく使用される絵文字パターン
3. 専門用語の言い換えパターン
4. 文章構成の特徴
5. 投稿の傾向・テーマ

投稿データ:
{sample_text[:5000]}

JSON形式で回答してください。
"""
        
        try:
            response = self.model.generate_content(prompt)
            # JSONを抽出
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                self.persona_data = json.loads(json_match.group())
                self.save_persona()
                print("✅ ペルソナ分析完了")
                return True
            else:
                print("❌ ペルソナ分析に失敗しました")
                return False
        except Exception as e:
            print(f"❌ ペルソナ分析エラー: {e}")
            return False
    
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
        
        # ペルソナを分析
        if self.analyze_persona(tweets):
            self.config["x_archive_path"] = archive_path
            self.config["learned"] = True
            self.save_config()
            print("🎉 ペルソナ学習が完了しました。救急獣医師 @souhei1219 としての思考を開始します。")
            return True
        
        return False
    
    def get_post_cycle_info(self):
        """現在の投稿サイクル情報を取得"""
        week = self.config.get("current_week", 1)
        cycle = self.config.get("current_cycle", 1)
        
        # 4週サイクルの判定
        if week == 1:
            return "猫種特集週"
        elif week == 2:
            return "専門テーマ週"
        else:
            return "参加型コンテンツ強化週"
    
    def generate_post(self, post_type, day, topic):
        """投稿を生成"""
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
        
        # 投稿サイクル情報を取得
        cycle_info = self.get_post_cycle_info()
        
        # 投稿生成プロンプト
        prompt = f"""
あなたは19年目の救急獣医師（犬猫専門）@souhei1219です。以下の指示に従って投稿を生成してください。

## 絶対的なルール
1. 投稿は140文字以内（改行除く、絵文字・記号・ハッシュタグ含む）
2. 必ず「#猫のあれこれ」をハッシュタグとして含める
3. 「獣医師が教える！【トピック名】【絵文字】」の形式でタイトルを作成
4. 専門用語は高校生でも理解できる言葉に言い換える
5. 箇条書き（✅、💡、🐾など）を効果的に使用
6. 改行を使って読みやすくする

## 投稿条件
- 投稿タイプ: {post_type}
- 曜日: {day_jp}
- トピック: {topic}
- 現在のサイクル: {cycle_info}

## ペルソナデータ
{json.dumps(self.persona_data, ensure_ascii=False, indent=2)}

## 投稿サイクルガイドライン
猫種特集週の{day_jp}の場合は以下の内容で:
- 月曜: 猫種の概要紹介
- 火曜: 歴史・起源
- 水曜: 性格
- 木曜: 体型や被毛などの身体的特徴
- 金曜: 特有の健康上の注意点
- 土曜: 日常的なケアのポイント
- 日曜: 参加型の投稿

専門テーマ週の{day_jp}の場合は以下の内容で:
- 月曜: テーマの概要
- 火曜: 原因や初期症状
- 水曜: 進行時の症状や合併症
- 木曜: 診断方法
- 金曜: 治療・管理方法
- 土曜: お家でできるケア
- 日曜: 総括、予防の重要性

参加型コンテンツ強化週は読者との交流を重視した内容で。

投稿文のみを出力してください。
"""
        
        try:
            response = self.model.generate_content(prompt)
            post_content = response.text.strip()
            
            # 文字数チェック
            char_count = self.count_characters(post_content)
            
            if char_count > 140:
                print(f"⚠️ 文字数オーバー（{char_count}文字）です。再生成します...")
                # 短縮版を生成
                short_prompt = prompt + "\n\n※140文字を超過しました。より簡潔に生成してください。"
                response = self.model.generate_content(short_prompt)
                post_content = response.text.strip()
                char_count = self.count_characters(post_content)
            
            return post_content, char_count
        
        except Exception as e:
            print(f"❌ 投稿生成エラー: {e}")
            return None, 0
    
    def x_post_command(self, post_type, day, topic):
        """x-postコマンドの実行"""
        print(f"📝 投稿を生成中... (タイプ: {post_type}, 曜日: {day}, トピック: {topic})")
        
        result = self.generate_post(post_type, day, topic)
        if result:
            post_content, char_count = result
            print("\n" + "="*50)
            print("📋 生成された投稿:")
            print("="*50)
            print(post_content)
            print("="*50)
            print(f"文字数: ({char_count}文字)")
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