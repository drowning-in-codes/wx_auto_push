# 微信公众号自动推送程序

本项目是一个微信公众号自动推送程序，支持从多个数据源爬取内容，包括动漫新闻和图片，并可选择性使用大模型改写内容，最后通过微信公众号自动推送给用户。

## 功能特性

- **多数据源支持**：
  - 动漫新闻：支持多个动漫网站的随机爬取
  - 图片：支持多个图片网站的随机爬取
- **大模型集成**：可选择性使用API调用大模型改写新闻内容
- **微信推送**：支持图文消息和图片消息的推送
- **智能调度**：根据配置文件定义每周发布频次，自动执行推送任务

## 项目结构

```
wx_auto_push/
├── main.py                # 主程序入口
├── config.json            # 配置文件
├── requirements.txt       # 依赖包
└── src/
    ├── crawlers/          # 爬虫模块
    │   ├── base_crawler.py
    │   ├── anime_crawler.py
    │   ├── image_crawler.py
    │   └── crawler_factory.py
    ├── models/            # 数据模型
    ├── push/              # 推送模块
    │   ├── wechat_client.py
    │   └── wechat_push_service.py
    ├── scheduler/         # 调度模块
    │   └── schedule_manager.py
    └── utils/             # 工具模块
        ├── config.py
        └── llm_client.py
```

## 环境要求

- Python 3.7+
- 依赖包：requests, beautifulsoup4, lxml, apscheduler, wechatpy

## 安装步骤

1. 克隆项目到本地

2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置 `config.json` 文件：
   - 填写微信公众号的 app_id 和 app_secret
   - 配置数据源 URL
   - 设置大模型 API 配置（可选）
   - 定义每周发布频次

## 配置说明

### config.json 配置项

```json
{
  "wechat": {
    "app_id": "your_app_id",           # 微信公众号AppID
    "app_secret": "your_app_secret",   # 微信公众号AppSecret
    "template_id": "your_template_id"  # 模板消息ID（可选）
  },
  "data_sources": {
    "anime": [                         # 动漫新闻数据源
      "https://news.dmzj.com/",
      "https://www.acfun.cn/",
      "https://www.bilibili.com/anime/",
      "https://www.iqiyi.com/dongman/"
    ],
    "images": [                        # 图片数据源
      "https://www.pixiv.net/",
      "https://wallhaven.cc/",
      "https://unsplash.com/",
      "https://www.pexels.com/"
    ]
  },
  "llm": {
    "enabled": false,                  # 是否启用大模型
    "api_key": "your_api_key",         # 大模型API密钥
    "api_url": "https://api.example.com/llm",  # 大模型API地址
    "prompt": "请将以下新闻内容改写为更生动有趣的微信公众号文章风格："  # 改写提示词
  },
  "schedule": {
    "weekly_frequency": 3,             # 每周推送频次
    "time_range": {                    # 推送时间范围
      "start": "08:00",
      "end": "20:00"
    }
  },
  "push": {
    "content_types": ["text", "image"],  # 推送内容类型
    "max_retry": 3                     # 最大重试次数
  }
}
```

## 使用方法

### 1. 立即执行一次推送任务

```bash
python main.py run
```

### 2. 启动调度器，开始定时执行任务

```bash
python main.py start
```

### 3. 停止调度器

```bash
python main.py stop
```

## 注意事项

1. **微信公众号配置**：
   - 需要在微信公众平台设置中获取 AppID 和 AppSecret
   - 对于模板消息推送，需要提前创建模板并获取模板ID
   - 对于自定义消息推送，需要用户关注公众号并获取 OPENID

2. **爬虫注意事项**：
   - 本程序使用了网络爬虫技术，请遵守相关网站的 robots.txt 规则
   - 建议合理设置爬取频率，避免对目标网站造成过大压力

3. **大模型集成**：
   - 需要配置有效的大模型 API 密钥和地址
   - 大模型功能为可选配置，如不需要可设置 `enabled: false`

4. **定时任务**：
   - 调度器会根据配置的每周频次随机选择执行天数
   - 每次执行时间会在配置的时间范围内随机选择

## 故障排查

- **无法获取微信 access_token**：检查 AppID 和 AppSecret 是否正确
- **爬虫失败**：检查网络连接，或调整爬虫策略以适应目标网站结构变化
- **推送失败**：检查微信公众号权限，确保已开启相关接口权限
- **调度器未执行**：检查系统时间是否正确，或手动运行测试任务

## 扩展建议

1. **增加更多数据源**：可在 `config.json` 中添加更多的新闻和图片数据源
2. **优化爬虫策略**：针对不同网站定制更精确的爬虫规则
3. **增加内容过滤**：添加关键词过滤，确保推送内容符合要求
4. **添加日志系统**：记录推送历史和故障信息，便于排查问题
5. **支持更多推送渠道**：除微信公众号外，可扩展支持其他平台的推送

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。