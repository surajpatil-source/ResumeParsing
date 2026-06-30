# AI Candidate Ranking System

Semantic candidate ranking for the Redrob AI Hackathon. Ranks 100K candidates against a Senior AI Engineer job description using a hybrid approach: rule-based feature engineering + sentence-transformer embeddings + behavioral signal weighting.

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Pre-compute embeddings and honeypot index (run once)

```bash
python precompute.py --candidates Dataset/candidates.jsonl --jd Dataset/job_description.docx
```

This takes ~50 minutes on a 4-core CPU (no GPU acceleration used). Creates artifacts in `precomputed/`.

### 3. Run ranking

```bash
python rank.py --candidates Dataset/candidates.jsonl --output submission.csv
```

Produces `submission.csv` with the top 100 candidates ranked by fit score. Runs in ~25-40 seconds on CPU.

### 4. Validate

```bash
python Dataset/validate_submission.py submission.csv
```

### Single command to reproduce (after pre-computation):

```bash
python rank.py --candidates Dataset/candidates.jsonl --output submission.csv
```

## Architecture

**Two-phase pipeline:**

- **Phase A (Pre-computation):** Generate 384-dim text embeddings for all 100K candidates using `all-MiniLM-L6-v2`, detect honeypot candidates via 4 integrity checks
- **Phase B (Runtime):** Stream candidates → extract features → hard filter → composite score → rank → output CSV

**3-layer scoring:**

1. **Hard filters:** Remove honeypots, consulting-only careers (no product company experience), non-tech profiles, pure research/academic profiles (high ML signal, zero production evidence)
2. **Composite fit score (0-1):** Skills (30%), Career relevance (25%), Title (10%), Semantic similarity (15%), Experience (10%), Location (5%), Education (5%)
3. **Behavioral & trap-pattern penalties (multipliers):** Two-tier ghost-candidate detection (0.55-0.80x for inactive/unresponsive profiles, 0.80-1.05x normal range), job-hopper penalty (0.70-0.85x for short average tenure), LangChain-only-recent trap (0.65x), CV/speech-without-NLP trap (0.70x), closed-source-senior soft penalty (0.98x), visa-blocker penalty (0.55x for non-India + won't-relocate + remote-only), and a soft title/description-mismatch penalty

## Sandbox App

```bash
streamlit run app.py
```

Upload candidate JSON or use the built-in sample to see rankings with reasoning.

## Project Structure

```
├── rank.py              # Main CLI entry point
├── precompute.py        # Pre-computation (embeddings + honeypots)
├── app.py               # Streamlit sandbox app
├── ranker/
│   ├── config.py        # Weights, thresholds, skill taxonomy
│   ├── loader.py        # JSONL streaming reader
│   ├── features.py      # 7 feature groups
│   ├── honeypot.py      # Honeypot detection
│   ├── scorer.py        # Composite scoring
│   ├── reasoner.py      # Per-candidate reasoning
│   └── pipeline.py      # Full pipeline orchestration
├── precomputed/         # Generated artifacts
├── Dataset/             # Input data
└── approach_deck.pptx   # Approach presentation
```

## Runtime Constraints

| Constraint | Limit | Achieved |
|-----------|-------|----------|
| Execution time | 5 min | 18.6s |
| RAM | 16 GB | ~2 GB |
| GPU | None | CPU only |
| Network | None | Fully offline |
| Disk | 5 GB | 147 MB |
