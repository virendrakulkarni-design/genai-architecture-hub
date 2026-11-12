# GenAI Architecture Hub | Systems Engineering & Frontier AI

[![Hub Impressions](https://hits.sh/virendrakulkarni-design.github.io/genai-architecture-hub-impressions.svg?label=Hub+Impressions&color=10b981)](https://github.com/virendrakulkarni-design/genai-architecture-hub)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A high-throughput, data-driven engineering blog and community dispatch hub explaining **Generative AI concepts, scaling laws, systems architecture, and production best practices**.

---

## Humanizer Skill & Writing Standards

All post generation adheres to the **Humanizer Skill** located in [`skills/humanizer/SKILL.md`](skills/humanizer/SKILL.md) and [`.agents/skills/humanizer/SKILL.md`](.agents/skills/humanizer/SKILL.md):

- **Strict Zero Emoji Rule:** No emojis are permitted anywhere in generated posts, titles, takeaways, badges, diagrams, or lists. Technical documentation communicates through clear prose and rigorous diagrams, not decorative pictograms.
- **Natural Human Systems Voice:** Eliminates AI clichés such as staged run-ups ("Let's dive in", "As modern pipelines mature"), fake contrasts ("not just X, but Y"), and forced triads.
- **Concrete Technical Rigor:** Anchored in real memory numbers (SRAM, HBM, KV-cache bandwidth), system architectures, and production failure modes.

---

## Automated Publishing & Self-Healing Pipeline

This repository automatically publishes in-depth architectural posts 3 times a day using GitHub Actions:
- **Frequency:** `0 */8 * * *` (3 times daily at 00:00, 08:00, and 16:00 UTC).
- **Automation Pipeline:** [`.github/workflows/schedule_post.yml`](.github/workflows/schedule_post.yml)
- **Generation Scripts:** [`scripts/generate_post.py`](scripts/generate_post.py) & [`scripts/generate_post.ps1`](scripts/generate_post.ps1).
- **Self-Healing Replenishment:** When upcoming topics drop below threshold, the runner automatically draws from a reserve pool and procedural architectural generators, preventing the queue from ever running dry.
- **Strict Deduplication:** Employs a 4-layer deduplication engine (exact match, substring containment, technical bigrams, and token Jaccard similarity) to ensure every post is mathematically distinct from all historical dispatches.
- **Topic Backlog:** Stored in [`data/upcoming_topics.json`](data/upcoming_topics.json).

---

## Suggesting Custom GenAI Topics On Demand

### From GitHub Actions UI:
1. Go to the **Actions** tab in this repository.
2. Select **"GenAI Architectural Publisher (3x Daily)"**.
3. Click **"Run workflow"**.
4. Enter any topic (e.g. `Mixture of Depths`, `Rotary Embeddings & YaRN`, `Triton Kernels`, `DPO vs KTO`).
5. Click **Run workflow** to synthesize and publish immediately.

### From Command Line:
```powershell
# Immediately generate and publish:
python scripts/generate_post.py --custom-topic "Mixture of Depths"

# Queue a custom topic for the next scheduled run:
powershell -ExecutionPolicy Bypass -File scripts\queue_topic.ps1 -Topic "Vision Transformers (ViT)"

# List remaining queued topics:
python scripts/generate_post.py --list-queue
```

---

## Deployment Options

### GitHub Pages (Recommended)
1. Push to GitHub.
2. Under **Settings > Pages**, set Source to **GitHub Actions**.
3. Add `ANTHROPIC_API_KEY` under **Repository Settings > Secrets and variables > Actions** (optional for dynamic LLM synthesis; built-in procedural templates serve as zero-dependency fallbacks).

### Docker Compose (Corporate Intranet / VPN)
```bash
docker-compose up -d --build
```
Live at `http://<host-ip>:8081`.
