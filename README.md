# ⚡ GenAI Architecture Hub | Systems Engineering & Frontier AI

A high-throughput, data-driven engineering blog and community dispatch hub explaining **Generative AI concepts, scaling laws, systems architecture, and production best practices**.

---

## ⏱️ Hourly Automated Scheduling (Every Hour at Minute 00)

This repository automatically publishes a new in-depth architectural post every hour:
- **Frequency:** `0 * * * *` (Every hour at minute 00).
- **Automation Pipeline:** [`workflows/schedule_post.yml`](workflows/schedule_post.yml)
- **Generation Script:** [`scripts/generate_post.py`](scripts/generate_post.py) & [`scripts/generate_post.ps1`](scripts/generate_post.ps1).
- **Topic Backlog:** Stored in [`data/upcoming_topics.json`](data/upcoming_topics.json) (covering Speculative Decoding, Hybrid Search/RRF, PagedAttention/FlashAttention, Diffusion Transformers, and Test-Time Compute).

---

## 💡 Suggesting Custom GenAI Topics On Demand

### From GitHub Actions UI:
1. Go to the **Actions** tab in this repository.
2. Select **"Hourly GenAI Architectural Publisher"**.
3. Click **"Run workflow"**.
4. Enter any topic (e.g. `Diffusion Models`, `Reasoning Models`, `KV Cache Optimization`, `DPO`).
5. Click **Run workflow** to publish immediately!

### From Command Line:
```powershell
# Immediately generate and publish:
python scripts/generate_post.py --custom-topic "Diffusion Models"

# Queue a custom topic for the next hourly run:
powershell scripts\queue_topic.ps1 -Topic "Vision Transformers (ViT)"
```

---

## 🌐 Deployment Options

### GitHub Pages (Recommended)
1. Push to GitHub.
2. Under **Settings > Pages**, set Source to **Deploy from a branch (main / root)** or **GitHub Actions**.
3. Add `ANTHROPIC_API_KEY` under **Repository Settings > Secrets and variables > Actions** (optional for dynamic synthesis).

### Docker Compose (Corporate Intranet / VPN)
```bash
docker-compose up -d --build
```
Live at `http://<host-ip>:8081`.
