# 微信公众号自动推送程序

本项目是一个微信公众号自动推送程序，支持从多个数据源爬取内容，包括动漫新闻和图片，并可选择性使用大模型改写内容，最后通过微信公众号自动推送给用户。

## 功能特性

- **多数据源支持**：
  - 动漫新闻：支持多个动漫网站的随机爬取
  - 图片：支持多个图片网站的随机爬取
  - Pixivision 插画：支持从 Pixivision 网站爬取插画内容
- **大模型集成**：可选择性使用API调用大模型改写内容
- **微信推送**：支持图文消息和图片消息的推送
- **智能调度**：根据配置文件定义每周发布频次，自动执行推送任务
- **数据库记录**：每次执行任务后，在数据库中插入消息记录，包含详细信息和状态
- **消息状态检查**：35分钟后自动检查消息发送状态并更新数据库
- **预览消息**：发送前可选择将消息发送给公众号主人进行预览
- **代理配置**：支持HTTP/HTTPS代理设置，确保网络请求可通过代理路由
- **立即推送**：支持立即推送指定类型的内容，无需等待调度器
- **uv构建支持**：使用uv管理依赖和构建项目，提高安装速度
- **CLI工具化**：支持完整的命令行工具，包括配置管理、登录认证、素材管理等
- **Pixivision 服务**：支持从 Pixivision 网站爬取插画，包括列表页和详情页解析

## 项目结构

```
wx_auto_push/
├── main.py                # 主程序入口
├── config.json            # 配置文件
├── config.development.json.example  # 开发环境配置示例
├── config.production.json.example   # 生产环境配置示例
├── requirements.txt       # 依赖包
├── pyproject.toml         # uv项目配置
├── data.db                # SQLite数据库文件
├── .env.example           # 环境变量示例文件
├── .env                   # 环境变量文件
└── src/
    ├── crawlers/          # 爬虫模块
    │   ├── base_crawler.py
    │   ├── anime_crawler.py
    │   ├── image_crawler.py
    │   ├── crawler_factory.py
    │   └── pixivision_crawler.py  # Pixivision 爬虫
    ├── models/            # 数据模型
    ├── push/              # 推送模块
    │   ├── wechat_client.py
    │   ├── wechat_push_service.py
    │   ├── wechat_material_service.py  # 素材管理服务
    │   ├── wechat_menu_service.py      # 菜单管理服务
    │   ├── wechat_publish_service.py   # 发布管理服务
    │   ├── wechat_callback_server.py   # 回调服务器
    │   └── pixivision_service.py       # Pixivision 服务
    ├── scheduler/         # 调度模块
    │   └── schedule_manager.py
    └── utils/             # 工具模块
        ├── config.py
        ├── llm_client.py
        ├── cache_manager.py
        └── db_manager.py  # 数据库管理模块
```

## 环境要求

- Python 3.13+
- 依赖包：requests, beautifulsoup4, lxml, apscheduler, wechatpy, redis, python-dotenv
- 可选：uv 0.9.26+ (用于依赖管理和构建)
- 可选：Redis (用于缓存 access token，默认使用本地文件缓存)

## 安装步骤

### 方法1：使用pip安装

1. 克隆项目到本地

2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

### 方法2：使用uv安装（推荐）

1. 克隆项目到本地

2. 安装uv（如果未安装）：
   ```bash
   pip install uv
   ```

3. 初始化并安装依赖：
   ```bash
   uv sync
   ```

4. 配置环境变量：
   - 复制 `.env.example` 文件为 `.env`
   - 填写微信公众号的 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`
   - 其他配置项可根据需要修改

5. 配置 `config.json` 文件（可选）：
   - 配置数据源 URL
   - 设置大模型 API 配置（可选）
   - 定义每周发布频次
   - 配置代理设置（可选）
   - 配置预览设置（可选）

## 配置说明

### 配置文件结构

项目支持三种配置文件：
- `config.development.json` - 开发环境配置
- `config.production.json` - 生产环境配置
- `config.json` - 默认配置

系统会根据 `NODE_ENV` 环境变量选择相应的配置文件，默认使用开发环境配置。

### 完整配置示例

```json
{
  "wechat": {
    "app_id": "your_app_id",
    "app_secret": "your_app_secret",
    "template_id": "your_template_id",
    "preview": {
      "enabled": false,
      "towxname": "your_wechat_name"
    }
  },
  "data_sources": {
    "anime": [
      "https://news.dmzj.com/",
      "https://www.acfun.cn/",
      "https://www.bilibili.com/anime/",
      "https://www.iqiyi.com/dongman/",
      "https://www.3dmgame.com/news_74_1/"
    ],
    "images": [
      "https://www.pixiv.net/",
      "https://wallhaven.cc/",
      "https://unsplash.com/",
      "https://www.pexels.com/"
    ]
  },
  "llm": {
    "enabled": false,
    "model": "openai",
    "openai": {
      "api_key": "your_api_key",
      "api_url": "https://api.openai.com/v1/chat/completions",
      "prompt": "请将以下新闻内容改写为更生动有趣的微信公众号文章风格："
    },
    "gemini": {
      "api_key": "your_gemini_api_key",
      "api_url": "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-lite:generateContent",
      "prompt": "请将以下新闻内容改写为更生动有趣的微信公众号文章风格："
    }
  },
  "schedule": {
    "weekly_frequency": 3,
    "time_range": {
      "start": "08:00",
      "end": "20:00"
    }
  },
  "push": {
    "content_types": ["text", "image"],
    "max_retry": 3,
    "image_publish_type": "image"  // 可选值：image（图片消息）或 news（图文消息）
  },
  "proxy": {
    "enabled": false,
    "http_proxy": "http://localhost:7890",
    "https_proxy": "http://localhost:7890"
  }
}
```

### 环境变量支持

项目支持从环境变量覆盖配置，主要环境变量包括：

- `WECHAT_APP_ID` - 微信公众号AppID
- `WECHAT_APP_SECRET` - 微信公众号AppSecret
- `WECHAT_PREVIEW_ENABLED` - 是否启用预览功能
- `WECHAT_PREVIEW_TOWXNAME` - 预览接收者微信号
- `WECHAT_TOKEN` - 微信服务器验证Token
- `WECHAT_CALLBACK_ENABLED` - 是否启用回调服务器
- `WECHAT_CALLBACK_HOST` - 回调服务器主机地址
- `WECHAT_CALLBACK_PORT` - 回调服务器端口
- `IMAGE_PUBLISH_TYPE` - 图片发布方式，可选值：image（图片消息）或 news（图文消息）
- `PROXY_ENABLED` - 是否启用代理
- `HTTP_PROXY` - HTTP代理地址
- `HTTPS_PROXY` - HTTPS代理地址
- `LLM_ENABLED` - 是否启用大模型
- `NODE_ENV` - 运行环境（development/production）
- `CACHE_TYPE` - 缓存类型，可选值：file（文件缓存）或 redis（Redis缓存）
- `REDIS_HOST` - Redis主机地址
- `REDIS_PORT` - Redis端口
- `REDIS_PASSWORD` - Redis密码
- `REDIS_DB` - Redis数据库编号

### 自定义菜单配置

项目支持通过配置文件自定义微信公众号菜单，示例配置如下：

```json
"wechat": {
  "menu": {
    "enabled": true,
    "button": [
      {
        "type": "click",
        "name": "今日新闻",
        "key": "today_news"
      },
      {
        "name": "图片",
        "sub_button": [
          {
            "type": "click",
            "name": "动漫图片",
            "key": "anime_images"
          },
          {
            "type": "click",
            "name": "随机图片",
            "key": "random_images"
          }
        ]
      },
      {
        "type": "view",
        "name": "官网",
        "url": "https://www.example.com"
      }
    ]
  }
}
```

菜单类型支持：
- `click` - 点击推事件
- `view` - 跳转URL
- `scancode_push` - 扫码推事件
- `scancode_waitmsg` - 扫码推事件且弹出“消息接收中”提示框
- `pic_sysphoto` - 弹出系统拍照发图
- `pic_photo_or_album` - 弹出拍照或者相册发图
- `pic_weixin` - 弹出微信相册发图器
- `location_select` - 弹出地理位置选择器

菜单配置需要通过运行 `python main.py config` 命令手动初始化，创建或更新自定义菜单。

## 使用方法

### 1. 立即执行一次推送任务

```bash
# 使用pip
python main.py run

# 使用uv
uv run python main.py run
```

### 2. 立即推送指定类型的内容

```bash
# 随机类型
python main.py push

# 指定文本类型
python main.py push text

# 指定图片类型
python main.py push image

# 使用uv
uv run python main.py push [text|image]
```

### 3. 启动调度器，开始定时执行任务

```bash
# 使用pip
python main.py start

# 使用uv
uv run python main.py start
```

### 4. 停止调度器

```bash
# 使用pip
python main.py stop

# 使用uv
uv run python main.py stop
```

### 5. 登录微信公众号

```bash
# 使用pip
python main.py login

# 使用uv
uv run python main.py login
```

该命令用于使用已配置的 appid 和 app secret 获取并存储 access token，如果已有 token 则使用，如果之前的 token 已过期则重新登陆更新。

### 6. 配置微信公众号

```bash
# 创建自定义菜单
python main.py config menu

# 设置微信公众号配置
python main.py config set --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET

# 使用uv
uv run python main.py config [menu|set]
```

- `config menu`：根据配置文件创建自定义菜单
- `config set`：设置微信公众号配置，包括 app_id、app_secret 等

### 7. 素材管理

素材管理命令用于管理公众号的永久素材和临时素材，支持获取、上传、删除等操作。

```bash
# 获取素材总数
python main.py material count

# 列出素材（暂未实现）
python main.py material list [image|voice|video|thumb]

# 获取指定素材
python main.py material get <media_id>

# 上传永久素材
python main.py material upload <type> <file_path> [title] [description]

# 删除永久素材
python main.py material delete <media_id>

# 使用uv
uv run python main.py material <subcommand> [args]
```

**参数说明：**
- `<type>`: 素材类型，可选值：image（图片）、voice（语音）、video（视频）和缩略图（thumb）
- `<file_path>`: 素材文件路径
- `<title>`: 视频素材标题（仅视频类型需要）
- `<description>`: 视频素材简介（仅视频类型需要）
- `<media_id>`: 素材的media_id

**注意事项：**
- 永久素材保存总数量有上限：图文消息素材、图片素材上限为100000，其他类型为1000
- 素材的格式大小等要求与公众平台官网一致
- 临时素材保存时间为3天，3天后media_id失效

### 素材类型说明

| 类型    | 描述                 | 限制条件                                                                 |
|---------|----------------------|--------------------------------------------------------------------------|
| image   | 图片素材             | 10M，支持bmp/png/jpeg/jpg/gif格式                                        |
| voice   | 语音素材             | 2M，播放长度不超过60s，mp3/wma/wav/amr格式                                |
| video   | 视频素材             | 10MB，支持MP4格式，需要提供title和description                            |
| thumb   | 缩略图素材           | 64KB，支持JPG格式                                                       |
| news    | 图文素材             | 需通过其他接口创建，不支持直接上传                                       |
| newsimg | 图文消息内图片       | 1MB以下，仅支持jpg/png格式，不占用素材库数量限制                          |

### 素材管理命令示例

```bash
# 获取素材总数
python main.py material count

# 上传图片素材
python main.py material upload image ./test.jpg

# 上传视频素材，带标题和简介
python main.py material upload video ./test.mp4 "视频标题" "视频简介"

# 删除素材
python main.py material delete MEDIA_ID
```

### 8. Pixivision 管理

Pixivision 管理命令用于从 Pixivision 网站爬取插画内容，支持获取插画列表、详情和推送。

```bash
# 获取插画列表（默认第1页）
python main.py pixivision list

# 获取指定页码范围的插画列表
python main.py pixivision list 1 3

# 获取指定插画的详情
python main.py pixivision get 11525

# 推送指定插画到微信
python main.py pixivision push 11525

# 使用uv
uv run python main.py pixivision [list|get|push] [args]
```

**参数说明：**
- `list`：获取插画列表，可指定开始页码和结束页码
- `get`：获取指定插画的详情，需要提供插画ID
- `push`：推送指定插画到微信，需要提供插画ID

## 注意事项
注意，根据目前公众号平台,许多接口(例如群发)都需要认证。具体请查看(群发接口)["https://developers.weixin.qq.com/doc/service/api/notify/message/api_sendall.html"]。
而企业认证需要缴年费，这也是微信赚钱的一种方式吧。

1. **微信公众号配置**：
   - 需要在微信公众平台设置中获取 AppID 和 AppSecret
   - 对于模板消息推送，需要提前创建模板并获取模板ID
   - 对于自定义消息推送，需要用户关注公众号并获取 OPENID

2. **爬虫注意事项**：
   - 本程序使用了网络爬虫技术，请遵守相关网站的 robots.txt 规则
   - 建议合理设置爬取频率，避免对目标网站造成过大压力
   - Pixivision 爬虫可能会受到网站访问限制，建议使用代理

3. **大模型集成**：
   - 需要配置有效的大模型 API 密钥和地址
   - 大模型功能为可选配置，如不需要可设置 `enabled: false`

4. **定时任务**：
   - 调度器会根据配置的每周频次随机选择执行天数
   - 每次执行时间会在配置的时间范围内随机选择

5. **数据库**：
   - 项目使用SQLite数据库，自动创建 `data.db` 文件
   - 数据库记录包含详细的消息信息和状态，便于后续查询

6. **预览消息**：
   - 预览消息功能每日调用次数有限制（100次），请勿滥用
   - 需要配置公众号主人的微信号 `towxname`

7. **代理配置**：
   - 如需要通过代理访问网络，可在配置文件中设置代理信息
   - 支持HTTP和HTTPS代理

8. **回调URL配置**：
   - 用于接收微信服务器的群发消息结果通知
   - 需要在微信公众平台设置中配置对应的URL和Token
   - 支持自定义端口和主机地址
   - 自动处理MASSSENDJOBFINISH事件，更新消息状态

9. **数据库记录**：
   - 每条群发消息都会在数据库中保存详细记录
   - 包含发送状态、成功人数、失败人数等信息
   - 支持通过msg_id查询具体消息的发送结果

10. **Access Token 存储**：
    - 默认使用本地文件缓存存储 access token
    - 可通过配置 `CACHE_TYPE=redis` 启用 Redis 缓存
    - Redis 缓存需要配置相应的 Redis 服务器信息

11. **Pixivision 服务**：
    - 支持从 Pixivision 网站爬取插画内容
    - 可获取插画列表和详情
    - 支持推送插画到微信公众号

## 故障排查

- **无法获取微信 access_token**：检查 AppID 和 AppSecret 是否正确，以及网络连接是否正常
- **爬虫失败**：检查网络连接，或调整爬虫策略以适应目标网站结构变化
- **Pixivision 爬虫失败**：检查网络连接，尝试使用代理，或检查网站是否有访问限制
- **推送失败**：检查微信公众号权限，确保已开启相关接口权限
- **调度器未执行**：检查系统时间是否正确，或手动运行测试任务
- **数据库错误**：检查数据库文件权限，确保程序有读写权限
- **预览失败**：检查 `towxname` 是否正确，以及每日调用次数是否超限
- **Access Token 缓存失败**：检查缓存目录权限，或配置 Redis 缓存

## 扩展建议

1. **增加更多数据源**：可在配置文件中添加更多的新闻和图片数据源
2. **优化爬虫策略**：针对不同网站定制更精确的爬虫规则
3. **增加内容过滤**：添加关键词过滤，确保推送内容符合要求
4. **添加日志系统**：记录推送历史和故障信息，便于排查问题
5. **支持更多推送渠道**：除微信公众号外，可扩展支持其他平台的推送
6. **使用开发者沙箱**: [沙箱]("https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo?action=showinfo&t=sandbox/index"),[接口浏览]("https://developers.weixin.qq.com/apiExplorer")以及[调试工具]("https://mp.weixin.qq.com/debug")

## 微信API URL清单

### 基础API

| 功能 | URL | 方法 |
|------|-----|------|
| 获取access_token | `https://api.weixin.qq.com/cgi-bin/token` | GET |

### 自定义菜单API

| 功能 | URL | 方法 |
|------|-----|------|
| 创建自定义菜单 | `https://api.weixin.qq.com/cgi-bin/menu/create` | POST |
| 查询自定义菜单信息 | `https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info` | GET |
| 获取自定义菜单配置 | `https://api.weixin.qq.com/cgi-bin/menu/get` | GET |
| 删除自定义菜单 | `https://api.weixin.qq.com/cgi-bin/menu/delete` | GET |
| 创建个性化菜单 | `https://api.weixin.qq.com/cgi-bin/menu/addconditional` | POST |
| 删除个性化菜单 | `https://api.weixin.qq.com/cgi-bin/menu/delconditional` | POST |
| 测试个性化菜单匹配 | `https://api.weixin.qq.com/cgi-bin/menu/trymatch` | POST |

### 素材管理API

#### 永久素材
| 功能 | URL | 方法 |
|------|-----|------|
| 获取永久素材总数 | `https://api.weixin.qq.com/cgi-bin/material/get_materialcount` | GET |
| 获取永久素材 | `https://api.weixin.qq.com/cgi-bin/material/get_material` | POST |
| 上传永久素材 | `https://api.weixin.qq.com/cgi-bin/material/add_material` | POST |
| 删除永久素材 | `https://api.weixin.qq.com/cgi-bin/material/del_material` | POST |

#### 临时素材
| 功能 | URL | 方法 |
|------|-----|------|
| 获取临时素材 | `https://api.weixin.qq.com/cgi-bin/media/get` | GET |
| 上传临时素材 | `https://api.weixin.qq.com/cgi-bin/media/upload` | POST |
| 获取高清语音素材 | `https://api.weixin.qq.com/cgi-bin/media/get/jssdk` | GET |

#### 图文消息素材
| 功能 | URL | 方法 |
|------|-----|------|
| 上传图文消息素材 | `https://api.weixin.qq.com/cgi-bin/media/uploadnews` | POST |
| 上传图文消息内图片 | `https://api.weixin.qq.com/cgi-bin/media/uploadimg` | POST |

### 消息发送API

| 功能 | URL | 方法 |
|------|-----|------|
| 预览消息 | `https://api.weixin.qq.com/cgi-bin/message/mass/preview` | POST |
| 查询群发消息发送状态 | `https://api.weixin.qq.com/cgi-bin/message/mass/get` | POST |
| 删除群发消息 | `https://api.weixin.qq.com/cgi-bin/message/mass/delete` | POST |
| 按标签群发消息 | `https://api.weixin.qq.com/cgi-bin/message/mass/sendall` | POST |
| 按OpenID列表群发消息 | `https://api.weixin.qq.com/cgi-bin/message/mass/send` | POST |
| 发送模板消息 | `https://api.weixin.qq.com/cgi-bin/message/template/send` | POST |
| 发送客服消息 | `https://api.weixin.qq.com/cgi-bin/message/custom/send` | POST |

### 发布管理API

| 功能 | URL | 方法 |
|------|-----|------|
| 获取已发布的消息列表 | `https://api.weixin.qq.com/cgi-bin/freepublish/batchget` | POST |
| 获取已发布的图文信息 | `https://api.weixin.qq.com/cgi-bin/freepublish/getarticle` | POST |
| 删除发布文章 | `https://api.weixin.qq.com/cgi-bin/freepublish/delete` | POST |
| 发布状态查询 | `https://api.weixin.qq.com/cgi-bin/freepublish/get` | POST |
| 发布草稿 | `https://api.weixin.qq.com/cgi-bin/freepublish/submit` | POST |

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。