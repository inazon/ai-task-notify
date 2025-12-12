#!/usr/bin/env python3
"""
AI Task Notify - Claude Code / Codex 任务完成通知脚本

支持的通知渠道:
- 企业微信 (WeCom)
- 飞书 (Feishu)
- 钉钉 (DingTalk)
- 邮件 (Email)

使用方式:
1. Claude Code (Stop hook): 通过 stdin 接收 JSON
2. Codex CLI (notify): 通过命令行参数接收 JSON
"""

import json
import sys
import os
import hmac
import hashlib
import base64
import time
import urllib.request
import urllib.error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
from typing import Optional


def load_env(env_path: Optional[str] = None) -> dict:
    """加载 .env 文件"""
    env = {}

    if env_path is None:
        env_path = Path(__file__).parent / ".env"
    else:
        env_path = Path(env_path)

    if not env_path.exists():
        return env

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip()

    return env


def get_config(env: dict, key: str, default: str = "") -> str:
    """获取配置，优先使用环境变量"""
    return os.environ.get(key, env.get(key, default))


def get_enabled_channels(env: dict) -> list:
    """获取启用的通知渠道列表"""
    channels_str = get_config(env, "NOTIFY_CHANNELS", "")
    if not channels_str:
        return []
    return [c.strip().lower() for c in channels_str.split(",") if c.strip()]


def http_post(url: str, data: dict, headers: Optional[dict] = None) -> tuple:
    """发送 HTTP POST 请求"""
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"

    json_data = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=json_data, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")
    except Exception as e:
        return 0, str(e)


# ============ 企业微信 ============

def send_wecom(env: dict, title: str, content: str) -> bool:
    """发送企业微信通知"""
    webhook_url = get_config(env, "WECOM_WEBHOOK_URL")
    if not webhook_url:
        return False

    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": f"### {title}\n{content}"
        }
    }

    status, resp = http_post(webhook_url, data)
    if status == 200:
        result = json.loads(resp)
        return result.get("errcode") == 0
    return False


# ============ 飞书 ============

def gen_feishu_sign(secret: str, timestamp: str) -> str:
    """生成飞书签名"""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def send_feishu(env: dict, title: str, content: str) -> bool:
    """发送飞书通知"""
    webhook_url = get_config(env, "FEISHU_WEBHOOK_URL")
    if not webhook_url:
        return False

    secret = get_config(env, "FEISHU_SECRET")

    data = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "markdown",
                    "content": content
                }
            ]
        }
    }

    if secret:
        timestamp = str(int(time.time()))
        sign = gen_feishu_sign(secret, timestamp)
        data["timestamp"] = timestamp
        data["sign"] = sign

    status, resp = http_post(webhook_url, data)
    if status == 200:
        result = json.loads(resp)
        return result.get("code") == 0 or result.get("StatusCode") == 0
    return False


# ============ 钉钉 ============

def gen_dingtalk_sign(secret: str, timestamp: str) -> str:
    """生成钉钉签名"""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode("utf-8"),
        string_to_sign.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    return urllib.parse.quote_plus(base64.b64encode(hmac_code).decode("utf-8"))


def send_dingtalk(env: dict, title: str, content: str) -> bool:
    """发送钉钉通知"""
    webhook_url = get_config(env, "DINGTALK_WEBHOOK_URL")
    if not webhook_url:
        return False

    secret = get_config(env, "DINGTALK_SECRET")

    if secret:
        timestamp = str(int(time.time() * 1000))
        sign = gen_dingtalk_sign(secret, timestamp)
        separator = "&" if "?" in webhook_url else "?"
        webhook_url = f"{webhook_url}{separator}timestamp={timestamp}&sign={sign}"

    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": f"### {title}\n{content}"
        }
    }

    status, resp = http_post(webhook_url, data)
    if status == 200:
        result = json.loads(resp)
        return result.get("errcode") == 0
    return False


# ============ 邮件 ============

def send_email(env: dict, title: str, content: str) -> bool:
    """发送邮件通知"""
    smtp_host = get_config(env, "SMTP_HOST")
    smtp_user = get_config(env, "SMTP_USER")
    smtp_password = get_config(env, "SMTP_PASSWORD")
    email_from = get_config(env, "EMAIL_FROM")
    email_to = get_config(env, "EMAIL_TO")

    if not all([smtp_host, smtp_user, smtp_password, email_from, email_to]):
        return False

    smtp_port = int(get_config(env, "SMTP_PORT", "465"))
    use_ssl = get_config(env, "SMTP_USE_SSL", "true").lower() == "true"

    recipients = [e.strip() for e in email_to.split(",") if e.strip()]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = title
    msg["From"] = email_from
    msg["To"] = ", ".join(recipients)

    html_content = f"""
    <html>
    <body>
        <h2>{title}</h2>
        <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
{content}
        </pre>
    </body>
    </html>
    """

    msg.attach(MIMEText(content, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.starttls()

        server.login(smtp_user, smtp_password)
        server.sendmail(email_from, recipients, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}", file=sys.stderr)
        return False


# ============ 通知调度 ============

CHANNEL_HANDLERS = {
    "wecom": send_wecom,
    "feishu": send_feishu,
    "dingtalk": send_dingtalk,
    "email": send_email,
}


def send_notification(env: dict, title: str, content: str) -> dict:
    """发送通知到所有启用的渠道"""
    channels = get_enabled_channels(env)
    results = {}

    for channel in channels:
        handler = CHANNEL_HANDLERS.get(channel)
        if handler:
            try:
                results[channel] = handler(env, title, content)
            except Exception as e:
                print(f"Channel {channel} error: {e}", file=sys.stderr)
                results[channel] = False

    return results


def format_message(source: str, event_type: str, data: dict) -> tuple:
    """格式化通知消息，返回 (title, content)"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if source == "claude-code":
        transcript = data.get("transcript", [])
        last_message = ""
        if transcript:
            for item in reversed(transcript):
                if item.get("type") == "assistant":
                    msg = item.get("message", {})
                    if isinstance(msg, dict):
                        content_list = msg.get("content", [])
                        for c in content_list:
                            if isinstance(c, dict) and c.get("type") == "text":
                                last_message = c.get("text", "")[:500]
                                break
                    break

        title = "🤖 Claude Code 任务完成"
        content = f"""**时间**: {now}
**工作目录**: {data.get('cwd', 'N/A')}
**会话ID**: {data.get('session_id', 'N/A')[:8]}...

**最后消息**:
{last_message or '(无内容)'}"""

    elif source == "codex":
        title = "🤖 Codex 任务完成"
        content = f"""**时间**: {now}
**事件类型**: {event_type}

**原始数据**:
```json
{json.dumps(data, ensure_ascii=False, indent=2)[:1000]}
```"""

    else:
        title = "🤖 AI 任务完成"
        content = f"""**时间**: {now}
**来源**: {source}

**数据**:
```json
{json.dumps(data, ensure_ascii=False, indent=2)[:1000]}
```"""

    return title, content


def parse_input() -> tuple:
    """
    解析输入，返回 (source, event_type, data)

    Claude Code: 通过 stdin 传入 JSON
    Codex: 通过命令行参数传入 JSON
    """
    data = {}
    source = "unknown"
    event_type = ""

    # 尝试从命令行参数读取 (Codex 方式)
    if len(sys.argv) > 1:
        try:
            data = json.loads(sys.argv[1])
            source = "codex"
            event_type = data.get("type", "")

            # Codex 只处理 agent-turn-complete 事件
            if event_type != "agent-turn-complete":
                return source, event_type, None

        except json.JSONDecodeError:
            pass

    # 尝试从 stdin 读取 (Claude Code 方式)
    if not data and not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                data = json.loads(stdin_data)
                source = "claude-code"
                event_type = "stop"
        except json.JSONDecodeError:
            pass

    return source, event_type, data


def main() -> int:
    # 加载配置
    env = load_env()

    # 检查是否有启用的渠道
    channels = get_enabled_channels(env)
    if not channels:
        print("No notification channels enabled", file=sys.stderr)
        return 0

    # 解析输入
    source, event_type, data = parse_input()

    if data is None:
        # 事件类型不需要处理
        return 0

    if not data:
        print("No valid input data", file=sys.stderr)
        return 1

    # 格式化消息
    title, content = format_message(source, event_type, data)

    # 发送通知
    results = send_notification(env, title, content)

    # 输出结果
    success_count = sum(1 for v in results.values() if v)
    print(f"Notifications sent: {success_count}/{len(results)}")
    for channel, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {channel}")

    return 0 if success_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
