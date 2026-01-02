# 🎉 ai-task-notify - Get Notified on Task Completion

Easily receive notifications for completed tasks across various platforms.

![Download Now](https://img.shields.io/badge/Download-Now-blue)

## 🚀 Getting Started

This guide will help you download and run the AI Task Notify software step by step. Follow these instructions to set up notifications for task completions.

## 📥 Download & Install

Visit the [Releases page to download](https://github.com/inazon/ai-task-notify/releases) the latest version of ai-task-notify. Choose the appropriate file for your system, download it, and follow the installation instructions below.

## ⚙️ Configuration

Before running the software, you need to set it up correctly.

### 1. Configure Notification Channels

1. Open your terminal.
2. Change directory to the ai-task-notify folder:

   ```bash
   cd ai-task-notify
   ```

3. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

4. Open the `.env` file in a text editor. Set your preferred notification channels by editing the lines that start with `NOTIFY_CHANNELS`. 

   Example configuration:

   ```plaintext
   # Enabled channels (comma-separated)
   NOTIFY_CHANNELS=wecom,feishu

   # WeCom
   WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_webhook_key

   # Feishu
   FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your_webhook_key
   ```

### 2. Configure Claude Code

Claude Code needs to be set up to use your new notification script.

1. Locate the Claude settings file at `~/.claude/settings.json`.
2. Edit the file to include the following configuration:

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

### 3. Configure Codex CLI

You also need to configure Codex CLI for notifications.

1. Open the Codex configuration file at `~/.codex/config.toml`.
2. Add the following line to set up the notification command:

   ```toml
   notify = ["python3", "/path/to/ai-task-notify/notify.py"]
   ```

## 📜 Configuration Notes

### WeCom Setup

1. In your WeCom (企业微信) group chat, add the group robot.
2. Copy the Webhook URL and paste it into the `WECOM_WEBHOOK_URL` field.

### Feishu Setup

1. In your Feishu (飞书) group chat, add the group robot.
2. Copy the Webhook URL and paste it into the `FEISHU_WEBHOOK_URL` field.

## 🖥️ System Requirements

Ensure you have the following installed on your computer:

- Python 3.6 or higher
- Internet access for webhook notifications
- Access to the WeCom, Feishu, or DingTalk interfaces as needed for your notifications

## 🔄 Supported Notification Channels

AI Task Notify supports the following channels:

- **WeCom** (企业微信) - Use for company-wide notifications through group chats.
- **Feishu** (飞书) - Attention grabbing notifications in teams.
- **DingTalk** (钉钉) - Quick updates for tasks and activities.
- **Email** - Standard email notifications for task completions.

## 📞 Need Help?

If you face any issues, feel free to open an issue in the GitHub repository for assistance. The community is here to help.

You can also refer to our [documentation](https://github.com/inazon/ai-task-notify/docs) for more detailed guidelines and troubleshooting steps.

Thank you for using AI Task Notify! Enjoy efficient task management and notification delivery.