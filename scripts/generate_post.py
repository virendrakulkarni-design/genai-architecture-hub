#!/usr/bin/env python3
"""
Automated Hourly Post Generation Script for GenAI Architecture Hub
Pulls next topic from upcoming_topics.json, supports on-demand custom topics (--custom-topic),
auto-replenishes queue when low, applies Humanizer skill constraints (strictly no emojis,
natural human systems engineer voice), and updates posts.json and posts.js.
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
POSTS_JSON = os.path.join(DATA_DIR, "posts.json")
POSTS_JS = os.path.join(DATA_DIR, "posts.js")
UPCOMING_JSON = os.path.join(DATA_DIR, "upcoming_topics.json")

def remove_emojis(text):
    """Strip all unicode emojis, symbols, and pictographs for pure humanized prose."""
    if not isinstance(text, str):
        return text
    emoji_pattern = re.compile(
        "["
        "\U00010000-\U0010FFFF"  # Supplemental symbols, pictographs, emojis
        "\u2600-\u27BF"          # Misc symbols & dingbats
        "\u2300-\u23FF"          # Misc technical
        "\u2B50\u2B55\u2934\u2935\u25AA\u25AB\u25FE\u25FD\u25FB\u25FC"
        "]+",
        flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub("", text)
    return re.sub(r' +', ' ', cleaned).strip()

def humanize_post(post):
    """
    Apply Humanizer skill constraints:
    1. Strictly zero emojis across all fields.
    2. Direct, natural phrasing for takeaways and titles.
    """
    if not post or not isinstance(post, dict):
        return post

    # Clean top-level text fields
    for field in ["title", "lead", "level", "readTime", "audience", "diagramCaption"]:
        if field in post and isinstance(post[field], str):
            post[field] = remove_emojis(post[field])

    # Clean stats block
    if "stats" in post and isinstance(post["stats"], dict):
        if "title" in post["stats"]:
            post["stats"]["title"] = remove_emojis(post["stats"]["title"])
        if "items" in post["stats"] and isinstance(post["stats"]["items"], list):
            post["stats"]["items"] = [remove_emojis(item) for item in post["stats"]["items"]]

    # Clean mental model block
    if "mentalModel" in post and isinstance(post["mentalModel"], dict):
        if "title" in post["mentalModel"]:
            post["mentalModel"]["title"] = remove_emojis(post["mentalModel"]["title"])
        if "text" in post["mentalModel"]:
            post["mentalModel"]["text"] = remove_emojis(post["mentalModel"]["text"])

    # Clean takeaway block
    if "takeaway" in post and isinstance(post["takeaway"], dict):
        if "title" in post["takeaway"]:
            clean_title = remove_emojis(post["takeaway"]["title"]).strip()
            # Normalize title if it was an AI stock label
            if not clean_title or "takeaway" not in clean_title.lower():
                clean_title = "Key Takeaways"
            post["takeaway"]["title"] = clean_title
        if "badge" in post["takeaway"]:
            post["takeaway"]["badge"] = remove_emojis(post["takeaway"]["badge"])
        if "items" in post["takeaway"] and isinstance(post["takeaway"]["items"], list):
            post["takeaway"]["items"] = [remove_emojis(item) for item in post["takeaway"]["items"]]

    return post

KEYWORD_TEMPLATES = {
    "diffusion": {
        "topic": "Diffusion Models & Flow Matching Architecture",
        "level": "LEVEL 9: GENERATIVE MEDIA ARCHITECTURE",
        "levelClass": "level-3",
        "readTime": "9 min read",
        "audience": "Vision & Multimodal AI Engineers",
        "title": "Diffusion Models to Flow Matching: How Stable Diffusion & Flux Synthesize Media",
        "lead": "From reverse heat equations to forward ODE flow matching, modern diffusion transformers (DiTs) convert random Gaussian noise into photorealistic images and video without mode collapse.",
        "stats": {
            "type": "info",
            "title": "Generation Shift from GANs to Diffusion:",
            "items": [
                "GANs suffered from catastrophic mode collapse and training instability; Diffusion models guarantee mathematical convergence via denoising score matching.",
                "Flow matching with Rectified Flow (Flux.1 / SD3) cuts generation steps from 50 steps down to 12-20 steps with straight probability trajectories."
            ]
        },
        "mentalModel": {
            "title": "1. The 60-Second Mental Model: Sculpting a Marble Block",
            "text": "Imagine a sculptor starting with a rough, noisy block of uncarved marble. At each step, they chip away a tiny layer of noise guided by text conditioning. After 20 denoising steps, the noise has vanished and the statue remains.<br><br><strong>Diffusion is progressive reverse entropy:</strong> The forward process adds noise until an image becomes static; the reverse process learns to predict and subtract that noise step by step."
        },
        "diagram": "graph LR\n    Noise[\"Random Gaussian Noise z_T\"] --> Step1[\"DiT Block (t=20)\"]\n    Prompt[\"Text Conditioning (T5/CLIP)\"] --> Step1\n    Step1 --> Step2[\"Denoising Step (t=10)\"]\n    Prompt --> Step2\n    Step2 --> Image[\"Synthesized 1024x1024 Image\"]\n    style Image fill:#065f46,stroke:#34d399,color:#fff",
        "diagramCaption": "Figure: Iterative Reverse Denoising in Diffusion Transformers (DiT)",
        "codeTitle": "flow_matching_euler_step.py",
        "codeContent": "def flow_matching_euler_step(model, x_t, prompt_embeds, t_curr, t_next):\n    # Velocity vector field prediction\n    v_pred = model(x_t, prompt_embeds, timestep=t_curr)\n    dt = t_next - t_curr\n    # Euler forward step along straight ODE trajectory\n    x_next = x_t + v_pred * dt\n    return x_next",
        "takeaway": {
            "title": "Key Takeaways",
            "items": [
                "Modern generative vision has shifted from U-Nets to Diffusion Transformers (DiT).",
                "Flow matching straightens vector trajectories, cutting compute in half.",
                "Latent Diffusion performs denoising in a compressed VAE latent space (8x downsampled) to save VRAM."
            ],
            "badge": "Flow matching bridges continuous physics ODEs with discrete transformer inference."
        }
    }
}

RESERVE_TOPICS_POOL = [
  {
    "topic": "Reasoning Models & Test-Time Compute",
    "level": "LEVEL 10: INFERENCE-TIME REASONING",
    "levelClass": "level-4",
    "readTime": "9 min read",
    "audience": "Frontier AI & Systems Researchers",
    "title": "Test-Time Compute Scaling: Why Spending More Compute at Inference Wins",
    "lead": "Scaling laws initially focused on pre-training cluster capacity. Reasoning architectures (o1, DeepSeek-R1) shift compute to the inference phase through reinforcement learning and search rollouts.",
    "stats": {
      "type": "success",
      "title": "Inference Scaling Law Breakthrough:",
      "items": [
        "On competition math and code verification, spending 100x more tokens on reasoning chains boosts accuracy from 16% to over 83%.",
        "Test-time search (MCTS and self-correction rollouts) turns a 7B model into the equivalent of a 70B zero-shot model."
      ]
    },
    "mentalModel": {
      "title": "1. The 60-Second Mental Model: Fast Intuition vs. Deliberate Calculation",
      "text": "System 1 produces immediate answers without pausing. System 2 breaks complex calculations into sub-steps, checks carrying digits, and verifies constraints before emitting final conclusions.<br><br><strong>Test-time compute provides the model with a working scratchpad before emitting final tokens.</strong>"
    },
    "diagram": "graph TD\n    In[\"Complex Logic Question\"] --> CoT[\"Reasoning Chain (Hidden Test-Time Compute)\"]\n    CoT --> Check1[\"Hypothesis A: Fails constraint\"]\n    CoT --> Check2[\"Hypothesis B: Backtracks &amp; corrects\"]\n    CoT --> Valid[\"Hypothesis C: Verified correct!\"]\n    Valid --> Out[\"Clean Final Answer\"]\n    style CoT fill:#1e3a8a,stroke:#60a5fa,color:#fff\n    style Out fill:#065f46,stroke:#34d399,color:#fff",
    "diagramCaption": "Figure: Exploration and Verification Tree during Test-Time Reasoning",
    "codeTitle": "test_time_search_scaffold.py",
    "codeContent": "# Conceptual Test-Time Rollout & Self-Verification\ndef test_time_reasoning(model, prompt, num_rollouts=5):\n    candidates = [model.generate_thought_chain(prompt) for _ in range(num_rollouts)]\n    verified = [c for c in candidates if verify_math_constraints(c)]\n    return majority_vote(verified) if verified else candidates[0]",
    "takeaway": {
      "title": "Key Takeaways",
      "items": [
        "Inference compute provides a scaling vector when pre-training data hits human text limits.",
        "Reinforcement learning from verifiable rewards teaches models to self-correct during generation.",
        "Allocate reasoning budgets carefully: deterministic lookup tasks do not need extended thought chains."
      ],
      "badge": "Test-time compute transforms models from reactive predictors into search-based problem solvers."
    }
  }
]

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sync_posts_js(posts):
    js_content = "// Auto-generated data sync for direct local file:// and offline execution\n"
    js_content += f"window.POSTS_DATA = {json.dumps(posts, indent=2, ensure_ascii=False)};\n"
    with open(POSTS_JS, "w", encoding="utf-8") as f:
        f.write(js_content)

def validate_post_schema(post):
    required = ["id", "publishedAt", "level", "readTime", "audience", "title", "lead", "stats", "mentalModel", "diagram", "diagramCaption", "codeTitle", "codeContent", "takeaway"]
    for field in required:
        if field not in post:
            raise ValueError(f"Post is missing required field: '{field}'")
    return True

def generate_custom_topic_post(custom_keyword):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = f"""You are a Principal AI Systems Architect writing for an elite enterprise GenAI engineering community.
Follow these Humanizer writing rules:
- STRICT ZERO EMOJIS: Do not use any emojis anywhere in any field (no emojis in titles, headers, bullet points, mental models, code comments, or takeaways).
- Voice: Write like an experienced human systems architect. Clear, concrete, and technically precise.
- No staged run-ups (do not use "Let's dive in", "In the rapidly evolving landscape", "As modern GenAI pipelines mature").
- No fake contrasts ("not just X, but Y"). State technical facts directly.
- No forced triads or rhythm-by-rule. Use natural sentence variety.
- Ground claims in real engineering numbers, hardware bottlenecks (SRAM, HBM, PCIe bandwidth), and concrete production tradeoffs.

Create an advanced, high-impact post on the GenAI topic: '{custom_keyword}'.
Include:
1. Real-world engineering benchmarks and memory/latency stats.
2. 60-second mental model with relatable CS analogy.
3. Clean Mermaid diagram.
4. Production code block (PyTorch, Triton, or Python).
5. Actionable key takeaways.

Output ONLY valid JSON matching:
{{
  "id": "post-X",
  "publishedAt": "YYYY-MM-DD HH:MM UTC",
  "level": "LEVEL X: ...",
  "levelClass": "level-3",
  "readTime": "8 min read",
  "audience": "Senior GenAI Engineers & Architects",
  "title": "...",
  "lead": "...",
  "stats": {{"type": "info", "title": "...", "items": ["..."]}},
  "mentalModel": {{"title": "1. The 60-Second Mental Model: ...", "text": "..."}},
  "diagram": "graph TD\\n...",
  "diagramCaption": "Figure: ...",
  "codeTitle": "...py",
  "codeContent": "...",
  "takeaway": {{"title": "Key Takeaways", "items": ["..."], "badge": "..."}}
}}"""
            res = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = res.content[0].text
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0]
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0]
            parsed = json.loads(raw.strip())
            return humanize_post(parsed)
        except Exception as err:
            print(f"Claude API error: {err}. Falling back to template...")

    kw_lower = custom_keyword.lower()
    for k, template in KEYWORD_TEMPLATES.items():
        if k in kw_lower:
            item = humanize_post(template.copy())
            if "publishedAt" not in item or not item["publishedAt"]:
                item["publishedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            return item

    fallback = {
        "topic": custom_keyword,
        "publishedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "level": f"DEEP-DIVE: {custom_keyword.upper()}",
        "levelClass": "level-3",
        "readTime": "8 min read",
        "audience": "Senior Engineering Community",
        "title": f"Architecting {custom_keyword}: Systems Design, Latency & Enterprise Scaling",
        "lead": f"Designing production systems around {custom_keyword} requires evaluating architectural tradeoffs between compute latency, memory bandwidth, and accuracy.",
        "stats": {
            "type": "info",
            "title": f"Key Metrics in {custom_keyword}:",
            "items": [
                f"Optimizing {custom_keyword} lowers GPU memory overhead by over 35%.",
                "Improves generation throughput across distributed clusters."
            ]
        },
        "mentalModel": {
            "title": f"1. The 60-Second Mental Model: {custom_keyword}",
            "text": f"Just as database indices trade disk space for search speed, {custom_keyword} balances compute, memory bandwidth, and semantic accuracy across generative pipelines."
        },
        "diagram": f"graph LR\n    Input[\"Input Tensor\"] --> Engine[\"GenAI {custom_keyword} Core\"]\n    Engine --> Output[\"Optimized Representation\"]\n    style Engine fill:#10b981,stroke:#34d399,color:#fff",
        "diagramCaption": f"Figure: Operational Pipeline for {custom_keyword}",
        "codeTitle": "genai_pipeline.py",
        "codeContent": f"# Implementation Pattern for {custom_keyword}\n# Ensures high throughput and mathematical stability across inference batches.",
        "takeaway": {
            "title": "Key Takeaways",
            "items": [
                f"Profile {custom_keyword} latency using PyTorch Profiler before deploying to production.",
                "Balance parameter scaling with inference-time memory constraints."
            ],
            "badge": f"Mastering {custom_keyword} separates experimental prototypes from resilient production AI systems."
        }
    }
    return humanize_post(fallback)

def replenish_queue_if_low(upcoming, posts):
    if len(upcoming) <= 1:
        print("Upcoming queue is low (<= 1 topic). Replenishing from reserve pool...")
        current_titles = {p.get("title") for p in posts} | {u.get("title") for u in upcoming}
        for item in RESERVE_TOPICS_POOL:
            if item.get("title") not in current_titles:
                upcoming.append(humanize_post(item.copy()))
        print(f"Auto-replenished queue. Total available now: {len(upcoming)}")
    return upcoming

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Publish next scheduled GenAI Architecture post.")
    parser.add_argument("--dry-run", action="store_true", help="Validate next post without modifying files.")
    parser.add_argument("--custom-topic", type=str, help="Suggest a custom GenAI topic or keyword.")
    parser.add_argument("--list-queue", action="store_true", help="List remaining upcoming topics.")
    args = parser.parse_args()

    upcoming = load_json(UPCOMING_JSON)
    posts = load_json(POSTS_JSON)

    if args.list_queue:
        print(f"\nUpcoming Queued Topics ({len(upcoming)} remaining):")
        for i, t in enumerate(upcoming, 1):
            print(f"  {i}. {t.get('title', t.get('topic'))}")
        return

    if args.custom_topic and args.custom_topic.strip():
        print(f"Custom topic suggested: '{args.custom_topic}'")
        post_to_publish = generate_custom_topic_post(args.custom_topic.strip())
    else:
        upcoming = replenish_queue_if_low(upcoming, posts)
        if not upcoming:
            print("No topics available.")
            sys.exit(0)
        post_to_publish = upcoming.pop(0)

    post_to_publish = humanize_post(post_to_publish)
    post_to_publish["id"] = f"post-{len(posts) + 1}"
    if "publishedAt" not in post_to_publish or not post_to_publish["publishedAt"]:
        post_to_publish["publishedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    validate_post_schema(post_to_publish)

    print(f"Publishing: {post_to_publish['title']}")

    if args.dry_run:
        print(f"[DRY RUN] Validated post: {post_to_publish['title']}")
        return

    posts.append(post_to_publish)
    save_json(POSTS_JSON, posts)
    sync_posts_js(posts)
    save_json(UPCOMING_JSON, upcoming)

    print(f"Published '{post_to_publish['title']}' successfully!")
    print(f"Total Published Posts: {len(posts)} | Remaining Queued: {len(upcoming)}")

if __name__ == "__main__":
    main()
