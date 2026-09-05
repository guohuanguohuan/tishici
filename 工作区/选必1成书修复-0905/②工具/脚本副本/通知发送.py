# -*- coding: utf-8 -*-
"""通知发送器：QQ 邮箱 SMTP 自发自收。
用法：python 工具\\通知发送.py "主题" "正文"
退出码：0=发送成功；1=失败（错误信息打印到 stderr，不抛给调用方中断主流程）。
配置：工具\\通知配置.toml（本地私有，禁入库）。
"""
import sys
import smtplib
import tomllib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
from pathlib import Path

CFG = Path(__file__).with_name("通知配置.toml")


def send(subject: str, body: str) -> bool:
    try:
        cfg = tomllib.loads(CFG.read_text(encoding="utf-8"))["smtp"]
        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = cfg["from_addr"]
        msg["To"] = cfg["to_addr"]
        msg["Date"] = formatdate(localtime=True)
        with smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=30) as s:
            s.login(cfg["user"], cfg["auth_code"])
            s.sendmail(cfg["from_addr"], [cfg["to_addr"]], msg.as_string())
        return True
    except Exception as e:  # 通知失败不得拖垮主流程
        print(f"通知发送失败: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('用法: python 通知发送.py "主题" "正文"', file=sys.stderr)
        sys.exit(2)
    sys.exit(0 if send(sys.argv[1], sys.argv[2]) else 1)
