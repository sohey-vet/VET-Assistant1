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
from duplicate_checker import DuplicateChecker

class VetAssistantCLI:
    def __init__(self):
        self.config_file = Path("config.json")
        self.persona_file = Path("persona_data.json")
        self.api_key = "AIzaSyAA0eEtEXToBEtZSrdllKJYZdkHQDrfgik"
        self.persona_data = {}
        self.duplicate_checker = DuplicateChecker()
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
    
    def generate_post(self, post_type, day, topic, max_attempts=3):
        """投稿を生成（重複チェック付き）"""
        if not self.config.get("learned", False):
            print("❌ 先にlearnコマンドを実行してください")
            return None
        
        if not self.load_persona():
            print("❌ ペルソナデータが見つかりません")
            return None
        
        # 重複チェックを含む投稿生成を試行
        for attempt in range(max_attempts):
            print(f"🔄 投稿生成試行 {attempt + 1}/{max_attempts}")
            
            post_content, char_count = self._generate_single_post(post_type, day, topic)
            if not post_content:
                continue
            
            # 重複チェック実行
            print("🔍 重複チェック実行中...")
            is_duplicate, duplicate_info = self.duplicate_checker.check_duplicate(
                post_content, topic, post_type, similarity_threshold=0.7
            )
            
            if not is_duplicate:
                print("✅ 重複なし - 投稿を承認")
                # 投稿を履歴に保存
                self.duplicate_checker.save_post(post_content, topic, post_type, day)
                return post_content, char_count
            else:
                print(f"⚠️ 重複検出 - {len(duplicate_info)}件の類似投稿が見つかりました")
                self._show_duplicate_info(duplicate_info)
                
                if attempt < max_attempts - 1:
                    print("🔄 投稿を再生成します...")
                    # より具体的な指示で再生成
                    topic = f"{topic} (別のアプローチ)"
        
        print("❌ 重複のない投稿を生成できませんでした")
        return None, 0
        
    def _generate_single_post(self, post_type, day, topic):
        """単一投稿を生成（内部メソッド）"""
        # 曜日を日本語に変換
        day_map = {
            "mon": "月曜日", "tue": "火曜日", "wed": "水曜日", 
            "thu": "木曜日", "fri": "金曜日", "sat": "土曜日", "sun": "日曜日"
        }
        day_jp = day_map.get(day, day)
        
        # 投稿サイクル情報を取得
        cycle_info = self.get_post_cycle_info()
        
        # 既存の投稿履歴を取得して重複を避ける指示を追加
        recent_posts = self.duplicate_checker.get_post_history(10)
        recent_topics = [post['topic'] for post in recent_posts if post['topic']]
        recent_keywords = []
        for post in recent_posts:
            recent_keywords.extend(post.get('keywords', []))
        
        avoid_instruction = ""
        if recent_topics:
            avoid_instruction += f"\n\n## 重複回避指示\n最近の投稿トピック: {', '.join(recent_topics[:5])}\n"
        if recent_keywords:
            common_keywords = [k for k, v in Counter(recent_keywords).most_common(10)]
            avoid_instruction += f"よく使われたキーワード: {', '.join(common_keywords)}\n"
            avoid_instruction += "上記のトピックやキーワードと重複しないよう、新しい視点や表現を使用してください。"
        
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
7. 過去の投稿と重複しないよう、独自性のある内容にする

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

参加型コンテンツ強化週は読者との交流を重視した内容で。{avoid_instruction}

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
    
    def _show_duplicate_info(self, duplicate_info):
        """重複情報を表示"""
        print("\n📋 重複検出詳細:")
        print("="*60)
        
        for i, dup in enumerate(duplicate_info[:3], 1):  # 上位3件を表示
            print(f"\n{i}. 類似度: {dup['similarity']:.2f} ({dup['type']})")
            print(f"   トピック: {dup['topic']}")
            print(f"   作成日: {dup['created_at']}")
            print(f"   内容: {dup['content'][:50]}{'...' if len(dup['content']) > 50 else ''}")
        
        print("="*60)
    
    def show_post_history(self, limit=10):
        """投稿履歴を表示"""
        posts = self.duplicate_checker.get_post_history(limit)
        
        if not posts:
            print("📝 投稿履歴がありません")
            return
        
        print(f"\n📋 最近の投稿履歴 (最新{len(posts)}件):")
        print("="*80)
        
        for post in posts:
            print(f"\n📅 {post['created_at']}")
            print(f"📝 トピック: {post['topic']}")
            print(f"🏷️  タイプ: {post['post_type']} ({post['day']})")
            print(f"📊 文字数: {post['char_count']}")
            print(f"🔍 キーワード: {', '.join(post['keywords'][:5])}")
            print(f"💬 内容: {post['content'][:60]}{'...' if len(post['content']) > 60 else ''}")
            print("-" * 80)
    
    def clean_old_posts(self, days=90):
        """古い投稿を削除"""
        return self.duplicate_checker.clean_old_posts(days)

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
    
    # historyコマンド
    history_parser = subparsers.add_parser('history', help='投稿履歴表示')
    history_parser.add_argument('--limit', type=int, default=10, help='表示件数（デフォルト: 10）')
    
    # cleanコマンド
    clean_parser = subparsers.add_parser('clean', help='古い投稿履歴を削除')
    clean_parser.add_argument('--days', type=int, default=90, help='保持日数（デフォルト: 90日）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    app = VetAssistantCLI()
    
    if args.command == 'learn':
        app.learn_command(args.archive_path)
    elif args.command == 'x-post':
        app.x_post_command(args.type, args.day, args.topic)
    elif args.command == 'history':
        app.show_post_history(args.limit)
    elif args.command == 'clean':
        app.clean_old_posts(args.days)

if __name__ == "__main__":
    main()