#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级通知推送脚本 - 飞书 + 邮件
仅依赖 requests（Python 标准库外的唯一依赖）
用于 SOLO 定时任务推送分析结果
"""

import json
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path


def load_env():
    """从 .env 文件加载环境变量"""
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        return
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            if key and value:
                os.environ.setdefault(key, value)


def send_feishu(webhook_url: str, title: str, content: str) -> bool:
    """发送飞书消息"""
    try:
        import requests
        payload = {
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
                        "content": content[:4000]
                    }
                ]
            }
        }
        resp = requests.post(
            webhook_url,
            json=payload,
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0 or data.get("StatusCode") == 0:
                print(f"[飞书] 推送成功: {title}")
                return True
            else:
                print(f"[飞书] 推送返回异常: {data}")
        else:
            print(f"[飞书] HTTP 错误: {resp.status_code}")
    except Exception as e:
        print(f"[飞书] 推送失败: {e}")
    return False


def send_email(
    sender: str,
    password: str,
    receivers: list,
    subject: str,
    content: str,
    smtp_server: str = "smtp.qq.com",
    smtp_port: int = 465
) -> bool:
    """发送邮件"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(receivers)

        html_content = content.replace("\n", "<br>")
        html_content = f"""
        <html>
        <body style="font-family: 'Microsoft YaHei', sans-serif; line-height: 1.8; padding: 20px;">
        <div style="max-width: 800px; margin: 0 auto;">
        {html_content}
        </div>
        </body>
        </html>
        """

        text_part = MIMEText(content, "plain", "utf-8")
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(text_part)
        msg.attach(html_part)

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender, password)
            server.sendmail(sender, receivers, msg.as_string())

        print(f"[邮件] 推送成功: {subject}")
        return True
    except Exception as e:
        print(f"[邮件] 推送失败: {e}")
    return False


def push_report(title: str, content: str):
    """推送报告到飞书和邮件"""
    load_env()

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    full_title = f"[A股分析] {title} - {now}"

    # 飞书推送
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "")
    if webhook_url:
        send_feishu(webhook_url, full_title, content)
    else:
        print("[飞书] 未配置 FEISHU_WEBHOOK_URL，跳过飞书推送")

    # 邮件推送
    sender = os.getenv("EMAIL_SENDER", "")
    password = os.getenv("EMAIL_PASSWORD", "")
    receivers_str = os.getenv("EMAIL_RECEIVERS", "")
    if sender and password and receivers_str:
        receivers = [r.strip() for r in receivers_str.split(",") if r.strip()]
        send_email(sender, password, receivers, full_title, content)
    else:
        print("[邮件] 未配置邮件信息，跳过邮件推送")

    # 保存到文件
    try:
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        date_str = datetime.now().strftime('%Y%m%d')
        filename = f"{title.replace(' ', '_')}_{date_str}.md"
        filepath = log_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {full_title}\n\n{content}")
        print(f"[文件] 报告已保存: {filepath}")
    except Exception as e:
        print(f"[文件] 保存失败: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python notify_lite.py <标题> <内容文件>")
        print("  或: echo '内容' | python notify_lite.py <标题> -")
        sys.exit(1)

    title = sys.argv[1]
    content_source = sys.argv[2]

    if content_source == "-":
        content = sys.stdin.read()
    else:
        with open(content_source, 'r', encoding='utf-8') as f:
            content = f.read()

    push_report(title, content)
