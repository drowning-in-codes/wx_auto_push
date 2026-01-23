from flask import Flask, request, abort
import hashlib
import xml.etree.ElementTree as ET
import json
from datetime import datetime

class WeChatCallbackServer:
    def __init__(self, config, db_manager, push_service):
        self.app = Flask(__name__)
        self.config = config
        self.db_manager = db_manager
        self.push_service = push_service
        
        # 获取微信配置
        wechat_config = self.config.get_wechat_config()
        self.token = wechat_config.get("token", "wechat_auto_push")
        
        # 注册路由
        self._register_routes()
    
    def _register_routes(self):
        """注册路由"""
        @self.app.route('/wechat/callback', methods=['GET', 'POST'])
        def wechat_callback():
            return self._handle_callback()
    
    def _handle_callback(self):
        """处理微信回调"""
        if request.method == 'GET':
            return self._verify_wechat_server()
        elif request.method == 'POST':
            return self._handle_wechat_event()
        else:
            abort(405)
    
    def _verify_wechat_server(self):
        """验证微信服务器请求"""
        try:
            signature = request.args.get('signature', '')
            timestamp = request.args.get('timestamp', '')
            nonce = request.args.get('nonce', '')
            echostr = request.args.get('echostr', '')
            
            # 验证签名
            if self._check_signature(signature, timestamp, nonce):
                return echostr
            else:
                abort(403)
        except Exception as e:
            print(f"验证微信服务器失败: {e}")
            abort(403)
    
    def _handle_wechat_event(self):
        """处理微信事件"""
        try:
            # 解析XML数据
            xml_data = request.data
            root = ET.fromstring(xml_data)
            
            # 获取事件类型
            event = root.find('Event').text if root.find('Event') is not None else None
            
            if event == 'MASSSENDJOBFINISH':
                return self._handle_mass_send_finish(root)
            else:
                print(f"未知事件类型: {event}")
                return "success"
        except Exception as e:
            print(f"处理微信事件失败: {e}")
            return "success"
    
    def _handle_mass_send_finish(self, root):
        """处理MASSSENDJOBFINISH事件"""
        try:
            # 解析事件数据
            msg_id = root.find('MsgID').text if root.find('MsgID') is not None else None
            status = root.find('Status').text if root.find('Status') is not None else None
            total_count = root.find('TotalCount').text if root.find('TotalCount') is not None else '0'
            filter_count = root.find('FilterCount').text if root.find('FilterCount') is not None else '0'
            sent_count = root.find('SentCount').text if root.find('SentCount') is not None else '0'
            error_count = root.find('ErrorCount').text if root.find('ErrorCount') is not None else '0'
            
            print(f"接收到群发消息完成事件:")
            print(f"  MsgID: {msg_id}")
            print(f"  Status: {status}")
            print(f"  TotalCount: {total_count}")
            print(f"  FilterCount: {filter_count}")
            print(f"  SentCount: {sent_count}")
            print(f"  ErrorCount: {error_count}")
            
            # 根据msg_id查询消息记录
            message = self.db_manager.get_message_by_msg_id(msg_id)
            if message:
                # 更新消息状态
                if status == 'send success':
                    new_status = 1  # 发送成功
                else:
                    new_status = 2  # 发送失败
                
                # 更新消息状态和详细信息
                self.db_manager.update_message_status(
                    message_id=message['id'],
                    status=new_status,
                    send_time=datetime.now(),
                    total_count=int(total_count),
                    filter_count=int(filter_count),
                    sent_count=int(sent_count),
                    error_count=int(error_count),
                    msg_status_detail=status
                )
            
            return "success"
        except Exception as e:
            print(f"处理群发消息完成事件失败: {e}")
            return "success"
    
    def _check_signature(self, signature, timestamp, nonce):
        """验证签名"""
        # 将token、timestamp、nonce三个参数进行字典序排序
        params = [self.token, timestamp, nonce]
        params.sort()
        
        # 将三个参数字符串拼接成一个字符串进行sha1加密
        combined = ''.join(params)
        hash_str = hashlib.sha1(combined.encode()).hexdigest()
        
        # 验证加密后的字符串是否与signature相等
        return hash_str == signature
    
    def run(self):
        """启动Web服务器"""
        callback_config = self.config.get_wechat_config().get("callback", {})
        host = callback_config.get("host", "0.0.0.0")
        port = callback_config.get("port", 80)
        
        print(f"启动微信回调服务器，监听 {host}:{port}")
        print(f"回调URL: http://{host}:{port}/wechat/callback")
        
        # 使用线程方式启动，避免阻塞主程序
        from threading import Thread
        server_thread = Thread(target=self.app.run, kwargs={
            'host': host,
            'port': port,
            'debug': False
        })
        server_thread.daemon = True
        server_thread.start()
        
        return server_thread
