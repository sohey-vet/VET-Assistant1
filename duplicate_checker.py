#!/usr/bin/env python3
"""
重複チェック機能モジュール
投稿内容の重複や類似性を厳重にチェックする
"""

import json
import hashlib
import sqlite3
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import difflib
from collections import Counter

class DuplicateChecker:
    def __init__(self, db_path: str = "post_history.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """投稿履歴データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                normalized_content TEXT NOT NULL,
                topic TEXT,
                post_type TEXT,
                day TEXT,
                char_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                keywords TEXT,
                main_points TEXT
            )
        ''')
        
        # インデックスを作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON post_history(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_topic ON post_history(topic)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_type ON post_history(post_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON post_history(created_at)')
        
        conn.commit()
        conn.close()
    
    def normalize_content(self, content: str) -> str:
        """投稿内容を正規化（比較用）"""
        # 改行、空白、絵文字、ハッシュタグを除去
        normalized = re.sub(r'[\n\r\s]', '', content)
        normalized = re.sub(r'[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '', normalized)
        normalized = re.sub(r'#\w+', '', normalized)
        return normalized.lower()
    
    def extract_keywords(self, content: str) -> List[str]:
        """投稿内容からキーワードを抽出"""
        # 専門用語、病名、猫種名などを抽出
        keywords = []
        
        # 病名・症状パターン
        disease_patterns = [
            r'(腎臓病|心臓病|糖尿病|甲状腺|肝臓|膀胱|尿路|結石|感染症|アレルギー)',
            r'(白内障|緑内障|結膜炎|皮膚炎|外耳炎|歯周病|口内炎)',
            r'(嘔吐|下痢|便秘|発熱|食欲不振|体重減少|呼吸困難)'
        ]
        
        # 猫種パターン
        breed_patterns = [
            r'(アメリカンショートヘア|ペルシャ|ロシアンブルー|スコティッシュフォールド)',
            r'(メインクーン|ラグドール|ベンガル|アビシニアン|マンチカン|ブリティッシュ)'
        ]
        
        # 医療用語パターン
        medical_patterns = [
            r'(診断|治療|手術|薬|ワクチン|検査|血液検査|レントゲン|エコー)',
            r'(症状|予防|ケア|管理|観察|対処法|応急処置)'
        ]
        
        all_patterns = disease_patterns + breed_patterns + medical_patterns
        
        for pattern in all_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            keywords.extend(matches)
        
        return list(set(keywords))
    
    def extract_main_points(self, content: str) -> List[str]:
        """投稿内容から主要ポイントを抽出"""
        points = []
        
        # 箇条書きポイントを抽出
        bullet_patterns = [
            r'✅\s*([^\n]+)',
            r'💡\s*([^\n]+)', 
            r'🐾\s*([^\n]+)',
            r'⚠️\s*([^\n]+)',
            r'❗\s*([^\n]+)'
        ]
        
        for pattern in bullet_patterns:
            matches = re.findall(pattern, content)
            points.extend(matches)
        
        # 重要な文を抽出
        important_sentences = re.findall(r'[。！？][^\n]*?[重要|大切|注意|必要|推奨][^\n]*?[。！？]', content)
        points.extend(important_sentences)
        
        return [point.strip() for point in points if point.strip()]
    
    def calculate_content_hash(self, content: str) -> str:
        """投稿内容のハッシュ値を計算"""
        normalized = self.normalize_content(content)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def calculate_similarity(self, content1: str, content2: str) -> float:
        """2つの投稿内容の類似度を計算（0.0-1.0）"""
        norm1 = self.normalize_content(content1)
        norm2 = self.normalize_content(content2)
        
        # 完全一致の場合
        if norm1 == norm2:
            return 1.0
        
        # 文字列の類似度
        text_similarity = difflib.SequenceMatcher(None, norm1, norm2).ratio()
        
        # キーワードの類似度
        keywords1 = set(self.extract_keywords(content1))
        keywords2 = set(self.extract_keywords(content2))
        
        if keywords1 or keywords2:
            keyword_similarity = len(keywords1 & keywords2) / len(keywords1 | keywords2)
        else:
            keyword_similarity = 0.0
        
        # 主要ポイントの類似度
        points1 = set(self.extract_main_points(content1))
        points2 = set(self.extract_main_points(content2))
        
        if points1 or points2:
            points_similarity = len(points1 & points2) / len(points1 | points2)
        else:
            points_similarity = 0.0
        
        # 重み付き平均
        final_similarity = (
            text_similarity * 0.4 +
            keyword_similarity * 0.4 +
            points_similarity * 0.2
        )
        
        return final_similarity
    
    def save_post(self, content: str, topic: str = "", post_type: str = "", day: str = "") -> bool:
        """投稿を履歴に保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            content_hash = self.calculate_content_hash(content)
            normalized_content = self.normalize_content(content)
            keywords = json.dumps(self.extract_keywords(content), ensure_ascii=False)
            main_points = json.dumps(self.extract_main_points(content), ensure_ascii=False)
            char_count = len(content.replace('\n', ''))
            
            cursor.execute('''
                INSERT INTO post_history 
                (content, content_hash, normalized_content, topic, post_type, day, 
                 char_count, keywords, main_points)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (content, content_hash, normalized_content, topic, post_type, day,
                  char_count, keywords, main_points))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ 投稿保存エラー: {e}")
            return False
    
    def check_duplicate(self, content: str, topic: str = "", post_type: str = "", 
                       similarity_threshold: float = 0.7) -> Tuple[bool, List[Dict]]:
        """重複チェックを実行"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 完全一致チェック
            content_hash = self.calculate_content_hash(content)
            cursor.execute('SELECT * FROM post_history WHERE content_hash = ?', (content_hash,))
            exact_match = cursor.fetchone()
            
            if exact_match:
                return True, [{
                    'type': 'exact_match',
                    'similarity': 1.0,
                    'content': exact_match[1],
                    'topic': exact_match[3],
                    'created_at': exact_match[8]
                }]
            
            # 類似度チェック
            duplicates = []
            
            # 同じトピックの投稿を優先的にチェック
            if topic:
                cursor.execute('''
                    SELECT * FROM post_history 
                    WHERE topic = ? 
                    ORDER BY created_at DESC 
                    LIMIT 20
                ''', (topic,))
                similar_topic_posts = cursor.fetchall()
                
                for post in similar_topic_posts:
                    similarity = self.calculate_similarity(content, post[1])
                    if similarity >= similarity_threshold:
                        duplicates.append({
                            'type': 'similar_topic',
                            'similarity': similarity,
                            'content': post[1],
                            'topic': post[3],
                            'created_at': post[8]
                        })
            
            # 同じ投稿タイプの投稿をチェック
            if post_type:
                cursor.execute('''
                    SELECT * FROM post_history 
                    WHERE post_type = ? 
                    ORDER BY created_at DESC 
                    LIMIT 30
                ''', (post_type,))
                similar_type_posts = cursor.fetchall()
                
                for post in similar_type_posts:
                    similarity = self.calculate_similarity(content, post[1])
                    if similarity >= similarity_threshold:
                        # 既に追加されていないかチェック
                        if not any(d['content'] == post[1] for d in duplicates):
                            duplicates.append({
                                'type': 'similar_type',
                                'similarity': similarity,
                                'content': post[1],
                                'topic': post[3],
                                'created_at': post[8]
                            })
            
            # 最近の投稿全般をチェック
            cursor.execute('''
                SELECT * FROM post_history 
                ORDER BY created_at DESC 
                LIMIT 50
            ''')
            recent_posts = cursor.fetchall()
            
            for post in recent_posts:
                similarity = self.calculate_similarity(content, post[1])
                if similarity >= similarity_threshold:
                    # 既に追加されていないかチェック
                    if not any(d['content'] == post[1] for d in duplicates):
                        duplicates.append({
                            'type': 'recent_similar',
                            'similarity': similarity,
                            'content': post[1],
                            'topic': post[3],
                            'created_at': post[8]
                        })
            
            conn.close()
            
            # 類似度でソート
            duplicates.sort(key=lambda x: x['similarity'], reverse=True)
            
            return len(duplicates) > 0, duplicates
            
        except Exception as e:
            print(f"❌ 重複チェックエラー: {e}")
            return False, []
    
    def get_post_history(self, limit: int = 50) -> List[Dict]:
        """投稿履歴を取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM post_history 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            posts = cursor.fetchall()
            conn.close()
            
            return [{
                'id': post[0],
                'content': post[1],
                'topic': post[3],
                'post_type': post[4],
                'day': post[5],
                'char_count': post[6],
                'created_at': post[8],
                'keywords': json.loads(post[9]) if post[9] else [],
                'main_points': json.loads(post[10]) if post[10] else []
            } for post in posts]
            
        except Exception as e:
            print(f"❌ 履歴取得エラー: {e}")
            return []
    
    def clean_old_posts(self, days_to_keep: int = 90):
        """古い投稿を削除"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM post_history 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days_to_keep))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"✅ {deleted_count}件の古い投稿を削除しました")
            return True
            
        except Exception as e:
            print(f"❌ 古い投稿削除エラー: {e}")
            return False