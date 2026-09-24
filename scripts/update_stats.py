#!/usr/bin/env python3
"""Refresh quantified project / OSS stats inside README.md markers."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

OWNER = "Lossalt"
README = Path(__file__).resolve().parents[1] / "README.md"

OWN_REPOS = [
    ("article-image", "可搬迁图床：正文写名字，迁站只改 `base_url`"),
    ("random-img", "随机壁纸接口：图池可拆，302 / 直出 / JSON"),
    ("iptv-gen", "IPTV M3U 生成：采集、测活、排序、导出"),
]

MYRIAD_PRS = ["Myriad-You/Myriad#585"]
SAKURAIRO_PRS = [
    "mirai-mamori/Sakurairo#1429",
    "mirai-mamori/Sakurairo#1430",
    "mirai-mamori/Sakurairo#1431",
]


def gh_get(path: str) -> object:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    req = urllib.request.Request(
        "https://api.github.com/" + path.lstrip("/"),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "lossalt-profile-stats",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            return json.loads(body or b"null")
    except urllib.error.HTTPError as exc:
        if exc.code == 202:
            return None
        raise


def repo_stats(repo: str) -> dict[str, int]:
    data = gh_get(f"repos/{repo}/stats/contributors")
    if not isinstance(data, list):
        return {"commits": 0, "add": 0, "del": 0, "files": 0}

    commits = add = delete = 0
    for person in data:
        if person.get("author", {}).get("login") != OWNER:
            continue
        commits += int(person.get("total", 0))
        for week in person.get("weeks", []) or []:
            add += int(week.get("a", 0) or 0)
            delete += int(week.get("d", 0) or 0)

    tree = gh_get(f"repos/{repo}/git/trees/HEAD?recursive=1")
    files = 0
    if isinstance(tree, dict):
        files = sum(1 for item in tree.get("tree", []) if item.get("type") == "blob")
    return {"commits": commits, "add": add, "del": delete, "files": files}


def pr_stats(full_name: str) -> dict[str, int]:
    repo_full, number = full_name.split("#")
    pr = gh_get(f"repos/{repo_full}/pulls/{number}")
    if not isinstance(pr, dict):
        return {"add": 0, "del": 0, "files": 0}
    return {
        "add": int(pr.get("additions") or 0),
        "del": int(pr.get("deletions") or 0),
        "files": int(pr.get("changed_files") or 0),
    }


def pr_count(repo: str) -> int:
    data = gh_get(f"search/issues?q=repo:{repo}+author:{OWNER}+type:pr")
    if isinstance(data, dict):
        return int(data.get("total_count") or 0)
    return 0


def fmt_num(n: int) -> str:
    return f"{n:,}" if abs(n) >= 1000 else str(n)


def replace_block(text: str, name: str, payload: str) -> str:
    pattern = rf"(<!-- stats:{name}:start -->)(.*?)(<!-- stats:{name}:end -->)"
    new = f"\\1\n{payload.rstrip()}\n\\3"
    updated, count = re.subn(pattern, new, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"marker stats:{name} not found")
    return updated


def main() -> None:
    project_rows = []
    for repo, desc in OWN_REPOS:
        st = repo_stats(f"{OWNER}/{repo}")
        project_rows.append(
            f"| [**{repo}**](https://github.com/{OWNER}/{repo}) | {desc} "
            f"| **{st['commits']}** commits · `+{fmt_num(st['add'])}` `−{fmt_num(st['del'])}` |"
        )
    projects = (
        "| 项目 | 简介 | 规模 |\n"
        "|---|---|---|\n"
        + "\n".join(project_rows)
    )

    my_add = my_del = my_files = 0
    for ref in MYRIAD_PRS:
        st = pr_stats(ref)
        my_add += st["add"]
        my_del += st["del"]
        my_files += st["files"]

    sak_add = sak_del = sak_files = 0
    sak_n = 0
    for ref in SAKURAIRO_PRS:
        st = pr_stats(ref)
        if st["files"]:
            sak_n += 1
        sak_add += st["add"]
        sak_del += st["del"]
        sak_files += st["files"]

    oss = (
        "| 项目 | 我做了什么 | 量化 |\n"
        "|---|---|---|\n"
        "| [**Myriad**](https://github.com/Myriad-You/Myriad) "
        f"| [PR #585](https://github.com/Myriad-You/Myriad/pull/585) 补全 `zh-TW` 机器人配对文案（已 merge） "
        f"| **{my_files}** files · `+{fmt_num(my_add)}` `−{fmt_num(my_del)}` |\n"
        "| [**Sakurairo**](https://github.com/mirai-mamori/Sakurairo) "
        f"| {sak_n} 个 PR：本地曲库 / 说说时间轴 / 评论表单修复 "
        f"| **{sak_n}** PRs · `+{fmt_num(sak_add)}` `−{fmt_num(sak_del)}` |"
    )

    text = README.read_text(encoding="utf-8")
    text = replace_block(text, "projects", projects)
    text = replace_block(text, "oss", oss)
    README.write_text(text, encoding="utf-8")
    print("README stats refreshed")


if __name__ == "__main__":
    main()
