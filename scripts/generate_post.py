#!/usr/bin/env python3
"""
Automated Hourly Post Generation Script for GenAI Architecture Hub
Pulls next topic from upcoming_topics.json, supports on-demand custom topics (--custom-topic),
auto-replenishes queue when low, and updates posts.json and posts.js.
"""

import os
import sys
import json
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
POSTS_JSON = os.path.join(DATA_DIR, "posts.json")
POSTS_JS = os.path.join(DATA_DIR, "posts.js")
UPCOMING_JSON = os.path.join(DATA_DIR, "upcoming_topics.json")

KEYWORD_TEMPLATES = {
    "diffusion": {
        "topic": "Diffusion Models & Flow Matching Architecture",
        "level": "LEVEL 9: GENERATIVE MEDIA ARCHITECTURE",
        "levelClass": "level-3",
        "readTime": "9 min read",
        "audience": "Vision & Multimodal AI Engineers",
        "title": "Diffusion Models to Flow Matching: How Stable Diffusion & Flux Actually Synthesize Media",
        "lead": "From reverse heat equations to forward ODE flow matching, how modern diffusion transformers (DiTs) convert random Gaussian noise into photorealistic images and video.",
        "stats": {
            "type": "info",
            "title": "The Generation Shift from GANs to Diffusion:",
            "items": [
                "GANs suffered from catastrophic mode collapse and training instability; Diffusion models guarantee mathematical convergence via denoising score matching.",
                "Flow matching with Rectified Flow (Flux.1 / SD3) cuts generation steps from <strong>50 steps down to 12-20 steps</strong> with straight probability trajectories."
            ]
        },
        "mentalModel": {
            "title": "1. The 60-Second Mental Model: Sculpting a Marble Block",
            "text": "Imagine a sculptor starting with a rough, noisy block of uncarved marble. At each step, they chip away a tiny layer of noise guided by the text prompt ('a majestic golden lion'). After 20 denoising steps, the noise has vanished and the statue remains.<br><br><strong>Diffusion is progressive reverse entropy:</strong> The forward process adds noise until an image becomes static; the reverse process learns to predict and subtract that noise step by step."
        },
        "diagram": "graph LR\n    Noise[\"Random Gaussian Noise z_T\"] --> Step1[\"DiT Block (t=20)\"]\n    Prompt[\"Text Conditioning (T5/CLIP)\"] --> Step1\n    Step1 --> Step2[\"Denoising Step (t=10)\"]\n    Prompt --> Step2\n    Step2 --> Image[\"Synthesized 1024x1024 Image\"]\n    style Image fill:#065f46,stroke:#34d399,color:#fff",
        "diagramCaption": "Figure: Iterative Reverse Denoising in Diffusion Transformers (DiT)",
        "codeTitle": "flow_matching_euler_step.py",
        "codeContent": "def flow_matching_euler_step(model, x_t, prompt_embeds, t_curr, t_next):\n    # Velocity vector field prediction\n    v_pred = model(x_t, prompt_embeds, timestep=t_curr)\n    dt = t_next - t_curr\n    # Euler forward step along straight ODE trajectory\n    x_next = x_t + v_pred * dt\n    return x_next",
        "takeaway": {
            "title": "🎁 Architect’s \"Monday Morning\" Takeaway",
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
    "lead": "For 5 years, scaling laws focused on pre-training (bigger datasets, bigger clusters). Reasoning models (o1, DeepSeek-R1) unlocked the new frontier: scaling compute during inference through reinforcement learning.",
    "stats": {
      "type": "success",
      "title": "The Inference Scaling Law Breakthrough:",
      "items": [
        "On competition math (AIME) and code verification, spending <strong>100x more tokens on reasoning chains</strong> boosts accuracy from 16% to over 83%.",
        "Test-time search (MCTS and self-correction rollouts) turns a 7B model into the equivalent of a 70B zero-shot model."
      ]
    },
    "mentalModel": {
      "title": "1. The 60-Second Mental Model: Fast Intuition vs. Deliberate Calculation",
      "text": "• <strong>System 1 (Standard LLM):</strong> What is 2 + 2? You answer '4' instantly without pausing.<br>• <strong>System 2 (Reasoning LLM):</strong> What is 37 × 89? If you blurt out an answer in 50ms, you will fail. You grab pencil and paper, break it into (37 × 80) + (37 × 9), check carrying digits, and verify.<br><br><strong>Test-Time compute gives models pencil and paper before emitting the final token.</strong>"
    },
    "diagram": "graph TD\n    In[\"Complex Logic Question\"] --> CoT[\"Reasoning Chain (Hidden Test-Time Compute)\"]\n    CoT --> Check1[\"Hypothesis A: Fails constraint\"]\n    CoT --> Check2[\"Hypothesis B: Backtracks &amp; corrects\"]\n    CoT --> Valid[\"Hypothesis C: Verified correct!\"]\n    Valid --> Out[\"Clean Final Answer\"]\n    style CoT fill:#1e3a8a,stroke:#60a5fa,color:#fff\n    style Out fill:#065f46,stroke:#34d399,color:#fff",
    "diagramCaption": "Figure: Exploration and Verification Tree during Test-Time Reasoning",
    "codeTitle": "test_time_search_scaffold.py",
    "codeContent": "# Conceptual Test-Time Rollout & Self-Verification\ndef test_time_reasoning(model, prompt, num_rollouts=5):\n    candidates = [model.generate_thought_chain(prompt) for _ in range(num_rollouts)]\n    verified = [c for c in candidates if verify_math_constraints(c)]\n    return majority_vote(verified) if verified else candidates[0]",
    "takeaway": {
      "title": "🎁 Architect’s \"Monday Morning\" Takeaway",
      "items": [
        "Inference compute is the new scaling vector when pre-training data hits human text limits.",
        "Reinforcement learning from verifiable rewards (code execution, math proofs) teaches models to self-correct.",
        "Budget your reasoning tokens: simple classification tasks don't need 10,000 reasoning tokens."
      ],
      "badge": "Test-time compute transforms models from reactive parrots into proactive problem solvers."
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
    required = ["id", "level", "readTime", "audience", "title", "lead", "stats", "mentalModel", "diagram", "diagramCaption", "codeTitle", "codeContent", "takeaway"]
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
Create an advanced, high-impact post on the GenAI topic: '{custom_keyword}'.
Include:
1. Real-world engineering benchmarks and memory/latency stats.
2. 60-second mental model with relatable CS analogy.
3. Clean Mermaid diagram.
4. Production code block (PyTorch, Triton, or Python).
5. Actionable Monday morning takeaway.

Output ONLY valid JSON matching:
{{
  "id": "post-X",
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
  "takeaway": {{"title": "🎁 Architect’s \\"Monday Morning\\" Takeaway", "items": ["..."], "badge": "..."}}
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
            return json.loads(raw.strip())
        except Exception as err:
            print(f"⚠️ Claude API error: {err}. Falling back to template...")

    kw_lower = custom_keyword.lower()
    for k, template in KEYWORD_TEMPLATES.items():
        if k in kw_lower:
            return template.copy()

    return {
        "topic": custom_keyword,
        "level": f"DEEP-DIVE: {custom_keyword.upper()}",
        "levelClass": "level-3",
        "readTime": "8 min read",
        "audience": "Senior Engineering Community",
        "title": f"Architecting {custom_keyword}: Systems Design, Latency & Enterprise Scaling",
        "lead": f"As modern GenAI pipelines mature, understanding '{custom_keyword}' from first principles is essential for robust, cost-effective deployments.",
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
            "title": "🎁 Architect’s \"Monday Morning\" Takeaway",
            "items": [
                f"Profile {custom_keyword} latency using PyTorch Profiler before deploying to production.",
                "Balance parameter scaling with inference-time memory constraints."
            ],
            "badge": f"Mastering {custom_keyword} separates experimental prototypes from resilient production AI systems."
        }
    }

def replenish_queue_if_low(upcoming, posts):
    if len(upcoming) <= 1:
        print("🔄 Upcoming queue is low (<= 1 topic). Replenishing from reserve pool...")
        current_titles = {p.get("title") for p in posts} | {u.get("title") for u in upcoming}
        for item in RESERVE_TOPICS_POOL:
            if item.get("title") not in current_titles:
                upcoming.append(item)
        print(f"✨ Auto-replenished queue. Total available now: {len(upcoming)}")
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
        print(f"\n📋 Upcoming Queued Topics ({len(upcoming)} remaining):")
        for i, t in enumerate(upcoming, 1):
            print(f"  {i}. {t.get('title', t.get('topic'))}")
        return

    if args.custom_topic and args.custom_topic.strip():
        print(f"💡 Custom topic suggested: '{args.custom_topic}'")
        post_to_publish = generate_custom_topic_post(args.custom_topic.strip())
    else:
        upcoming = replenish_queue_if_low(upcoming, posts)
        if not upcoming:
            print("⚠️ No topics available.")
            sys.exit(0)
        post_to_publish = upcoming.pop(0)

    post_to_publish["id"] = f"post-{len(posts) + 1}"
    validate_post_schema(post_to_publish)

    print(f"🚀 Publishing: {post_to_publish['title']}")

    if args.dry_run:
        print(f"[DRY RUN] Validated post: {post_to_publish['title']}")
        return

    posts.append(post_to_publish)
    save_json(POSTS_JSON, posts)
    sync_posts_js(posts)
    save_json(UPCOMING_JSON, upcoming)

    print(f"✅ Published '{post_to_publish['title']}' successfully!")
    print(f"📊 Total Published Posts: {len(posts)} | Remaining Queued: {len(upcoming)}")

if __name__ == "__main__":
    main()
