# 贡献指南

感谢您对本项目的兴趣！以下是如何为项目做出贡献的指南。

## 目录

- [开发环境设置](#开发环境设置)
- [开发流程](#开发流程)
- [提交PR](#提交PR)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [提交信息规范](#提交信息规范)
- [行为准则](#行为准则)

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/wx_auto_push.git
cd wx_auto_push
```

### 2. 使用 uv 管理依赖

本项目使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理，这是一个现代的 Python 包管理工具。

#### 安装 uv

- **Windows**:
  ```powershell
  iwr https://astral.sh/uv/install.ps1 | iex
  ```

- **macOS/Linux**:
  ```bash
  curl -Ls https://astral.sh/uv/install.sh | sh
  ```

#### 同步依赖

```bash
# 安装所有依赖
uv sync

# 激活虚拟环境
uv run python --version
```

### 3. 配置文件

复制配置文件示例并根据需要修改：

```bash
cp config.development.json.example config.development.json
# 编辑配置文件
```

### 4. 运行测试

确保所有测试通过：

```bash
uv run python -m pytest tests/
```

## 开发流程

1. **创建分支**：从 `main` 分支创建新分支
2. **实现功能**：编写代码实现新功能或修复bug
3. **运行测试**：确保所有测试通过
4. **提交代码**：遵循提交信息规范
5. **创建PR**：提交Pull Request到 `main` 分支

### 分支命名规范

- 功能分支：`feat/feature-name`
- 修复分支：`fix/bug-description`
- 文档分支：`docs/documentation-update`
- 重构分支：`refactor/code-improvement`

## 提交PR

### 1. 准备PR

- 确保代码符合[代码规范](#代码规范)
- 确保所有测试通过
- 确保PR描述清晰完整

### 2. PR描述模板

```markdown
## 描述

简要描述本次PR的目的和变更内容。

## 变更内容

- [ ] 新功能
- [ ] Bug修复
- [ ] 代码重构
- [ ] 文档更新
- [ ] 测试更新

## 相关Issue

链接到相关的Issue（如果有）。

## 测试

描述如何测试本次变更。

## 其他信息

任何其他需要说明的信息。
```

### 3. 代码审查

- PR提交后，维护者会进行代码审查
- 可能需要根据审查意见进行修改
- 审查通过后，PR会被合并

## 代码规范

### 1. 代码风格

- 遵循 PEP 8 代码风格
- 使用 4 个空格进行缩进
- 每行不超过 100 个字符
- 使用蛇形命名法（snake_case）
- 类名使用驼峰命名法（CamelCase）

### 2. 导入顺序

1. 标准库导入
2. 第三方库导入
3. 本地模块导入

### 3. 文档字符串

为函数、类和模块添加适当的文档字符串：

```python
def example_function(param1, param2):
    """
    函数功能描述
    
    参数:
        param1: 参数1描述
        param2: 参数2描述
    
    返回:
        返回值描述
    """
    pass
```

## 测试指南

### 1. 编写测试

- 为新功能添加单元测试
- 确保测试覆盖主要功能和边界情况
- 测试文件位于 `tests/` 目录
- 测试文件命名格式：`test_*.py`

### 2. 运行测试

```bash
# 运行所有测试
uv run python -m pytest tests/

# 运行特定测试文件
uv run python -m pytest tests/test_config.py

# 查看测试覆盖率
uv run python -m coverage run -m pytest tests/
uv run python -m coverage report
```

## 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<类型>[可选的范围]: <描述>

[可选的正文]

[可选的脚注]
```

### 类型

- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响代码功能）
- `refactor`: 代码重构（不新增功能或修复bug）
- `test`: 测试更新
- `chore`: 构建/依赖/工具更新

### 示例

```
feat: 添加Pixivision下载功能

添加了pixivision download命令，支持下载指定插画的图片到本地目录

fix: 修复代理配置问题

修复了代理禁用时的环境变量设置问题

docs: 更新README.md

更新了CLI命令文档
```

## 行为准则

- 尊重所有贡献者
- 接受建设性批评
- 专注于项目的最佳利益
- 保持专业性

## 联系方式

如果有任何问题或建议，可以通过以下方式联系：

- GitHub Issues
- 项目讨论区

感谢您的贡献！