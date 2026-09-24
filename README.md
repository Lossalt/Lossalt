<p align="center">
  <img src="assets/header.svg" alt="Lossalt" width="100%"/>
</p>

<p align="center">
  <a href="https://cjsy.cc"><img alt="Site" src="https://img.shields.io/badge/Site-cjsy.cc-0ea5e9?style=flat-square"/></a>
  <img alt="PHP" src="https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white"/>
  <img alt="WordPress" src="https://img.shields.io/badge/WordPress-21759B?style=flat-square&logo=wordpress&logoColor=white"/>
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img alt="Git" src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white"/>
</p>

I design small, durable web utilities around self-hosted publishing — mainly **WordPress resource portability**, image pipelines, and operational scripts.  
围绕自建发布链路做可长期维护的小工具：WordPress 资源可搬迁、图床解耦、运维向脚本。

**Focus** — decouple content references from physical storage, so migrations do not break posts.  
**Stack** — PHP · WordPress · Python · Git

---

### Selected work

| Repository | Summary |
|---|---|
| [**article-image**](https://github.com/Lossalt/article-image) | **Movable image-bed entry for WordPress.** Posts call `article_image.php?res=cover-01` instead of embedding absolute file URLs. Physical storage is resolved from `base_url` (and optional `local_dir`), so host/domain migrations only change config — post HTML is left untouched. Whitelist key & extension validation; auto-detect among `webp/jpg/jpeg/png/gif/avif`; config file named `article_image.config.php` to avoid drop-in collisions. |
| [**random-img**](https://github.com/Lossalt/random-img) | **Random wallpaper redirect service.** Separate `pc` / `mobile` pools with directory auto-scan (no hardcoded counts). Modes: `302` redirect, `?serve` byte streaming, `?json` metadata, plus `api.php` device index. Deploy full repo (local images) or PHP-only (fallback to GitHub raw). MIT-licensed PHP, Nginx sample included. |
| [**iptv-gen**](https://github.com/Lossalt/iptv-gen) | **IPTV M3U pipeline.** Collects channels from multiple sources, probes liveness on the LAN, ranks by stream quality, and exports a clean playlist. Python CLI oriented to self-hosted media setups. |

Design thread across the PHP tools: **keep content references stable, keep storage replaceable.**

---

### Open source

| Project | Contribution |
|---|---|
| [**Myriad**](https://github.com/Myriad-You/Myriad) | [PR #585](https://github.com/Myriad-You/Myriad/pull/585) — **merged.** Completed `zh-TW` copy for bot pairing / unpairing UI in `frontend/src/i18n/zh-TW.json` (~60 keys: QQ, Telegram, Discord, Feishu). Product wording aligned with zh-CN source and locale conventions (`配對碼` / `機器人`; QQ・Telegram `私聊`, Discord `私訊`, Feishu `單聊`). Reviewed & approved by [mirai-mamori](https://github.com/mirai-mamori). |
| [**Sakurairo**](https://github.com/mirai-mamori/Sakurairo) | Maintained fork of the WordPress theme (AI-assisted reading, multi-locale). Local workspace prepared (`origin` + `upstream`); contributions in progress. |

---

### Contact

- Web: [cjsy.cc](https://cjsy.cc/)  
- GitHub: [@Lossalt](https://github.com/Lossalt)

Open to discussion on **WordPress hosting/resource layout, migration tooling, and lightweight PHP services**.

---

<p align="center"><sub>Lossalt · profile</sub></p>
