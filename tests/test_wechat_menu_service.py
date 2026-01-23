import pytest
from unittest.mock import MagicMock
from src.push.wechat_menu_service import WeChatMenuService


class TestWeChatMenuService:
    """测试微信菜单服务"""

    @pytest.fixture
    def menu_service(self):
        """创建菜单服务实例，使用mock的微信客户端"""
        # 创建mock的微信客户端
        mock_client = MagicMock()
        # 创建菜单服务实例
        menu_service = WeChatMenuService(mock_client)
        return menu_service, mock_client

    def test_create_menu_enabled(self, menu_service):
        """测试创建启用的菜单"""
        menu_service_instance, mock_client = menu_service
        
        # 配置mock客户端的create_menu方法返回值
        mock_client.create_menu.return_value = {"errcode": 0, "errmsg": "ok"}
        
        # 测试数据
        menu_config = {
            "enabled": True,
            "button": [
                {
                    "type": "click",
                    "name": "今日新闻",
                    "key": "today_news"
                }
            ]
        }
        
        # 执行测试
        result = menu_service_instance.create_menu(menu_config)
        
        # 验证结果
        assert result == {"errcode": 0, "errmsg": "ok"}
        mock_client.create_menu.assert_called_once_with({"button": menu_config["button"]})

    def test_create_menu_disabled(self, menu_service):
        """测试创建未启用的菜单"""
        menu_service_instance, mock_client = menu_service
        
        # 测试数据
        menu_config = {
            "enabled": False,
            "button": [
                {
                    "type": "click",
                    "name": "今日新闻",
                    "key": "today_news"
                }
            ]
        }
        
        # 执行测试
        result = menu_service_instance.create_menu(menu_config)
        
        # 验证结果
        assert result is None
        mock_client.create_menu.assert_not_called()

    def test_get_menu(self, menu_service):
        """测试获取菜单配置"""
        menu_service_instance, mock_client = menu_service
        
        # 配置mock客户端的get_menu方法返回值
        expected_result = {"menu": {"button": [{"type": "click", "name": "今日新闻", "key": "today_news"}]}}
        mock_client.get_menu.return_value = expected_result
        
        # 执行测试
        result = menu_service_instance.get_menu()
        
        # 验证结果
        assert result == expected_result
        mock_client.get_menu.assert_called_once()

    def test_get_current_selfmenu_info(self, menu_service):
        """测试获取当前菜单信息"""
        menu_service_instance, mock_client = menu_service
        
        # 配置mock客户端的get_current_selfmenu_info方法返回值
        expected_result = {"is_menu_open": 1, "selfmenu_info": {"button": [{"type": "click", "name": "今日新闻", "key": "today_news"}]}}
        mock_client.get_current_selfmenu_info.return_value = expected_result
        
        # 执行测试
        result = menu_service_instance.get_current_selfmenu_info()
        
        # 验证结果
        assert result == expected_result
        mock_client.get_current_selfmenu_info.assert_called_once()

    def test_delete_menu(self, menu_service):
        """测试删除菜单"""
        menu_service_instance, mock_client = menu_service
        
        # 配置mock客户端的delete_menu方法返回值
        expected_result = {"errcode": 0, "errmsg": "ok"}
        mock_client.delete_menu.return_value = expected_result
        
        # 执行测试
        result = menu_service_instance.delete_menu()
        
        # 验证结果
        assert result == expected_result
        mock_client.delete_menu.assert_called_once()

    def test_create_conditional_menu(self, menu_service):
        """测试创建个性化菜单"""
        menu_service_instance, mock_client = menu_service
        
        # 配置mock客户端的create_conditional_menu方法返回值
        expected_result = {"errcode": 0, "errmsg": "ok", "menuid": "123456"}
        mock_client.create_conditional_menu.return_value = expected_result
        
        # 测试数据
        menu_data = {
            "button": [{"type": "click", "name": "今日新闻", "key": "today_news"}],
            "matchrule": {"tag_id": "100"}
        }
        
        # 执行测试
        result = menu_service_instance.create_conditional_menu(menu_data)
        
        # 验证结果
        assert result == expected_result
        mock_client.create_conditional_menu.assert_called_once_with(menu_data)

    def test_delete_conditional_menu(self, menu_service):
        """测试删除个性化菜单"""
        menu_service_instance, mock_client = menu_service
        
        # 配置mock客户端的delete_conditional_menu方法返回值
        expected_result = {"errcode": 0, "errmsg": "ok"}
        mock_client.delete_conditional_menu.return_value = expected_result
        
        # 执行测试
        menu_id = "123456"
        result = menu_service_instance.delete_conditional_menu(menu_id)
        
        # 验证结果
        assert result == expected_result
        mock_client.delete_conditional_menu.assert_called_once_with(menu_id)

    def test_try_match_menu(self, menu_service):
        """测试测试个性化菜单匹配结果"""
        menu_service_instance, mock_client = menu_service
        
        # 配置mock客户端的try_match_menu方法返回值
        expected_result = {"button": [{"type": "click", "name": "今日新闻", "key": "today_news"}]}
        mock_client.try_match_menu.return_value = expected_result
        
        # 执行测试
        user_id = "user123"
        result = menu_service_instance.try_match_menu(user_id)
        
        # 验证结果
        assert result == expected_result
        mock_client.try_match_menu.assert_called_once_with(user_id)
