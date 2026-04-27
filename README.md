# mteam-search

M-Team（馒头）PT 站影视资源搜索与下载 CLI 工具。

通过 API Key 鉴权，支持关键词搜索种子、查看详情、下载 `.torrent` 文件。

## 目录结构

```
├── SKILL.md                        # Skill 定义（触发词、工作流）
├── .claude/skills/mteam-search.md  # Claude Code skill
├── pyproject.toml                  # 包元数据
├── setup.py
├── .env.example                    # 环境变量模板
├── .env                            # 实际配置（gitignore）
├── requirements.txt
└── scripts/
    ├── __init__.py                 # 包导出 (MTeamAPI, format_size)
    ├── __main__.py                 # python -m scripts
    ├── api.py                      # API 客户端
    └── cli.py                      # CLI 入口
```

## 快速开始

### 1. 获取 API Key

登录 [M-Team](https://kp.m-team.cc) → **控制台** → **實驗室** → **存取令牌**，复制 token。

### 2. 配置

```bash
cp .env.example .env
```

编辑 `.env`：

```
MTEAM_API_KEY=你的API-Key
```

### 3. 安装

```bash
pip install -e .
```

安装后 `mteam-search` 命令全局可用：

```bash
mteam-search search "21世纪" --mode tvshow
```

### 4. 搜索

```
🔍 「21世纪」(mode=tvshow)
共 23 条  |  第 1 页，显示 20 条
--------------------------------------------------
[1173041] Perfect Crown 2026 S01E05-E06 1080p Disney+ WEB-DL H.264 AAC 2Audios-QHstudIo
  大小: 4.60 GB  |  做种: 222  |  下载中: 9
  标签: 中字  |  折扣: PERCENT_50
  IMDB: 8.2  |  豆瓣: -
```

## 使用方式

### CLI

```bash
# 搜索种子
mteam-search search <关键词> [--mode tvshow|movie|anime|music|all] [--page 1] [--pagesize 20]

# 查看详情
mteam-search detail <torrent_id>

# 下载种子
mteam-search download <torrent_id> [--dir ./seed]

# 输出原始 JSON（用于程序处理）
mteam-search search "关键词" --json
```

#### 不安装直接运行

```bash
# 直接执行
python scripts/cli.py search "21世纪" --mode tvshow

# 或作为模块
python -m scripts search "21世纪" --mode tvshow
```

### Python API

```python
from scripts import MTeamAPI

api = MTeamAPI()  # 自动读取 .env 中的 MTEAM_API_KEY

# 搜索 → 返回 (data, error)
result, err = api.search("21世纪", mode="tvshow", page_number=1, page_size=20)
for item in result["items"]:
    print(item["id"], item.get("name"))

# 详情
detail, err = api.detail("1173041")
print(detail.get("smallDescr"))

# 下载
path, err = api.download("1173041", download_dir="./seed")
```

所有 API 方法返回 `(data, error)` 元组：成功时 `error is None`，失败时 `data is None`。

## 搜索模式 (`--mode`)

| 值 | 含义 |
|----|------|
| `normal` | 综合搜索（默认） |
| `movie` | 电影 |
| `tvshow` | 电视剧 |
| `anime` | 动漫 |
| `music` | 音乐 |
| `adult` | 成人 |
| `all` | 全部 |

## `MTeamAPI` 参数

| 参数 | 环境变量 | 默认值 | 必填 |
|------|----------|--------|------|
| `api_key` | `MTEAM_API_KEY` | — | 是 |
| `base_url` | `MTEAM_API_BASE` | `https://api.m-team.cc/api` | 否 |

## 配置

| 环境变量 | 说明 |
|----------|------|
| `MTEAM_API_KEY` | API Key，从控制台 → 實驗室 → 存取令牌获取 |
| `MTEAM_API_BASE` | API 基础地址（默认 `https://api.m-team.cc/api`） |

项目支持 `.env` 文件自动加载（通过 python-dotenv），也支持系统环境变量。
