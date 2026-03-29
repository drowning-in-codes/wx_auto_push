# 测试文档

本文档描述了微信公众号自动推送程序的单元测试设计和实现。

## 测试概述

项目采用 Python 标准库 `unittest` 作为测试框架，测试代码位于 `tests` 目录下。

## 测试结构

```
tests/
├── __init__.py                    # 测试包初始化
├── test_config.py                 # 配置模块测试
├── test_storage.py                # 存储模块测试
├── test_image_compressor.py       # 图片压缩模块测试
├── test_crawler.py                # 爬虫模块测试
├── test_schedule_manager.py       # 调度管理模块测试
└── test_pixivision_service.py     # Pixivision服务模块测试
```

## 运行测试

### 运行所有测试

```bash
python -m pytest tests/
```

或使用 unittest:

```bash
python -m unittest discover tests/
```

### 运行单个测试文件

```bash
python -m unittest tests/test_config.py
```

### 运行单个测试类

```bash
python -m unittest tests.test_config.TestConfig
```

### 运行单个测试方法

```bash
python -m unittest tests.test_config.TestConfig.test_get_wechat_config
```

## 测试模块说明

### 1. Config 模块测试 (`test_config.py`)

测试配置管理模块的功能。

| 测试方法 | 测试内容 |
|---------|---------|
| `test_get_wechat_config` | 测试获取微信配置 |
| `test_get_proxy_config` | 测试获取代理配置 |
| `test_get_request_config` | 测试获取请求配置 |
| `test_get_download_config` | 测试获取下载配置 |
| `test_get_download_directory` | 测试获取下载目录 |
| `test_get_schedule_config` | 测试获取调度配置 |
| `test_get_image_compression_config` | 测试获取图片压缩配置 |
| `test_get_draft_config` | 测试获取草稿配置 |
| `test_get_with_default` | 测试获取不存在的配置项返回默认值 |
| `test_config_file_not_exists` | 测试配置文件不存在时使用默认配置 |

### 2. Storage 模块测试 (`test_storage.py`)

测试存储模块的功能，包括 JSON 存储和数据库存储。

#### JsonStorage 测试

| 测试方法 | 测试内容 |
|---------|---------|
| `test_save_illustration` | 测试保存插画 |
| `test_get_illustration_by_id` | 测试根据ID获取插画 |
| `test_get_illustration_by_id_not_found` | 测试获取不存在的插画 |
| `test_get_all_illustrations` | 测试获取所有插画 |
| `test_search_illustrations` | 测试搜索插画 |
| `test_search_illustrations_by_tag` | 测试根据标签搜索插画 |
| `test_delete_illustration` | 测试删除插画 |
| `test_delete_illustration_not_found` | 测试删除不存在的插画 |

#### DatabaseStorage 测试

| 测试方法 | 测试内容 |
|---------|---------|
| `test_save_illustration` | 测试保存插画 |
| `test_get_illustration_by_id` | 测试根据ID获取插画 |
| `test_get_all_illustrations` | 测试获取所有插画 |
| `test_search_illustrations` | 测试搜索插画 |
| `test_delete_illustration` | 测试删除插画 |

#### StorageFactory 测试

| 测试方法 | 测试内容 |
|---------|---------|
| `test_create_json_storage` | 测试创建JSON存储 |
| `test_create_database_storage` | 测试创建数据库存储 |
| `test_create_invalid_storage` | 测试创建无效存储类型 |

### 3. ImageCompressor 模块测试 (`test_image_compressor.py`)

测试图片压缩模块的功能。

| 测试方法 | 测试内容 |
|---------|---------|
| `test_compress_small_image` | 测试压缩小图片（不需要压缩） |
| `test_compress_large_image` | 测试压缩大图片 |
| `test_compress_exceeds_max_size` | 测试压缩超大图片 |
| `test_compress_nonexistent_image` | 测试压缩不存在的图片 |
| `test_compress_with_different_quality` | 测试不同压缩质量 |
| `test_compress_png_image` | 测试压缩PNG图片 |
| `test_get_image_size` | 测试获取图片大小 |
| `test_get_image_dimensions` | 测试获取图片尺寸 |
| `test_should_compress` | 测试判断是否需要压缩 |

### 4. Crawler 模块测试 (`test_crawler.py`)

测试爬虫模块的功能。

#### BaseCrawler 测试

| 测试方法 | 测试内容 |
|---------|---------|
| `test_init` | 测试初始化 |
| `test_init_without_proxy` | 测试不带代理初始化 |
| `test_get_random_url` | 测试获取随机URL |
| `test_get_proxies_disabled` | 测试代理禁用时获取代理配置 |
| `test_get_proxies_enabled` | 测试代理启用时获取代理配置 |
| `test_get_headers` | 测试获取请求头 |
| `test_crawl_success` | 测试爬取成功 |
| `test_parse_not_implemented` | 测试parse方法未实现 |

#### CrawlerFactory 测试

| 测试方法 | 测试内容 |
|---------|---------|
| `test_create_pixivision_crawler` | 测试创建Pixivision爬虫 |
| `test_create_anime_crawler` | 测试创建动漫爬虫 |
| `test_create_image_crawler` | 测试创建图片爬虫 |
| `test_create_invalid_crawler` | 测试创建无效爬虫类型 |

#### PixivisionCrawler 测试

| 测试方法 | 测试内容 |
|---------|---------|
| `test_crawl_one` | 测试爬取单个页面 |
| `test_parse_illustration_id` | 测试解析插画ID |

### 5. ScheduleManager 模块测试 (`test_schedule_manager.py`)

测试调度管理模块的功能。

| 测试方法 | 测试内容 |
|---------|---------|
| `test_init` | 测试初始化 |
| `test_set_weekly_frequency` | 测试设置每周频次 |
| `test_set_time_range` | 测试设置时间范围 |
| `test_get_random_execution_days` | 测试获取随机执行日期 |
| `test_get_random_execution_time` | 测试获取随机执行时间 |
| `test_should_execute_today` | 测试今天是否应该执行 |
| `test_get_next_execution_time` | 测试获取下次执行时间 |
| `test_start` | 测试启动调度器 |
| `test_stop` | 测试停止调度器 |
| `test_execute_task` | 测试执行任务 |
| `test_validate_time_range` | 测试验证时间范围 |
| `test_parse_time_string` | 测试解析时间字符串 |

### 6. PixivisionService 模块测试 (`test_pixivision_service.py`)

测试 Pixivision 服务模块的功能。

| 测试方法 | 测试内容 |
|---------|---------|
| `test_init` | 测试初始化 |
| `test_get_illustration_list` | 测试获取插画列表 |
| `test_get_illustration_detail` | 测试获取插画详情 |
| `test_save_illustration` | 测试保存插画 |
| `test_get_illustration_by_id` | 测试根据ID获取插画 |
| `test_get_illustration_by_id_not_found` | 测试获取不存在的插画 |
| `test_search_illustrations` | 测试搜索插画 |
| `test_get_ranking` | 测试获取排行榜 |
| `test_get_recommendations` | 测试获取推荐榜 |
| `test_download_illustration_images` | 测试下载插画图片 |
| `test_clean_title_for_folder_name` | 测试清理标题作为文件夹名称 |

## 测试覆盖率

### 查看测试覆盖率

安装 coverage 工具：

```bash
pip install coverage
```

运行测试并生成覆盖率报告：

```bash
coverage run -m unittest discover tests/
coverage report
coverage html
```

### 目标覆盖率

| 模块 | 目标覆盖率 |
|------|-----------|
| Config | 90% |
| Storage | 85% |
| ImageCompressor | 85% |
| Crawler | 80% |
| ScheduleManager | 80% |
| PixivisionService | 75% |

## 测试最佳实践

1. **测试隔离**：每个测试方法应该独立运行，不依赖其他测试的结果
2. **使用 Mock**：对于外部依赖（如网络请求、文件系统），使用 Mock 进行模拟
3. **清理资源**：测试完成后清理临时文件和资源
4. **边界测试**：测试边界条件和异常情况
5. **命名规范**：测试方法名应该清晰描述测试内容

## 持续集成

项目使用 GitHub Actions 进行持续集成测试，每次提交代码时会自动运行测试。

配置文件：`.github/workflows/ci-cd.yml`

## 添加新测试

添加新测试时，请遵循以下步骤：

1. 在 `tests` 目录下创建测试文件，命名格式为 `test_*.py`
2. 导入必要的模块和测试基类
3. 创建测试类，继承自 `unittest.TestCase`
4. 实现 `setUp` 和 `tearDown` 方法（如需要）
5. 编写测试方法，方法名以 `test_` 开头
6. 运行测试确保通过
