import sqlite3
import os
import json
from datetime import datetime


class DBManager:
    def __init__(self, db_path="data.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """
        初始化数据库，创建消息表
        """
        # 确保数据库目录存在
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # 连接数据库并创建表
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建消息表
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            media_id TEXT,
            msg_id TEXT,
            send_time TEXT,
            status INTEGER DEFAULT 0,
            total_count INTEGER DEFAULT 0,
            filter_count INTEGER DEFAULT 0,
            sent_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            msg_status_detail TEXT,
            create_time TEXT NOT NULL
        )
        """
        )

        conn.commit()
        conn.close()

    def insert_message(
        self,
        task_id,
        title,
        content=None,
        media_id=None,
        msg_id=None,
        send_time=None,
        status=0,
    ):
        """
        插入消息记录
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        create_time = datetime.now().isoformat()
        send_time_str = send_time.isoformat() if send_time else None

        cursor.execute(
            """
        INSERT INTO messages (task_id, title, content, media_id, msg_id, send_time, status, create_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                task_id,
                title,
                content,
                media_id,
                msg_id,
                send_time_str,
                status,
                create_time,
            ),
        )

        message_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return message_id

    def update_message_status(
        self,
        message_id,
        status,
        send_time=None,
        total_count=None,
        filter_count=None,
        sent_count=None,
        error_count=None,
        msg_status_detail=None,
    ):
        """
        更新消息状态
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 构建更新字段和值
        update_fields = []
        update_values = []

        update_fields.append("status = ?")
        update_values.append(status)

        if send_time:
            update_fields.append("send_time = ?")
            update_values.append(send_time.isoformat())

        if total_count is not None:
            update_fields.append("total_count = ?")
            update_values.append(total_count)

        if filter_count is not None:
            update_fields.append("filter_count = ?")
            update_values.append(filter_count)

        if sent_count is not None:
            update_fields.append("sent_count = ?")
            update_values.append(sent_count)

        if error_count is not None:
            update_fields.append("error_count = ?")
            update_values.append(error_count)

        if msg_status_detail:
            update_fields.append("msg_status_detail = ?")
            update_values.append(msg_status_detail)

        # 添加WHERE条件
        update_values.append(message_id)

        # 构建SQL语句
        sql = f"UPDATE messages SET {', '.join(update_fields)} WHERE id = ?"

        cursor.execute(sql, tuple(update_values))

        conn.commit()
        conn.close()

    def update_message_msg_id(self, message_id, msg_id):
        """
        更新消息的msg_id
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        UPDATE messages SET msg_id = ? WHERE id = ?
        """,
            (msg_id, message_id),
        )

        conn.commit()
        conn.close()

    def get_message(self, message_id):
        """
        获取消息记录
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT * FROM messages WHERE id = ?
        """,
            (message_id,),
        )

        message = cursor.fetchone()
        conn.close()

        if message:
            return {
                "id": message[0],
                "task_id": message[1],
                "title": message[2],
                "content": message[3],
                "media_id": message[4],
                "msg_id": message[5],
                "send_time": message[6],
                "status": message[7],
                "total_count": message[8],
                "filter_count": message[9],
                "sent_count": message[10],
                "error_count": message[11],
                "msg_status_detail": message[12],
                "create_time": message[13],
            }
        return None

    def get_messages_by_status(self, status):
        """
        根据状态获取消息记录
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT * FROM messages WHERE status = ? ORDER BY create_time DESC
        """,
            (status,),
        )

        messages = []
        for message in cursor.fetchall():
            messages.append(
                {
                    "id": message[0],
                    "task_id": message[1],
                    "title": message[2],
                    "content": message[3],
                    "media_id": message[4],
                    "msg_id": message[5],
                    "send_time": message[6],
                    "status": message[7],
                    "total_count": message[8],
                    "filter_count": message[9],
                    "sent_count": message[10],
                    "error_count": message[11],
                    "msg_status_detail": message[12],
                    "create_time": message[13],
                }
            )

        conn.close()
        return messages

    def get_message_by_msg_id(self, msg_id):
        """
        根据msg_id查询消息记录
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT * FROM messages WHERE msg_id = ?
        """,
            (msg_id,),
        )

        message = cursor.fetchone()
        conn.close()

        if message:
            return {
                "id": message[0],
                "task_id": message[1],
                "title": message[2],
                "content": message[3],
                "media_id": message[4],
                "msg_id": message[5],
                "send_time": message[6],
                "status": message[7],
                "total_count": message[8],
                "filter_count": message[9],
                "sent_count": message[10],
                "error_count": message[11],
                "msg_status_detail": message[12],
                "create_time": message[13],
            }
        return None

    def get_all_messages(self):
        """
        获取所有消息记录
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
        SELECT * FROM messages ORDER BY create_time DESC
        """
        )

        messages = []
        for message in cursor.fetchall():
            messages.append(
                {
                    "id": message[0],
                    "task_id": message[1],
                    "title": message[2],
                    "content": message[3],
                    "media_id": message[4],
                    "msg_id": message[5],
                    "send_time": message[6],
                    "status": message[7],
                    "total_count": message[8],
                    "filter_count": message[9],
                    "sent_count": message[10],
                    "error_count": message[11],
                    "msg_status_detail": message[12],
                    "create_time": message[13],
                }
            )

        conn.close()
        return messages
