import sqlite3
import json
import os
from typing import List, Dict, Optional
from .base_storage import StorageBase


class DatabaseStorage(StorageBase):
    """
    数据库存储服务
    将插画信息存储到SQLite数据库中
    """

    def __init__(self, db_path: str = "data/illustrations.db"):
        """
        初始化数据库存储服务
        
        参数:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._init_database()

    def _init_database(self):
        """
        初始化数据库表结构
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 创建插画表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS illustrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    content TEXT,
                    images TEXT,
                    tags TEXT,
                    source TEXT,
                    category TEXT,
                    thumbnail TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_id ON illustrations(article_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON illustrations(title)')
            conn.commit()

    def _serialize_list(self, data: list) -> str:
        """
        序列化列表为JSON字符串
        """
        return json.dumps(data, ensure_ascii=False)

    def _deserialize_list(self, data: str) -> list:
        """
        反序列化JSON字符串为列表
        """
        if not data:
            return []
        try:
            return json.loads(data)
        except:
            return []

    def save_illustration(self, illustration: Dict) -> bool:
        """
        保存单个插画信息
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                article_id = illustration.get('article_id')
                if not article_id:
                    return False
                
                # 检查是否已存在
                cursor.execute('SELECT id FROM illustrations WHERE article_id = ?', (article_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有记录
                    cursor.execute('''
                        UPDATE illustrations SET 
                            title = ?, 
                            url = ?, 
                            content = ?, 
                            images = ?, 
                            tags = ?, 
                            source = ?, 
                            category = ?, 
                            thumbnail = ?, 
                            updated_at = CURRENT_TIMESTAMP
                        WHERE article_id = ?
                    ''', (
                        illustration.get('title', ''),
                        illustration.get('url', ''),
                        illustration.get('content', ''),
                        self._serialize_list(illustration.get('images', [])),
                        self._serialize_list(illustration.get('tags', [])),
                        illustration.get('source', ''),
                        illustration.get('category', ''),
                        illustration.get('thumbnail', ''),
                        article_id
                    ))
                else:
                    # 添加新记录
                    cursor.execute('''
                        INSERT INTO illustrations (
                            article_id, title, url, content, images, tags, source, category, thumbnail
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article_id,
                        illustration.get('title', ''),
                        illustration.get('url', ''),
                        illustration.get('content', ''),
                        self._serialize_list(illustration.get('images', [])),
                        self._serialize_list(illustration.get('tags', [])),
                        illustration.get('source', ''),
                        illustration.get('category', ''),
                        illustration.get('thumbnail', '')
                    ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"保存插画失败: {e}")
            return False

    def save_illustrations(self, illustrations: List[Dict]) -> bool:
        """
        批量保存插画信息
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for illustration in illustrations:
                    article_id = illustration.get('article_id')
                    if not article_id:
                        continue
                    
                    # 检查是否已存在
                    cursor.execute('SELECT id FROM illustrations WHERE article_id = ?', (article_id,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # 更新现有记录
                        cursor.execute('''
                            UPDATE illustrations SET 
                                title = ?, 
                                url = ?, 
                                content = ?, 
                                images = ?, 
                                tags = ?, 
                                source = ?, 
                                category = ?, 
                                thumbnail = ?, 
                                updated_at = CURRENT_TIMESTAMP
                            WHERE article_id = ?
                        ''', (
                            illustration.get('title', ''),
                            illustration.get('url', ''),
                            illustration.get('content', ''),
                            self._serialize_list(illustration.get('images', [])),
                            self._serialize_list(illustration.get('tags', [])),
                            illustration.get('source', ''),
                            illustration.get('category', ''),
                            illustration.get('thumbnail', ''),
                            article_id
                        ))
                    else:
                        # 添加新记录
                        cursor.execute('''
                            INSERT INTO illustrations (
                                article_id, title, url, content, images, tags, source, category, thumbnail
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            article_id,
                            illustration.get('title', ''),
                            illustration.get('url', ''),
                            illustration.get('content', ''),
                            self._serialize_list(illustration.get('images', [])),
                            self._serialize_list(illustration.get('tags', [])),
                            illustration.get('source', ''),
                            illustration.get('category', ''),
                            illustration.get('thumbnail', '')
                        ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"批量保存插画失败: {e}")
            return False

    def get_illustration(self, article_id: str) -> Optional[Dict]:
        """
        根据文章ID获取插画信息
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT article_id, title, url, content, images, tags, source, category, thumbnail 
                    FROM illustrations 
                    WHERE article_id = ?
                ''', (article_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'article_id': row[0],
                        'title': row[1],
                        'url': row[2],
                        'content': row[3],
                        'images': self._deserialize_list(row[4]),
                        'tags': self._deserialize_list(row[5]),
                        'source': row[6],
                        'category': row[7],
                        'thumbnail': row[8]
                    }
                return None
        except Exception as e:
            print(f"获取插画失败: {e}")
            return None

    def get_illustrations(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        获取插画列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT article_id, title, url, content, images, tags, source, category, thumbnail 
                    FROM illustrations 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                ''', (limit, offset))
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    result.append({
                        'article_id': row[0],
                        'title': row[1],
                        'url': row[2],
                        'content': row[3],
                        'images': self._deserialize_list(row[4]),
                        'tags': self._deserialize_list(row[5]),
                        'source': row[6],
                        'category': row[7],
                        'thumbnail': row[8]
                    })
                return result
        except Exception as e:
            print(f"获取插画列表失败: {e}")
            return []

    def update_illustration(self, article_id: str, illustration: Dict) -> bool:
        """
        更新插画信息
        """
        # 确保article_id一致
        illustration['article_id'] = article_id
        return self.save_illustration(illustration)

    def delete_illustration(self, article_id: str) -> bool:
        """
        删除插画信息
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM illustrations WHERE article_id = ?', (article_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"删除插画失败: {e}")
            return False

    def search_illustrations(self, keyword: str, limit: int = 100) -> List[Dict]:
        """
        搜索插画
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 使用LIKE进行模糊搜索
                cursor.execute('''
                    SELECT article_id, title, url, content, images, tags, source, category, thumbnail 
                    FROM illustrations 
                    WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', limit))
                rows = cursor.fetchall()
                
                result = []
                for row in rows:
                    result.append({
                        'article_id': row[0],
                        'title': row[1],
                        'url': row[2],
                        'content': row[3],
                        'images': self._deserialize_list(row[4]),
                        'tags': self._deserialize_list(row[5]),
                        'source': row[6],
                        'category': row[7],
                        'thumbnail': row[8]
                    })
                return result
        except Exception as e:
            print(f"搜索插画失败: {e}")
            return []