# 微信公众号自动推送程序

本项目是一个微信公众号自动推送程序，支持从多个数据源爬取内容，包括动漫新闻和图片，并可选择性使用大模型改写内容，最后通过微信公众号自动推送给用户。
![微信公众号自动推送](./wx_auto_push.png)

## 功能特性

- **多数据源支持**：
  - 动漫新闻：支持多个动漫网站的随机爬取
  - 图片：支持多个图片网站的随机爬取
  - Pixivision 插画：支持从 Pixivision 网站爬取插画内容
- **大模型集成**：可选择性使用API调用大模型改写内容
- **微信推送**：支持图文消息和图片消息的推送
- **智能调度**：根据配置文件定义每周发布频次，自动执行推送任务
- **调度上传**：支持定时从随机Pixivision插画创建草稿，自动记录已上传的article id避免重复
- **登录认证**：支持获取稳定版access_token，自动缓存管理，避免频繁请求API
- **数据库记录**：每次执行任务后，在数据库中插入消息记录，包含详细信息和状态
- **消息状态检查**：35分钟后自动检查消息发送状态并更新数据库
- **预览消息**：发送前可选择将消息发送给公众号主人进行预览
- **代理配置**：支持HTTP/HTTPS代理设置，确保网络请求可通过代理路由
- **代理池支持**：支持从代理池API获取代理，提高爬取的稳定性和可靠性
- **立即推送**：支持立即推送指定类型的内容，无需等待调度器
- **uv构建支持**：使用uv管理依赖和构建项目，提高安装速度
- **CLI工具化**：支持完整的命令行工具，包括配置管理、登录认证、永久素材管理等
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
    │   ├── wechat_material_service.py  # 永久素材管理服务
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
  },
  "proxy_pool": {
    "enabled": false,
    "api_url": "https://proxy.scdn.io/api/get_proxy.php",
    "protocol": "all",
    "count": 5,
    "country_code": "",
    "fetch_interval": 60,
    "max_proxies": 10,
    "proxy_config": {
      "enabled": false,
      "http_proxy": "http://localhost:7890",
      "https_proxy": "http://localhost:7890"
    }
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
- `PROXY_POOL_ENABLED` - 是否启用代理池
- `PROXY_POOL_API_URL` - 代理池API地址
- `PROXY_POOL_PROTOCOL` - 代理协议类型
- `PROXY_POOL_COUNT` - 每次获取的代理数量
- `PROXY_POOL_COUNTRY_CODE` - 代理国家代码
- `PROXY_POOL_FETCH_INTERVAL` - 代理刷新间隔（秒）
- `PROXY_POOL_MAX_PROXIES` - 最大代理数量
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

### 5. 调度管理

调度管理命令用于配置和运行定时推送任务。

```bash
# 设置推送时间范围
python main.py schedule time --start 08:00 --end 20:00

# 设置每周推送频次
python main.py schedule frequency --weekly-frequency 3

# 查看调度配置
python main.py schedule view

# 启动调度器（持续运行）
python main.py schedule run

# 执行一次推送任务后退出
python main.py schedule run-once

# 启动调度上传（从随机Pixivision插画创建草稿）
python main.py schedule upload --start_page 1 --end_page 3

# 执行一次上传任务后退出
python main.py schedule upload-once --start_page 1 --end_page 3

# 使用uv
uv run python main.py schedule [time|frequency|view|run|run-once|upload|upload-once] [args]
```

**参数说明：**

- `time`：设置推送时间范围
  - `--start`：开始时间，格式 HH:MM，默认 08:00
  - `--end`：结束时间，格式 HH:MM，默认 20:00
- `frequency`：设置每周推送频次
  - `--weekly-frequency`：每周推送次数，默认 3
- `view`：查看当前调度配置
- `run`：启动调度器，持续运行直到手动停止
- `run-once`：执行一次推送任务后退出
- `upload`：启动调度上传，从随机Pixivision插画创建草稿
  - `--start_page`：开始页码，默认 1
  - `--end_page`：结束页码，默认 3
  - `--title`：草稿标题（可选）
  - `--author`：作者名称（可选）
  - `--compress`：是否压缩图片（可选）
  - `--digest`：图文消息摘要（可选）
  - `--content`：图文消息内容（可选）
  - `--show_cover`：是否显示封面图片，默认 1
  - `--message_type`：消息类型，news(图文消息)或newspic(图片消息)，默认 newspic
- `upload-once`：执行一次上传任务后退出，参数同upload

**配置项：**

在 `config.json` 中可以配置调度参数：

```json
{
  "schedule": {
    "weekly_frequency": 3,
    "time_range": {
      "start": "08:00",
      "end": "20:00"
    },
    "upload": {
      "start_page": 1,
      "end_page": 3,
      "title": "",
      "author": "",
      "compress": true,
      "digest": "",
      "content": "",
      "show_cover": 1,
      "message_type": "newspic"
    }
  }
}
```

**上传历史：**

使用 `schedule upload` 命令时，系统会自动创建一个 `uploaded_articles.json` 文件来记录已上传的article id，避免重复上传。该文件包含以下信息：

```json
{
  "12345": {
    "upload_time": "2026-03-29T10:30:00",
    "draft_media_id": "media_id_12345"
  }
}
```

如果需要清空上传历史，可以删除 `uploaded_articles.json` 文件。

### 6. 登录微信公众号

```bash
# 使用pip
python main.py login

# 使用uv
uv run python main.py login
```

该命令用于使用已配置的 appid 和 app secret 获取并存储 access token，如果已有 token 则使用，如果之前的 token 已过期则重新登陆更新。

### 7. 配置微信公众号

```bash
# 创建自定义菜单
python main.py config menu

# 设置微信公众号配置
python main.py config set --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET

# 使用uv
uv run python main.py config [menu|set]
```

- `config menu`：根据配置文件创建自定义菜单
- `config set`：设置微信公众号配置，包括 app\_id、app\_secret 等

### 8. 登录获取Token

```bash
# 获取稳定版access_token
python main.py login

# 使用uv
uv run python main.py login
```

该命令会调用微信API获取稳定版access_token，并自动缓存到本地。Token有效期为2小时，过期后会自动刷新。

**功能说明：**
- 获取稳定版access_token（推荐使用，比普通token更稳定）
- 自动缓存token，避免频繁请求微信API
- 支持代理配置，确保网络请求成功

### 9. 永久素材管理

永久素材管理命令用于管理公众号的永久素材，支持获取、上传、删除等操作。

```bash
# 获取永久素材总数
python main.py material count

# 列出永久素材
python main.py material list <type>

# 获取指定永久素材
python main.py material get <media_id>

# 上传永久素材
python main.py material upload <type> <file_path> [title] [description]

# 删除永久素材
python main.py material delete <media_id>

# 使用uv
uv run python main.py material <subcommand> [args]
```

**参数说明：**

- `<type>`: 素材类型，可选值：image（图片）、voice（语音）、video（视频）、thumb（缩略图）和 news（图文）
- `<file_path>`: 素材文件路径
- `<title>`: 视频素材标题（仅视频类型需要）
- `<description>`: 视频素材简介（仅视频类型需要）
- `<media_id>`: 素材的media\_id

**注意事项：**

- 永久素材保存总数量有上限：图文消息素材、图片素材上限为100000，其他类型为1000
- 素材的格式大小等要求与公众平台官网一致

### 9. 临时素材管理

临时素材管理命令用于管理公众号的临时素材，支持上传和获取操作。

```bash
# 获取临时素材
python main.py material temporary get <media_id>

# 上传临时素材
python main.py material temporary upload <type> <file_path>

# 使用uv
uv run python main.py material temporary <subcommand> [args]
```

**参数说明：**

- `<type>`: 素材类型，可选值：image（图片）、voice（语音）、video（视频）和 thumb（缩略图）
- `<file_path>`: 素材文件路径
- `<media_id>`: 素材的media\_id

**注意事项：**

- 临时素材保存时间为3天，3天后media\_id失效
- 临时素材不占用素材库数量限制

### 素材类型说明

| 类型      | 描述      | 限制条件                               |
| ------- | ------- | ---------------------------------- |
| image   | 图片素材    | 10M，支持bmp/png/jpeg/jpg/gif格式       |
| voice   | 语音素材    | 2M，播放长度不超过60s，mp3/wma/wav/amr格式    |
| video   | 视频素材    | 10MB，支持MP4格式，需要提供title和description |
| thumb   | 缩略图素材   | 64KB，支持JPG格式                       |
| news    | 图文素材    | 需通过其他接口创建，不支持直接上传                  |
| newsimg | 图文消息内图片 | 1MB以下，仅支持jpg/png格式，不占用素材库数量限制      |

### 永久素材管理命令示例

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

### 10. Pixivision 管理

Pixivision 管理命令用于从 Pixivision 网站爬取插画内容，支持获取插画列表、详情、推送和上传图片。

```bash
# 获取插画列表（默认第1页）
python main.py pixivision list

# 获取指定页码范围的插画列表
python main.py pixivision list --start-page 1 --end-page 3

# 搜索插画
python main.py pixivision list --query "搜索关键词"

# 获取指定插画的详情
python main.py pixivision detail 11525

# 获取排行榜
python main.py pixivision ranking

# 获取推荐榜
python main.py pixivision recommendations

# 推送指定插画到微信
python main.py pixivision push

# 下载指定插画的图片到本地
python main.py pixivision download 11525

# 下载到指定目录
python main.py pixivision download 11525 --output ./my_downloads

# 存储插画信息
python main.py pixivision store 11525

# 查看已存储的插画
python main.py pixivision stored

# 搜索已存储的插画
python main.py pixivision search "关键词"

# 使用uv
uv run python main.py pixivision [list|detail|ranking|recommendations|push|download|store|stored|search] [args]
```

**参数说明：**

- `list`：获取插画列表
  - `--start-page`：可选参数，开始页码，默认1
  - `--end-page`：可选参数，结束页码，默认1
  - `--query`：可选参数，搜索关键词
  - `--save`：可选参数，是否保存到存储
- `detail`：获取指定插画的详情，需要提供插画ID
  - `--save`：可选参数，是否保存到存储
- `ranking`：获取排行榜插画列表
  - `--save`：可选参数，是否保存到存储
- `recommendations`：获取推荐榜插画列表
  - `--save`：可选参数，是否保存到存储
- `push`：推送插画到微信
- `download`：下载插画图片到本地
  - `illustration_id`：插画ID（必需）
  - `--output`：可选参数，输出目录，默认使用配置文件中的目录
- `store`：存储插画信息到本地
  - `illustration_id`：插画ID（必需）
- `stored`：查看已存储的插画列表
  - `--limit`：可选参数，返回数量限制，默认10
  - `--offset`：可选参数，偏移量，默认0
- `search`：搜索已存储的插画
  - `keyword`：搜索关键词（必需）
  - `--limit`：可选参数，返回数量限制，默认10

**下载功能：**

- 支持多线程下载（可配置线程数，默认5个）
- 支持失败重试（可配置重试次数，默认3次）
- 使用插画标题作为文件夹名称
- 图片按序号命名（001.jpg, 002.jpg 等）
- 可通过配置文件 `config.json` 中的 `download` 配置项自定义下载参数：
  - `max_workers`: 最大线程数，默认 5
  - `max_retries`: 最大重试次数，默认 3
  - `directory`: 下载目录，默认 "./downloads"

**图片压缩功能：**

- 上传图片时会自动检查文件大小
- 超过阈值的图片会自动压缩（默认阈值1MB）
- 压缩过程会调整图片尺寸（最大边长2000像素）和质量（85%）
- 压缩后的图片会自动清理临时文件
- 可通过配置文件 `config.json` 中的 `image_compression` 配置项自定义压缩参数：
  - `enabled`: 是否启用压缩，默认 true
  - `max_size`: 最大文件大小（字节），默认 1048576（1MB）
  - `max_dimension`: 最大边长（像素），默认 2000
  - `quality`: JPEG 压缩质量（1-100），默认 85

**存储功能：**

- 默认使用 JSON 存储，数据保存在 `data/illustrations.json` 文件中
- 支持 SQLite 数据库存储，可在初始化时指定 `storage_type='database'`
- 存储的信息包括：标题、文章ID、URL、描述、图片列表、标签、分类、缩略图等
- 可通过 `pixivision store` 命令存储插画信息
- 可通过 `pixivision stored` 命令查看已存储的插画
- 可通过 `pixivision search` 命令搜索已存储的插画

### 11. 草稿管理

草稿管理命令用于管理公众号的草稿箱，支持设置开关状态、新增草稿、获取草稿列表、获取草稿总数、删除草稿、获取草稿详情和更新草稿等操作。

#### 11.1 草稿箱开关设置

草稿箱开关设置用于开启或查询草稿箱和发布功能的开关状态。详细文档请参考：[草稿箱开关设置](https://developers.weixin.qq.com/doc/subscription/api/draftbox/draftmanage/api_draft_switch.html)

**注意事项：**

- 此接口应在服务器端调用，不可在前端（小程序、网页、APP等）直接调用
- 内测期间会逐步放量，任何用户都可能会自动打开
- 此开关开启后不可逆，换言之，无法从开启的状态回到关闭
- 内测期间，无论开关开启与否，旧版的图文素材API，以及新版的草稿箱、发布等API均可以正常使用
- 在内测结束之后，所有用户都将自动开启，即草稿箱、发布等功能将对所有用户开放

**命令示例：**

```bash
# 设置草稿箱开关状态（开启）
python main.py draft switch

# 仅检查草稿箱开关状态
python main.py draft switch --checkonly 1

# 设置草稿箱开关状态（关闭）
python main.py draft switch --checkonly 0
```

#### 11.2 草稿创建命令（图片自动上传）

`draft create` 命令可以自动上传图片到素材库并创建图文消息草稿，支持从本地文件夹或 Pixivision 文章ID获取图片。

**基本用法：**

```bash
# 从本地文件夹创建草稿（使用配置默认值）
python main.py draft create "./images/folder"

# 从 Pixivision 文章ID创建草稿
python main.py draft create 11525

# 指定标题和作者
python main.py draft create "./images/folder" --title "我的图片集" --author "作者名"

# 强制压缩/不压缩图片
python main.py draft create "./images/folder" --compress
python main.py draft create "./images/folder" --no-compress

# 创建图片消息草稿
python main.py draft create 11525 --message-type newspic

# 完整示例
python main.py draft create 11525 \
  --title "插画精选" \
  --author "小编" \
  --digest "精选插画作品" \
  --show-cover 1 \
  --message-type news
```

**参数说明：**

| 参数               | 说明                                | 默认值    |
| ---------------- | --------------------------------- | ------ |
| `source`         | 图片来源：本地文件夹路径或 Pixivision 文章ID     | 必填     |
| `--title`        | 草稿标题，默认使用文件夹名或插画标题                | 自动获取   |
| `--author`       | 作者名称，默认使用配置中的 `default_author`    | 配置值    |
| `--compress`     | 是否压缩图片                            | 使用配置   |
| `--digest`       | 图文消息摘要                            | 自动生成   |
| `--content`      | 图文消息内容（支持HTML）                    | 自动生成   |
| `--show-cover`   | 是否显示封面：1显示，0不显示                   | 1      |
| `--message-type` | 消息类型：`news`(图文消息)或`newspic`(图片消息) | `newspic` |

**配置项：**

在 `config.json` 中可以配置草稿默认值：

```json
{
  "draft": {
    "default_author": "公众号作者",
    "default_show_cover": 1
  }
}
```

#### 11.3 草稿管理命令

```bash
# 新增草稿
python main.py draft add '[{"title": "标题", "content": "内容", "thumb_media_id": "缩略图ID"}]'

# 获取草稿列表
python main.py draft list

# 获取草稿列表（指定偏移量和数量）
python main.py draft list --offset 0 --count 10

# 获取草稿列表（不返回内容）
python main.py draft list --no-content 1

# 获取草稿总数
python main.py draft count

# 删除草稿
python main.py draft delete <media_id>

# 获取草稿详情
python main.py draft get <media_id>

# 更新草稿
python main.py draft update <media_id> 0 '[{"title": "新标题", "content": "新内容", "thumb_media_id": "缩略图ID"}]'

# 发布草稿
python main.py draft submit <media_id>
```

# 使用uv

uv run python main.py draft <subcommand> \[args]


**参数说明：**
- `switch`：设置或查询草稿箱开关状态
  - `checkonly`：仅检查状态时传1，默认为0（设置状态）
- `add`：新增草稿
  - `title`：标题
  - `content`：内容
  - `thumb_media_id`：封面图片素材id（必须是永久MediaID）
  - `--author`：作者（可选）
  - `--digest`：摘要（可选）
  - `--content_source_url`：原文地址（可选）
- `list`：获取草稿列表
  - `offset`：偏移量，默认为0
  - `count`：数量，默认为10
  - `no_content`：是否返回内容，默认为0（返回内容）
- `count`：获取草稿总数
- `delete`：删除草稿
  - `media_id`：草稿的media_id
- `get`：获取草稿详情
  - `media_id`：草稿的media_id
- `update`：更新草稿
  - `media_id`：草稿的media_id
  - `index`：文章在图文消息中的位置，第一篇为0
  - `title`：标题
  - `content`：内容
  - `thumb_media_id`：封面图片素材id（必须是永久MediaID）
  - `--author`：作者（可选）
  - `--digest`：摘要（可选）
  - `--content_source_url`：原文地址（可选）

**注意事项：**
- 草稿箱开关开启后不可逆，无法从开启状态回到关闭
- 内测期间，无论开关开启与否，旧版的图文素材API以及新版的草稿箱、发布等API均可以正常使用
- 内测结束后，所有用户都将自动开启草稿箱功能
- 上传到草稿箱中的素材被群发或发布后，该素材将从草稿箱中移除
- 新增草稿也可在公众平台官网-草稿箱中查看和管理
- 删除草稿操作不可撤销，请谨慎操作

## 注意事项
注意，根据目前公众号平台,许多接口(例如群发)都需要认证。具体请查看[群发接口]('https://developers.weixin.qq.com/doc/service/api/notify/message/api_sendall.html').
而企业认证需要缴年费，这也是微信赚钱的一种方式吧。

此外，发布能力相关接口（如获取已发布的消息列表）也需要认证公众号或服务号才有权力使用，具体请查看[发布能力接口文档]('https://developers.weixin.qq.com/doc/subscription/api/public/api_freepublish_batchget.html')。

未认证公众号拥有的 API 访问能力包括：
- **素材管理**：支持上传和获取临时素材、永久素材
- **部分基础消息**：支持发送客服消息等基础消息功能
- **草稿管理**：支持创建和管理草稿

认证公众号或服务号可以访问更多高级功能，如群发消息、自定义菜单等。

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

8. **代理池配置**：
   - 支持从代理池API获取代理，提高爬取的稳定性和可靠性
   - 可配置协议类型、国家代码、获取数量等参数
   - 自动管理代理的刷新和选择
   - 当代理池未启用或未获取到代理时，会自动回退到传统代理配置
   - 可通过 proxy_config 配置连接代理池API时是否使用代理
   - proxy_config.enabled: 是否启用代理连接代理池API
   - proxy_config.http_proxy: HTTP代理地址
   - proxy_config.https_proxy: HTTPS代理地址
   - proxy_config 用于控制连接代理池API时是否使用代理，与爬取目标网站时使用的代理是独立的

9. **回调URL配置**：
   - 用于接收微信服务器的群发消息结果通知
   - 需要在微信公众平台设置中配置对应的URL和Token
   - 支持自定义端口和主机地址
   - 自动处理MASSSENDJOBFINISH事件，更新消息状态

10. **数据库记录**：
    - 每条群发消息都会在数据库中保存详细记录
    - 包含发送状态、成功人数、失败人数等信息
    - 支持通过msg_id查询具体消息的发送结果

11. **Access Token 存储**：
    - 默认使用本地文件缓存存储 access token
    - 可通过配置 `CACHE_TYPE=redis` 启用 Redis 缓存
    - Redis 缓存需要配置相应的 Redis 服务器信息

12. **Pixivision 服务**：
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

### 永久素材管理API

#### 永久素材
| 功能 | URL | 方法 |
|------|-----|------|
| 获取永久素材总数 | `https://api.weixin.qq.com/cgi-bin/material/get_materialcount` | GET |
| 获取永久素材列表 | `https://api.weixin.qq.com/cgi-bin/material/batchget_material` | POST |
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
| 上传图文消息素材 | `https://api.weixin.qq.com/cgi-bin/media/uploadnews` | POST | 说明：本接口用于上传图文消息，该能力已更新为草稿箱 |
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

### 草稿管理 API
| 功能 | URL | 方法 |
|------|-----|------|
| 草稿箱开关设置 | `https://api.weixin.qq.com/cgi-bin/draft/switch` | GET |
| 新增草稿 | `https://api.weixin.qq.com/cgi-bin/draft/add` | POST |
| 获取草稿列表 | `https://api.weixin.qq.com/cgi-bin/draft/batchget` | POST |
| 获取草稿总数 | `https://api.weixin.qq.com/cgi-bin/draft/count` | GET |
| 删除草稿 | `https://api.weixin.qq.com/cgi-bin/draft/delete` | POST |
| 获取草稿详情 | `https://api.weixin.qq.com/cgi-bin/draft/get` | POST |
| 更新草稿 | `https://api.weixin.qq.com/cgi-bin/draft/update` | POST |

### 发布管理API

| 功能 | URL | 方法 |
|------|-----|------|
| 获取已发布的消息列表 | `https://api.weixin.qq.com/cgi-bin/freepublish/batchget` | POST |
| 获取已发布的图文信息 | `https://api.weixin.qq.com/cgi-bin/freepublish/getarticle` | POST |
| 删除发布文章 | `https://api.weixin.qq.com/cgi-bin/freepublish/delete` | POST |
| 发布状态查询 | `https://api.weixin.qq.com/cgi-bin/freepublish/get` | POST |
| 发布草稿 | `https://api.weixin.qq.com/cgi-bin/freepublish/submit` | POST |
| 草稿箱开关设置 | `https://api.weixin.qq.com/cgi-bin/draft/switch` | POST |

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。
