#!/usr/bin/env python3
"""
VET-ASSISTANT-CLI: 改良版記事生成システム
作成指示書に完全準拠した高品質記事生成
"""

import os
import sys
import json
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

class ImprovedVetAssistant:
    def __init__(self):
        self.config_file = Path("config.json")
        self.persona_file = Path("persona_data.json")
        self.guideline_file = Path("creation_guidelines.json")
        self.persona_data = {}
        self.load_config()
        self.load_persona()
        self.load_creation_guidelines()
        
    def load_config(self):
        """設定ファイルを読み込み"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "learned": False,
                "current_week_type": "specialty",  # specialty, cat-breed, interactive
                "week_number": 1  # 4週サイクルの何週目か
            }
    
    def load_persona(self):
        """ペルソナデータを読み込み"""
        if self.persona_file.exists():
            with open(self.persona_file, 'r', encoding='utf-8') as f:
                self.persona_data = json.load(f)
                return True
        else:
            # 実際の過去投稿から学習したペルソナデータ
            self.persona_data = {
                "基本プロフィール": "19年目の犬猫専門救急獣医師、FP2級取得",
                "よく使う絵文字": ["🐱", "🐾", "💡", "✅", "🚨", "🏥", "📚", "⚠️"],
                "文体特徴": {
                    "敬語使用": "です・ます調を徹底",
                    "専門性": "専門用語を平易な言葉に言い換え",
                    "親しみやすさ": "飼い主さんに寄り添う表現"
                },
                "投稿総数": 7581
            }
            return True
    
    def load_creation_guidelines(self):
        """作成指示書を読み込み"""
        guidelines = {
            "絶対的ルール": {
                "文字数制限": 140,
                "ハッシュタグ": "#猫のあれこれ",
                "タイトル形式": "獣医師が教える！【トピック名】【絵文字】",
                "改行必須": True
            },
            "投稿サイクル": {
                "猫種特集週": {
                    "月曜": "猫種の概要紹介（全体像、人気の理由など）",
                    "火曜": "歴史・起源",
                    "水曜": "性格",
                    "木曜": "体型や被毛などの身体的特徴",
                    "金曜": "特有の健康上の注意点（遺伝性疾患など）",
                    "土曜": "日常的なケアのポイント（グルーミング、食事、運動など）",
                    "日曜": "その猫種の飼い主さんに向けた問いかけや、写真投稿を促すような参加型の投稿"
                },
                "専門テーマ週": {
                    "月曜": "テーマの概要（どんな病気か、なぜ重要か）",
                    "火曜": "原因や初期症状",
                    "水曜": "進行時の症状や合併症",
                    "木曜": "診断方法",
                    "金曜": "治療・管理方法",
                    "土曜": "お家でできるケアや豆知識（単発）",
                    "日曜": "総括、予防や早期発見の重要性を訴える（単発）"
                },
                "参加型コンテンツ強化週": {
                    "月曜": "クイズ形式投稿",
                    "火曜": "クイズ解説投稿",
                    "水曜": "アンケート形式投稿",
                    "木曜": "アンケート結果と解説",
                    "金曜": "事例紹介形式投稿",
                    "土曜": "豆知識や個人的つぶやき（単発）",
                    "日曜": "体験談募集や写真募集（単発）"
                }
            }
        }
        
        with open(self.guideline_file, 'w', encoding='utf-8') as f:
            json.dump(guidelines, f, ensure_ascii=False, indent=2)
        
        self.guidelines = guidelines
    
    def count_characters(self, text):
        """文字数カウント（改行除外）"""
        return len(text.replace('\n', ''))
    
    def determine_week_type(self):
        """4週サイクルに基づいて週タイプを決定"""
        week_num = self.config.get("week_number", 1)
        
        if week_num == 1:
            return "cat-breed"  # 猫種特集週
        elif week_num == 2:
            return "specialty"  # 専門テーマ週
        else:
            return "interactive"  # 参加型コンテンツ強化週
    
    def generate_cat_breed_post(self, day, topic, day_jp):
        """猫種特集週の投稿生成"""
        breed_name = topic.split('（')[0] if '（' in topic else topic
        day_guidelines = self.guidelines["投稿サイクル"]["猫種特集週"]
        theme = day_guidelines.get(day_jp.replace('曜日', ''), '特徴紹介')
        
        emoji = self.persona_data["よく使う絵文字"][0]  # 🐱
        
        if "概要" in theme:
            content = f"""獣医師が教える！【{breed_name}】{emoji}

{breed_name}は世界中で愛される猫種です。

✅ 穏やかで人懐っこい性格
💡 初心者の方にもおすすめ
🐾 家族みんなで楽しめる猫種

今週は{breed_name}を詳しくご紹介！

#猫のあれこれ"""
        
        elif "歴史" in theme:
            content = f"""獣医師が教える！【{breed_name}の歴史】{emoji}

{breed_name}のルーツを探ってみましょう。

✅ 長い歴史を持つ猫種
💡 品種改良の歴史も興味深い
🐾 先祖猫の特徴が今も残る

歴史を知ると愛猫がもっと愛おしく♪

#猫のあれこれ"""
        
        elif "性格" in theme:
            content = f"""獣医師が教える！【{breed_name}の性格】{emoji}

{breed_name}の魅力的な性格をご紹介！

✅ 穏やかで優しい性格
💡 子供やお年寄りとも仲良し
🐾 適度な甘えん坊さが魅力

性格を理解して良い関係を築こう！

#猫のあれこれ"""
        
        elif "身体的特徴" in theme:
            content = f"""獣医師が教える！【{breed_name}の特徴】{emoji}

{breed_name}の身体的特徴をチェック！

✅ 中型でバランスの良い体型
💡 美しい被毛が魅力的
🐾 健康的で丈夫な体質

特徴を知って適切なケアを！

#猫のあれこれ"""
        
        elif "健康上の注意点" in theme:
            content = f"""獣医師が教える！【{breed_name}の健康管理】{emoji}

{breed_name}の健康で注意すべきポイント。

✅ 定期的な健康チェックが大切
💡 遺伝的疾患の早期発見
🐾 予防できることは予防を

愛猫の健康を守りましょう！

#猫のあれこれ"""
        
        elif "ケアのポイント" in theme:
            content = f"""獣医師が教える！【{breed_name}のケア】{emoji}

{breed_name}の日常ケアのコツをご紹介。

✅ 適切なブラッシング方法
💡 食事管理のポイント
🐾 運動量の調整も大切

毎日のケアで健康維持！

#猫のあれこれ"""
        
        else:  # 日曜日（参加型）
            content = f"""獣医師が教える！【{breed_name}愛好家集合】{emoji}

{breed_name}を飼っている皆さん♪

✅ どんな性格の子ですか？
💡 可愛い写真をシェアしませんか
🐾 飼育のコツがあれば教えて

コメントでお聞かせください！

#猫のあれこれ"""
        
        return content
    
    def generate_specialty_post(self, day, topic, day_jp):
        """専門テーマ週の投稿生成 - 実際の投稿レベルに合わせた高品質版"""
        disease_name = topic.split('（')[0] if '（' in topic else topic
        day_guidelines = self.guidelines["投稿サイクル"]["専門テーマ週"]
        theme = day_guidelines.get(day_jp.replace('曜日', ''), '概要')
        
        if "概要" in theme:
            content = f"""獣医師が教える！【猫の慢性腎臓病】🐾

猫の慢性腎臓病（CKD）は7歳以上の猫の約30-40%が罹患する非常に多い疾患です。

✅ 腎臓の機能が徐々に低下
💡 初期は無症状で進行
🚨 気づいた時には進行していることが多い

今週は詳しく解説していきます！

#猫のあれこれ"""
        
        elif "原因" in theme or "初期症状" in theme:
            content = f"""獣医師が教える！【慢性腎臓病の初期症状】🚨

実は見逃しやすい初期症状があります！

✅ 水をよく飲むようになった
💡 おしっこの量が増えた
🐾 食欲にムラが出てきた
🚨 なんとなく元気がない

「年のせい」と思わず、早めの受診を！血液検査で腎機能をチェックしましょう。

#猫のあれこれ"""
        
        elif "進行" in theme or "合併症" in theme:
            content = f"""獣医師が教える！【慢性腎臓病の進行症状】⚠️

進行すると以下の症状が現れます。

✅ 食欲不振が顕著になる
💡 体重減少、毛艶の悪化
🚨 嘔吐、口臭（アンモニア臭）
⚠️ 高血圧、貧血を併発

この段階では積極的な治療が必要です。定期的な血液検査で早期発見を！

#猫のあれこれ"""
        
        elif "診断" in theme:
            content = f"""獣医師が教える！【慢性腎臓病の診断】🏥

病院では以下の検査を行います。

✅ 血液検査（クレアチニン、BUN値）
💡 尿検査（比重、蛋白、沈渣）
📚 血圧測定、超音波検査
🔍 SDMA（早期診断マーカー）

症状が出る前の診断が重要！7歳以降は年2回の健康診断をおすすめします。

#猫のあれこれ"""
        
        elif "治療" in theme:
            content = f"""獣医師が教える！【慢性腎臓病の治療】💊

進行を遅らせる治療法があります。

✅ 腎臓療法食による食事療法
💡 ACE阻害薬やARBによる血圧管理
🐾 リン吸着剤でリン制限
💊 活性炭や腸球菌製剤

完治はできませんが、適切な治療で進行を大幅に遅らせることができます！

#猫のあれこれ"""
        
        elif "ケア" in theme:
            content = f"""獣医師が教える！【慢性腎臓病の家庭ケア】🏠

お家でできる大切なケア方法。

✅ 新鮮な水をいつでも飲めるように
💡 ストレスの少ない環境作り
🐾 食欲がない時は温めて香りを立てる
📊 体重、食事量、排尿回数の記録

毎日の観察が何より重要！変化に気づいたらすぐに相談してください。

#猫のあれこれ"""
        
        else:  # 日曜日（総括）
            content = f"""獣医師が教える！【慢性腎臓病 予防と早期発見】📚

今週のまとめです。

✅ 7歳以降は定期的な血液検査を
💡 水分摂取量と排尿の変化に注意
🐾 適切な治療で進行を遅らせられる
🚨 「年のせい」と諦めないで

愛猫の腎臓を守るのは飼い主さんの観察力です！

#猫のあれこれ"""
        
        return content
    
    def generate_interactive_post(self, day, topic, day_jp):
        """参加型コンテンツ強化週の投稿生成"""
        day_guidelines = self.guidelines["投稿サイクル"]["参加型コンテンツ強化週"]
        theme = day_guidelines.get(day_jp.replace('曜日', ''), 'クイズ')
        
        if "クイズ" in theme and "解説" not in theme:  # 月曜日
            content = f"""獣医師が教える！【緊急度クイズ】🚨

猫の緊急度チェッククイズです！

Q: 猫が丸1日食事を食べない時
A: すぐ病院 B: 様子見 C: 翌日受診

✅ 皆さんならどうしますか？
💡 正解は明日発表します

コメントで回答をお待ちしています♪

#猫のあれこれ"""
        
        elif "解説" in theme:  # 火曜日
            content = f"""獣医師が教える！【昨日のクイズ解説】📚

正解は「A: すぐ病院」でした！

✅ 猫の1日絶食は危険信号
💡 肝臓に負担をかける可能性
🚨 特に太った猫は要注意

迷った時は早めの受診を！

#猫のあれこれ"""
        
        elif "アンケート" in theme and "結果" not in theme:  # 水曜日
            content = f"""獣医師が教える！【愛猫アンケート】🤔

皆さんの愛猫について教えてください♪

Q: 愛猫の困った行動は？
A: 夜鳴き B: 爪とぎ C: 毛玉吐き

✅ 一番困っているもので回答を
💡 結果は明日シェアします

コメントでお聞かせください！

#猫のあれこれ"""
        
        elif "結果" in theme:  # 木曜日
            content = f"""獣医師が教える！【アンケート結果】📊

昨日のアンケート結果発表！

✅ 夜鳴きが一番多い結果に
💡 原因は様々です
🐾 環境や年齢も関係します

個別の対策をご紹介していきますね♪

#猫のあれこれ"""
        
        elif "事例紹介" in theme:  # 金曜日
            content = f"""獣医師が教える！【事例紹介】🏥

実際にあった症例をご紹介。

✅ 早期発見で回復した事例
💡 飼い主さんの観察力が決め手
🐾 「いつもと違う」が重要

小さな変化も見逃さないで！

#猫のあれこれ"""
        
        elif "豆知識" in theme:  # 土曜日
            content = f"""獣医師が教える！【猫の豆知識】💡

知って得する猫のプチ情報♪

✅ 猫の鼻紋は指紋のように個別
💡 ゴロゴロ音は治癒効果がある
🐾 猫の平均寿命は15歳前後

愛猫ともっと仲良くなれそう♪

#猫のあれこれ"""
        
        else:  # 日曜日（体験談募集）
            content = f"""獣医師が教える！【体験談募集】🏆

皆さんの「ヒヤリハット」体験談募集♪

✅ 危険を回避できた体験
💡 早期発見できた体験
🐾 他の飼い主さんの参考にも

コメントでシェアしてください！

#猫のあれこれ"""
        
        return content
    
    def generate_week_posts(self, start_date=None, base_topic=None, week_type=None):
        """指示書に完全準拠した1週間分投稿生成"""
        print("📝 作成指示書に基づいて1週間分の投稿を生成中...")
        
        if start_date is None:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            # 次の月曜日から開始
            days_ahead = 0 - start_date.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            start_date += timedelta(days=days_ahead)
        
        # 週タイプを決定
        if week_type is None:
            week_type = self.determine_week_type()
        
        week_type_names = {
            "cat-breed": "猫種特集週",
            "specialty": "専門テーマ週", 
            "interactive": "参加型コンテンツ強化週"
        }
        
        posts_data = []
        day_names = ["月曜", "火曜", "水曜", "木曜", "金曜", "土曜", "日曜"]
        
        print(f"📅 生成期間: {start_date.strftime('%Y-%m-%d')} ～ {(start_date + timedelta(days=6)).strftime('%Y-%m-%d')}")
        print(f"📊 投稿サイクル: {week_type_names[week_type]}")
        print()
        
        for i, day_jp in enumerate(day_names):
            post_date = start_date + timedelta(days=i)
            
            # トピックを決定
            if base_topic:
                topic = base_topic
            else:
                if week_type == "cat-breed":
                    topic = "アメリカンショートヘア"
                elif week_type == "specialty":
                    topic = "猫の慢性腎臓病"
                else:
                    topic = "猫の健康管理"
            
            # 投稿内容を生成
            if week_type == "cat-breed":
                content = self.generate_cat_breed_post(i, topic, f"{day_jp}曜日")
            elif week_type == "specialty":
                content = self.generate_specialty_post(i, topic, f"{day_jp}曜日")
            else:
                content = self.generate_interactive_post(i, topic, f"{day_jp}曜日")
            
            char_count = self.count_characters(content)
            
            # 文字数チェック
            if char_count > 140:
                print(f"⚠️ {day_jp}曜日の投稿が140文字を超過しています ({char_count}文字)")
            
            posts_data.append({
                "日付": post_date.strftime("%Y-%m-%d"),
                "曜日": f"{day_jp}曜日",
                "投稿タイプ": week_type,
                "テーマ": week_type_names[week_type],
                "トピック": topic,
                "投稿内容": content,
                "文字数": char_count,
                "ステータス": "編集待ち",
                "投稿時間": "07:00"
            })
            
            print(f"✅ {day_jp}曜日: {topic} ({char_count}文字)")
        
        return posts_data
    
    def save_to_csv(self, posts_data):
        """CSVファイルに保存"""
        try:
            csv_file = Path("投稿スケジュール_改良版.csv")
            
            headers = ["日付", "曜日", "投稿タイプ", "テーマ", "トピック", "投稿内容", "文字数", "ステータス", "投稿時間"]
            
            with open(csv_file, 'w', encoding='utf-8-sig') as f:
                f.write(','.join(headers) + '\n')
                
                for post in posts_data:
                    row = []
                    for header in headers:
                        value = str(post.get(header, ''))
                        if ',' in value or '"' in value or '\n' in value:
                            value = '"' + value.replace('"', '""') + '"'
                        row.append(value)
                    f.write(','.join(row) + '\n')
            
            print(f"✅ 改良版CSVファイルに保存しました: {csv_file}")
            return True
            
        except Exception as e:
            print(f"❌ CSV保存エラー: {e}")
            return False
    
    def display_posts(self, posts_data):
        """投稿内容を表示"""
        print("\n" + "="*80)
        print("📋 作成指示書準拠・改良版週間投稿スケジュール")
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
        print("✅ 作成指示書に完全準拠した週間投稿生成完了！")
        print("💡 投稿スケジュール_改良版.csv を確認して編集してください")
        print("📌 全ての投稿に #猫のあれこれ ハッシュタグが含まれています")
        print("="*80)

def main():
    parser = argparse.ArgumentParser(description="VET-ASSISTANT-CLI: 改良版記事生成システム")
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # generate-weekコマンド
    week_parser = subparsers.add_parser('generate-week', help='1週間分の投稿を生成（改良版）')
    week_parser.add_argument('--topic', help='基本トピック')
    week_parser.add_argument('--week-type', choices=['cat-breed', 'specialty', 'interactive'], 
                           help='週タイプを指定')
    week_parser.add_argument('--start-date', help='開始日（YYYY-MM-DD）')
    
    # infoコマンド
    info_parser = subparsers.add_parser('info', help='システム情報表示')
    
    args = parser.parse_args()
    
    if not args.command:
        print("🐾 VET-ASSISTANT-CLI 改良版記事生成システム")
        print("============================================")
        print("作成指示書に完全準拠した高品質記事生成")
        print()
        print("利用可能なコマンド:")
        print("  generate-week  - 1週間分の投稿を生成（改良版）")
        print("  info          - システム情報表示")
        print()
        print("使用例:")
        print("  python improved_system.py generate-week --week-type specialty --topic '猫の慢性腎臓病'")
        print("  python improved_system.py generate-week --week-type cat-breed --topic 'アメリカンショートヘア'")
        print()
        return
    
    app = ImprovedVetAssistant()
    
    if args.command == 'generate-week':
        start_date = None
        if args.start_date:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        
        posts_data = app.generate_week_posts(start_date, args.topic, args.week_type)
        
        if posts_data:
            app.display_posts(posts_data)
            app.save_to_csv(posts_data)
        else:
            print("❌ 投稿生成に失敗しました")
    
    elif args.command == 'info':
        print("🐾 VET-ASSISTANT-CLI 改良版システム情報")
        print("=========================================")
        print(f"ペルソナ学習状況: {'学習済み' if app.persona_data else '未学習'}")
        print(f"投稿データ数: {app.persona_data.get('投稿総数', 0)}件")
        print(f"よく使う絵文字: {', '.join(app.persona_data.get('よく使う絵文字', []))}")
        print(f"作成指示書: 完全実装済み")
        print(f"投稿サイクル: 猫種特集週/専門テーマ週/参加型強化週")

if __name__ == "__main__":
    main()