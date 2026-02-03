# HN Daily Summary 📰

每天自动爬取 Hacker News Top 30 热门文章，使用 DeepSeek AI 生成中文摘要，并通过邮件发送。

## 功能特性

- 🔥 获取 HN 每日 Top 30 热门文章
- 🤖 使用 DeepSeek AI 智能分类和总结
- 🔗 包含原文链接和 HN 讨论链接，方便阅读
- 📧 自动发送邮件（支持 HTML 格式，多收件人）
- ⏰ GitHub Actions 定时任务（每天北京时间 16:00）
- 📁 支持本地文件输出（用于测试或存档）

## 快速开始

### 本地运行

1. **安装依赖**

```bash
cd /Users/lion/Projects/hn-daily-summary
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

3. **运行**

```bash
# 完整运行（发送邮件）
python3 main.py

# 仅保存文件（测试用）
OUTPUT_MODE=file python3 main.py
```

4. **国内网络代理**（如果 Gmail 被墙）

```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 all_proxy=socks5://127.0.0.1:7890
python3 main.py
```

### GitHub Actions 自动运行

1. **创建 GitHub 仓库**

```bash
cd /Users/lion/Projects/hn-daily-summary
git init
git add .
git commit -m "feat: HN daily summary with DeepSeek AI"

# 在 GitHub 上创建仓库后
git remote add origin https://github.com/YOUR_USERNAME/hn-daily-summary.git
git push -u origin main
```

2. **添加 Secrets**

在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加：

| Secret Name        | Description                       |
| ------------------ | --------------------------------- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key                  |
| `SMTP_SERVER`      | SMTP 服务器 (如 `smtp.gmail.com`) |
| `SMTP_PORT`        | SMTP 端口 (如 `587`)              |
| `SMTP_USERNAME`    | 发件邮箱地址                      |
| `SMTP_PASSWORD`    | 邮箱密码或应用专用密码            |
| `EMAIL_TO`         | 收件邮箱地址（多个用逗号分隔）    |

3. **手动触发测试**

仓库 Actions 页面 → HN Daily Summary → Run workflow

## 邮件配置说明

### Gmail

1. 开启两步验证
2. 生成应用专用密码：Google Account → Security → App passwords
3. 使用应用专用密码作为 `SMTP_PASSWORD`

### QQ 邮箱

- SMTP_SERVER: `smtp.qq.com`
- SMTP_PORT: `587`
- SMTP_PASSWORD: 需要开启 SMTP 服务并获取授权码

### 163 邮箱

- SMTP_SERVER: `smtp.163.com`
- SMTP_PORT: `25` 或 `465`
- SMTP_PASSWORD: 需要开启 SMTP 服务并获取授权码

## 配置选项

| 环境变量           | 默认值  | 说明                                |
| ------------------ | ------- | ----------------------------------- |
| `STORIES_COUNT`    | `30`    | 获取的文章数量                      |
| `SUMMARY_LANGUAGE` | `zh`    | 总结语言 (`zh` 中文, `en` 英文)     |
| `OUTPUT_MODE`      | `email` | 输出模式：`email` / `file` / `both` |

## 项目结构

```
hn-daily-summary/
├── src/
│   ├── hn_fetcher.py    # HN API 爬取
│   ├── summarizer.py    # DeepSeek AI 总结
│   └── emailer.py       # 邮件发送
├── main.py              # 主入口
├── ARCHITECTURE.md      # 技术架构文档
└── AGENTS.md            # AI 助手指南
```

## 文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 技术架构和实现细节
- [AGENTS.md](./AGENTS.md) - AI 助手维护指南

## License

MIT
