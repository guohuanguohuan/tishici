# -*- coding: utf-8 -*-
"""收信核查：列出 QQ 邮箱收件箱最近 N 封（主题/发件人/日期）。
用法：python 工具\\收信核查.py [N]（默认 5）
凭证同 工具\\通知配置.toml（imap.qq.com:993，授权码与 SMTP 通用）。
"""
import sys
import imaplib
import tomllib
import email
from email.header import decode_header, make_header
from pathlib import Path

CFG = Path(__file__).with_name("通知配置.toml")


def main(n: int = 5) -> int:
    cfg = tomllib.loads(CFG.read_text(encoding="utf-8"))["smtp"]
    with imaplib.IMAP4_SSL("imap.qq.com", 993, timeout=30) as m:
        m.login(cfg["user"], cfg["auth_code"])
        m.select("INBOX")
        _, data = m.search(None, "ALL")
        ids = data[0].split()
        if not ids:
            print("收件箱为空")
            return 0
        for i in ids[-n:]:
            _, d = m.fetch(i, "(BODY.PEEK[HEADER])")
            msg = email.message_from_bytes(d[0][1])
            subj = str(make_header(decode_header(msg.get("Subject", ""))))
            frm = str(make_header(decode_header(msg.get("From", ""))))
            date = msg.get("Date", "")
            print(f"- {date}｜{frm}｜{subj}")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1])) if len(sys.argv) > 1 else main())
