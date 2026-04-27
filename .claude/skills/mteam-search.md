---
name: mteam-search
description: >
  M-Team (馒头) PT 站影视资源搜索 — 搜索 torrent、查看详情、下载种子文件。
  触发词: 搜片, 找资源, 下载种子, torrent, mteam, 馒头, 搜索影视,
  PT下载, 电影搜索, 电视剧搜索, 动漫搜索,
  或任何 "[关键词] 资源/种子" 格式的输入。
---

# mteam-search — M-Team Torrent Search Skill

Search and download torrents from M-Team (馒头) private tracker via API Key.

## Quick Start

1. **获取 API Key**：登录 M-Team → 右上角 **控制台** → **實驗室** → **存取令牌**，复制 token。
2. 在项目根目录复制 `.env.example` 为 `.env`，填入 `MTEAM_API_KEY=<你的token>`。
3. 安装并运行：
   ```bash
   pip install -e .
   mteam-search search "关键词" --mode tvshow
   ```

## Workflow

1. 用户提出搜索需求时，运行 `mteam-search search <关键词> [--mode <模式>] [--page <页码>] [--pagesize <条数>]`。
2. 用户需要查看某个种子的详细信息时，运行 `mteam-search detail <torrent_id>`。
3. 用户需要下载 .torrent 文件时，运行 `mteam-search download <torrent_id> [--dir <目录>]`。
4. 将搜索结果以清晰可读的方式呈现给用户，包含种子 ID、名称、大小、做种/下载数、标签、IMDB/豆瓣评分。

## Search Modes

| 模式 | 含义 |
|------|------|
| `normal` | 综合搜索（默认） |
| `tvshow` | 电视剧 |
| `movie` | 电影 |
| `anime` | 动漫 |
| `music` | 音乐 |
| `adult` | 成人 |
| `all` | 全部类别 |

## Notes

- 本 skill 是脚本驱动的 CLI 工具，不依赖 MCP server。
- 需要 `MTEAM_API_KEY` 环境变量或项目根目录 `.env` 文件。API Key 获取路径：M-Team 网站 → **控制台** → **實驗室** → **存取令牌**。
- 也支持 `MTEAM_API_BASE` 环境变量自定义 API 地址（默认 `https://api.m-team.cc/api`）。
- 搜索结果中 `[数字]` 为种子 ID，可用于 detail/download 命令。
- 如果用户提示 API Key 无效或未配置，引导其前往 M-Team 控制台自助获取。
