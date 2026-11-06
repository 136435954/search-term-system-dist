# -*- coding: utf-8 -*-
"""把 README.md / config.json / 使用说明.md 同步到 Gitee 镜像仓，并逐文件校验是否真的落地。

背景：Gitee 的 contents 读接口有缓存，旧版 workflow 只凭 PUT 返回 200 就判定成功，
曾出现 run 绿勾但镜像里仍是旧内容的情况。这里改为「写入后用最新提交 sha 精确回读比对」，
不一致就重试，最终仍不一致则让任务失败，避免静默漏同步。
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

TOKEN = os.environ["GITEE_TOKEN"]
OWNER = "yan-tiantian"
REPO = "search-term-system-dist"
FILES = ["README.md", "config.json", "使用说明.md"]
API = "https://gitee.com/api/v5/repos/%s/%s" % (OWNER, REPO)
TIMEOUT = 90
RETRIES = 4


def call(path, method="GET", payload=None):
    """调用 Gitee OpenAPI，返回 (状态码, 解析后的 JSON 或 None)。"""
    url = API + path
    data = urllib.parse.urlencode(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"User-Agent": "sync", "Content-Type": "application/x-www-form-urlencoded"})
    last = None
    for attempt in range(1, RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            last = e.code
            if e.code in (409, 422, 429, 500, 502, 503, 504) and attempt < RETRIES:
                time.sleep(2 * attempt)
                continue
            return e.code, None
        except Exception as e:  # noqa: BLE001  网络抖动统一重试
            last = repr(e)[:120]
            if attempt < RETRIES:
                time.sleep(2 * attempt)
                continue
            return "ERR", None
    return last, None


def remote_sha(name):
    st, info = call("/contents/" + urllib.parse.quote(name, safe=""))
    if st == 200 and isinstance(info, dict):
        return info.get("sha")
    return None


def read_at(name, ref):
    """按指定提交读文件内容，绕开分支级别的缓存。"""
    st, info = call("/contents/%s?ref=%s" % (urllib.parse.quote(name, safe=""),
                                             urllib.parse.quote(ref)))
    if st == 200 and isinstance(info, dict) and info.get("content"):
        return info["content"].replace("\n", "")
    return None


def head_commit():
    st, info = call("/commits?per_page=1")
    if st == 200 and isinstance(info, list) and info:
        return info[0]["sha"]
    return None


failed = []
for name in FILES:
    if not os.path.exists(name):
        print("skip (not in repo):", name)
        continue
    with open(name, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    done = False
    for attempt in range(1, RETRIES + 1):
        sha = remote_sha(name)
        payload = {"access_token": TOKEN, "content": content, "message": "sync " + name}
        path = "/contents/" + urllib.parse.quote(name, safe="")
        if sha:
            payload["sha"] = sha
            st, _ = call(path, "PUT", payload)
        else:
            st, _ = call(path, "POST", payload)

        if st in (200, 201):
            commit = head_commit()
            got = read_at(name, commit) if commit else None
            if got == content:
                print("synced + verified", name, commit[:8])
                done = True
                break
            print("put ok, verify mismatch", name, "attempt", attempt)
        else:
            print("put fail", name, st, "attempt", attempt)
        time.sleep(3)

    if not done:
        failed.append(name)

if failed:
    print("SYNC FAILED:", failed)
    sys.exit(1)
print("ALL SYNCED")
