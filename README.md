# AI Task Notify

Claude Code 和 Codex CLI 任务完成通知脚本，支持多种通知渠道。

## 支持的通知渠道

- **企业微信** (WeCom) - 群机器人 Webhook
- **飞书** (Feishu/Lark) - 群机器人 Webhook
- **钉钉** (DingTalk) - 群机器人 Webhook
- **邮件** (Email) - SMTP

## 快速开始

### 1. 配置

```bash
cd ai-task-notify
cp .env.example .env
```

编辑 `.env` 文件，配置你需要的通知渠道：

```bash
# 启用的渠道 (用逗号分隔)
NOTIFY_CHANNELS=wecom,feishu

# 企业微信
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx

# 飞书
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

### 2. 配置 Claude Code

编辑 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/ai-task-notify/notify.py"
          }
        ]
      }
    ]
  }
}
```

### 3. 配置 Codex CLI

编辑 `~/.codex/config.toml`：

```toml
notify = ["python3", "/path/to/ai-task-notify/notify.py"]
```

## 配置说明

### 企业微信

1. 在企业微信群中添加群机器人
2. 复制 Webhook 地址到 `WECOM_WEBHOOK_URL`

### 飞书

1. 在飞书群设置中添加自定义机器人
2. 复制 Webhook 地址到 `FEISHU_WEBHOOK_URL`
3. 如果启用了签名校验，填写 `FEISHU_SECRET`

### 钉钉

1. 在钉钉群设置中添加自定义机器人
2. 复制 Webhook 地址到 `DINGTALK_WEBHOOK_URL`
3. 如果启用了加签，填写 `DINGTALK_SECRET`

### 邮件

```bash
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your@qq.com
SMTP_PASSWORD=授权码
SMTP_USE_SSL=true
EMAIL_FROM=your@qq.com
EMAIL_TO=recipient1@example.com,recipient2@example.com
```

## 测试

```bash
# 测试脚本 (模拟 Codex 调用)
python3 notify.py '{"type": "agent-turn-complete", "test": true}'

# 测试脚本 (模拟 Claude Code 调用)
echo '{"session_id": "test", "cwd": "/tmp"}' | python3 notify.py
```

## 文件结构

```
ai-task-notify/
├── .env.example    # 配置模板
├── .env            # 实际配置 (需要自己创建)
├── notify.py       # 通知脚本
└── README.md       # 说明文档
```

## 注意事项

- `.env` 文件包含敏感信息，请勿提交到版本控制
- 脚本使用 Python 标准库，无需安装额外依赖
- 未配置或未启用的渠道会自动跳过
