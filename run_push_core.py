#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# RUN_PUSH_V2
import smtplib
import socket
import subprocess
import sys
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

FEISHU_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/47549031-08ab-4b58-9c96-f8d5d74e19ae"
EMAIL_SENDER = "2770754682@qq.com"
EMAIL_PWD = "hlcsedrvznxmdeee"
EMAIL_RECEIVERS = ["2770754682@qq.com"]
FEISHU_CHUNK_SIZE = 3800

def _ensure_requests():
    try:
        import requests
        return
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "requests"])
        print("[依赖] requests 安装完成")

_ensure_requests()

def send_feishu_card(url, title, content):
    import requests
    try:
        payload = {
            "msg_type": "interactive",
            "card": {
                "header": {"title": {"tag": "plain_text", "content": title}, "template": "blue"},
                "elements": [{"tag": "markdown", "content": content}]
            }
        }
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                print(f"[飞书] 成功: {title}")
                return True
            print(f"[飞书] 失败: {data}")
        else:
            print(f"[飞书] HTTP错误: {resp.status_code}")
    except Exception as e:
        print(f"[飞书] 异常: {e}")
    return False

def send_feishu_chunked(url, title, content):
    if len(content) <= FEISHU_CHUNK_SIZE:
        return send_feishu_card(url, title, content)
    chunks = []
    remaining = content
    while remaining:
        if len(remaining) <= FEISHU_CHUNK_SIZE:
            chunks.append(remaining)
            break
        split_pos = remaining.rfind('\n', 0, FEISHU_CHUNK_SIZE)
        if split_pos == -1:
            split_pos = FEISHU_CHUNK_SIZE
        chunks.append(remaining[:split_pos])
        remaining = remaining[split_pos:].lstrip('\n')
    total = len(chunks)
    success_count = 0
    for i, chunk in enumerate(chunks, 1):
        part_title = f"{title} ({i}/{total})"
        if send_feishu_card(url, part_title, chunk):
            success_count += 1
    print(f"[飞书] 分段推送完成: {success_count}/{total} 成功")
    return success_count == total

def check_smtp_reachable(host="smtp.qq.com", port=465, timeout=5):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        sock.close()
        return True
    except (socket.timeout, OSError, ConnectionRefusedError):
        return False

def send_email(sender, pwd, receivers, subject, content):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(receivers)
        html = '<html><body style="font-family:Microsoft YaHei;"><div style="white-space:pre-wrap;">' + content + '</div></body></html>'
        msg.attach(MIMEText(content, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        with smtplib.SMTP_SSL(host="smtp.qq.com", port=465, timeout=15) as s:
            s.login(sender, pwd)
            s.sendmail(sender, receivers, msg.as_string())
        print("[邮件] 成功")
        return True
    except Exception as e:
        print(f"[邮件] 错误: {e}")
        return False

def save_email_fallback(subject, content):
    fallback_dir = Path("/workspace/logs/email_fallback")
    fallback_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = subject.replace(" ", "_").replace("/", "_").replace(":", "_")
    eml_path = fallback_dir / f"{ts}_{safe_name}.eml"
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = ", ".join(EMAIL_RECEIVERS)
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0800")
    msg.attach(MIMEText(content, "plain", "utf-8"))
    with open(eml_path, "w", encoding="utf-8") as f:
        f.write(msg.as_string())
    print(f"[邮件] 已保存待发: {eml_path}")
    return eml_path

def push_report(title, content):
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    full_title = f"[A股分析] {title} - {now}"
    print("=" * 50)
    print(f"推送任务: {full_title}")
    print(f"内容长度: {len(content)} 字符")
    print("=" * 50)
    print("\n[1/2] 飞书推送...")
    feishu_ok = send_feishu_chunked(FEISHU_URL, full_title, content)
    print("\n[2/2] 邮件推送...")
    if check_smtp_reachable():
        email_ok = send_email(EMAIL_SENDER, EMAIL_PWD, EMAIL_RECEIVERS, full_title, content)
    else:
        print("[邮件] SMTP端口不可达，降级为本地存档")
        save_email_fallback(full_title, content)
        email_ok = False
    print("\n" + "=" * 50)
    print(f"推送结果汇总:")
    print(f"  飞书: {'成功' if feishu_ok else '失败'}")
    print(f"  邮件: {'成功' if email_ok else '已降级存档'}")
    print("=" * 50)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 run_push_core.py <报告标题>")
        sys.exit(1)
    title = sys.argv[1]
    date_str = datetime.now().strftime('%Y%m%d')
    filepath = Path("/workspace/logs") / f"{title.replace(' ', '_')}_{date_str}.md"
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        push_report(title, content)
    else:
        print(f"文件不存在: {filepath}")
        sys.exit(1)

if __name__ == "__main__":
    main()
