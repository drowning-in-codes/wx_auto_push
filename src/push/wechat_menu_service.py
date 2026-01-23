from .wechat_client import WeChatClient


class WeChatMenuService:
    def __init__(self, client):
        """
        初始化微信菜单服务
        :param client: WeChatClient实例
        """
        self.client = client

    def create_menu(self, menu_config):
        """
        创建微信自定义菜单
        """
        if not menu_config or not menu_config.get("enabled", False):
            print("自定义菜单未启用，跳过创建")
            return None

        # 提取菜单按钮配置
        menu_data = {}
        if "button" in menu_config:
            menu_data["button"] = menu_config["button"]

        # 创建菜单
        result = self.client.create_menu(menu_data)
        print(f"创建自定义菜单结果: {result}")
        return result

    def get_menu(self):
        """
        获取微信自定义菜单配置
        仅能查询到使用API设置的菜单
        """
        return self.client.get_menu()

    def get_current_selfmenu_info(self):
        """
        查询当前微信自定义菜单信息
        该方法可以查询到使用API设置的菜单和公众平台官网设置的菜单
        """
        return self.client.get_current_selfmenu_info()

    def delete_menu(self):
        """
        删除微信自定义菜单
        """
        return self.client.delete_menu()

    def create_conditional_menu(self, menu_data):
        """
        创建个性化菜单
        """
        return self.client.create_conditional_menu(menu_data)

    def delete_conditional_menu(self, menu_id):
        """
        删除个性化菜单
        """
        return self.client.delete_conditional_menu(menu_id)

    def try_match_menu(self, user_id):
        """
        测试个性化菜单匹配结果
        """
        return self.client.try_match_menu(user_id)
