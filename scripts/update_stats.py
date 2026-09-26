#!/usr/bin/env python3
"""Refresh quantified project / OSS stats inside README.md markers (best-effort).

Safe to run even when:
- some repos are private or stats endpoints return 404/202
- README has no stats markers (no-op)
"""

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
    ("yi-relay", "驿 Relay：统一长任务 Agent 入口产品原型（NAS/常驻后端 + 多端同步）"),
]

MYRIAD_PRS = ["Myriad-You/Myriad#585", "Myriad-You/Myriad#588"]
SAKURAIRO_PRS = [
    "mirai-mamori/Sakurairo#1429",
    "mirai-mamori/Sakurairo#1430",
    "mirai-mamori/Sakurairo#1431",
]


def gh_get(path: str):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "lossalt-profile-stats",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        "https://api.github.com/" + path.lstrip("/"),
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as exc:
        # 202: stats still computing; 404: empty/private/unavailable
        if exc.code in (202, 404, 403):
            return None
        raise
    except urllib.error.URLError:
        return None


def repo_stats(repo: str) -> dict[str, int]:
    data = gh_get(f"repos/{repo}/stats/contributors")
    commits = add = delete = 0
    if isinstance(data, list):
        for person in data:
            if person.get("author", {}).get("login") != OWNER:
                continue
            commits += int(person.get("total") or 0)
            for week in person.get("weeks") or []:
                add += int(week.get("a") or 0)
                delete += int(week.get("d") or 0)
    else:
        # Fallback: commit list length (public repos)
        commits_data = gh_get(f"repos/{repo}/commits?per_page=1")
        # approximate via Link header is overkill; use 0 if unknown
        commits = 0
        if isinstance(commits_data, list) and commits_data:
            commits = 1

    files = 0
    tree = gh_get(f"repos/{repo}/git/trees/HEAD?recursive=1")
    if isinstance(tree, dict):
        files = sum(1 for item in tree.get("tree") or [] if item.get("type") == "blob")

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


def fmt_num(n: int) -> str:
    return f"{n:,}" if abs(n) >= 1000 else str(n)


def replace_block(text: str, name: str, payload: str) -> str:
    pattern = rf"(<!-- stats:{name}:start -->)(.*?)(<!-- stats:{name}:end -->)"
    if not re.search(pattern, text, flags=re.S):
        print(f"skip marker stats:{name} (not present)")
        return text
    new = f"\\1\n{payload.rstrip()}\n\\3"
    updated, count = re.subn(pattern, new, text, count=1, flags=re.S)
    if count != 1:
        return text
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
        f"| [PR #585](https://github.com/Myriad-You/Myriad/pull/585) `zh-TW` 补全 · "
        f"[PR #588](https://github.com/Myriad-You/Myriad/pull/588) 本地曲库音源（均已 merge） "
        f"| **{my_files}** files · `+{fmt_num(my_add)}` `−{fmt_num(my_del)}` |\n"
        "| [**Sakurairo**](https://github.com/mirai-mamori/Sakurairo) "
        f"| {sak_n} 个 PR：本地曲库 / 说说时间轴 / 评论表单修复（已进 preview） "
        f"| **{sak_n}** PRs · `+{fmt_num(sak_add)}` `−{fmt_num(sak_del)}` |"
    )

    text = README.read_text(encoding="utf-8")
    text = replace_block(text, "projects", projects)
    text = replace_block(text, "oss", oss)
    README.write_text(text, encoding="utf-8")
    print("README stats refreshed (best-effort)")


if __name__ == "__main__":
    main()
