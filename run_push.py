
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

def send_feishu(url, title, content):
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
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200 and resp.json().get("code") == 0:
            print("[飞书] 成功")
            return True
        print("[飞书] 失败")
    except Exception as e:
        print(f"[飞书] 失败: {e}")
    return False

def send_email(sender, pwd, receivers, subject, content):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(receivers)
        html = f'<html><body style="font-family:Microsoft YaHei;"><div>{content.replace(chr(10), "<br>")}</div></body></html>'
        msg.attach(MIMEText(content, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP_SSL("smtp.qq.com", 465) as s:
            s.login(sender, pwd)
            s.sendmail(sender, receivers, msg.as_string())
        print("[邮件] 成功")
    except Exception as e:
        print(f"[邮件] 失败: {e}")

def push_report(title, content):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    full_title = f"[A股分析] {title} - {now}"
    send_feishu("https://open.feishu.cn/open-apis/bot/v2/hook/47549031-08ab-4b58-9c96-f8d5d74e19ae", full_title, content)
    send_email("2770754682@qq.com", "hlcsedrvznxmdeee", ["2770754682@qq.com"], full_title, content)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        sys.exit(1)
    title = sys.argv[1]
    date_str = datetime.now().strftime('%Y%m%d')
    filepath = Path("/workspace/logs") / f"{title.replace(' ', '_')}_{date_str}.md"
    if filepath.exists():
        print(f"[推送文件] {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        push_report(title, content)
    else:
        print(f"[错误] 文件不存在: {filepath}")

