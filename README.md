# GenAI Architecture Hub | Systems Engineering & Frontier AI

[![Hub Visitors](https://komarev.com/ghpvc/?username=virendrakulkarni-genai-architecture-hub&label=Hub+Visitors&color=10b981&style=flat-square)](https://github.com/virendrakulkarni-design/genai-architecture-hub)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A high-throughput, data-driven engineering blog and community dispatch hub explaining **Generative AI concepts, scaling laws, systems architecture, and production best practices**.

---

## Humanizer Skill & Writing Standards

All post generation adheres to the **Humanizer Skill** located in [`skills/humanizer/SKILL.md`](skills/humanizer/SKILL.md) and [`.agents/skills/humanizer/SKILL.md`](.agents/skills/humanizer/SKILL.md):

- **Strict Zero Emoji Rule:** No emojis are permitted anywhere in generated posts, titles, takeaways, badges, diagrams, or lists. Technical documentation communicates through clear prose and rigorous diagrams, not decorative pictograms.
- **Natural Human Systems Voice:** Eliminates AI clichés such as staged run-ups ("Let's dive in", "As modern pipelines mature"), fake contrasts ("not just X, but Y"), and forced triads.
- **Concrete Technical Rigor:** Anchored in real memory numbers (SRAM, HBM, KV-cache bandwidth), system architectures, and production failure modes.

---

## Hourly Automated Scheduling (Every Hour at Minute 00)

This repository automatically publishes a new in-depth architectural post every hour:
- **Frequency:** `0 * * * *` (Every hour at minute 00).
- **Automation Pipeline:** [`.github/workflows/schedule_post.yml`](.github/workflows/schedule_post.yml)
- **Generation Script:** [`scripts/generate_post.py`](scripts/generate_post.py) & [`scripts/generate_post.ps1`](scripts/generate_post.ps1).
- **Topic Backlog:** Stored in [`data/upcoming_topics.json`](data/upcoming_topics.json) (covering Speculative Decoding, Hybrid Search/RRF, PagedAttention/FlashAttention, Diffusion Transformers, and Test-Time Compute).

---

## Suggesting Custom GenAI Topics On Demand

### From GitHub Actions UI:
1. Go to the **Actions** tab in this repository.
2. Select **"Hourly GenAI Architectural Publisher"**.
3. Click **"Run workflow"**.
4. Enter any topic (e.g. `Diffusion Models`, `Reasoning Models`, `KV Cache Optimization`, `DPO`).
5. Click **Run workflow** to publish immediately.

### From Command Line:
```powershell
# Immediately generate and publish:
python scripts/generate_post.py --custom-topic "Diffusion Models"

# Queue a custom topic for the next hourly run:
powershell scripts\queue_topic.ps1 -Topic "Vision Transformers (ViT)"
```

---

## Deployment Options

### GitHub Pages (Recommended)
1. Push to GitHub.
2. Under **Settings > Pages**, set Source to **Deploy from a branch (main / root)** or **GitHub Actions**.
3. Add `ANTHROPIC_API_KEY` under **Repository Settings > Secrets and variables > Actions** (optional for dynamic synthesis).

### Docker Compose (Corporate Intranet / VPN)
```bash
docker-compose up -d --build
```
Live at `http://<host-ip>:8081`.
