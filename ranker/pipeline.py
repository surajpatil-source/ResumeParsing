"""Full ranking pipeline: load → filter → score → rank → output."""

import csv
import json
import time
import numpy as np
from pathlib import Path

from .loader import stream_candidates
from .features import extract_all_features
from .scorer import compute_final_score, should_hard_filter
from .reasoner import generate_reasoning


def run_pipeline(
    candidates_path: str,
    output_path: str,
    precomputed_dir: str = "precomputed",
    top_k: int = 100,
):
    start = time.time()
    precomputed = Path(precomputed_dir)

    print("Loading precomputed artifacts...")
    embeddings = None
    jd_embedding = None
    candidate_id_to_idx = {}

    emb_path = precomputed / "embeddings.npy"
    jd_emb_path = precomputed / "jd_embedding.npy"
    ids_path = precomputed / "candidate_ids.json"

    if emb_path.exists() and jd_emb_path.exists() and ids_path.exists():
        embeddings = np.load(str(emb_path))
        jd_embedding = np.load(str(jd_emb_path))
        with open(ids_path) as f:
            id_list = json.load(f)
        candidate_id_to_idx = {cid: i for i, cid in enumerate(id_list)}
        jd_norm = jd_embedding / (np.linalg.norm(jd_embedding) + 1e-10)
        emb_norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10
        embeddings_normed = embeddings / emb_norms
        print(f"  Loaded {len(id_list)} embeddings ({embeddings.shape})")
    else:
        print("  WARNING: No precomputed embeddings found. Semantic similarity disabled.")

    honeypot_path = precomputed / "honeypots.json"
    honeypot_ids = set()
    if honeypot_path.exists():
        with open(honeypot_path) as f:
            honeypot_ids = set(json.load(f))
        print(f"  Loaded {len(honeypot_ids)} honeypot IDs")
    else:
        print("  WARNING: No honeypot index found. Running without honeypot filter.")

    print(f"Artifacts loaded in {time.time() - start:.1f}s")

    print("Scoring candidates...")
    total = 0
    filtered = 0

    # --- Pass 1: extract features + raw semantic sims ---
    pass1 = []  # list of (cid, candidate, features, raw_sim)

    for candidate in stream_candidates(candidates_path):
        total += 1
        cid = candidate["candidate_id"]
        is_honeypot = cid in honeypot_ids

        features = extract_all_features(candidate)

        if should_hard_filter(features, is_honeypot):
            filtered += 1
            continue

        raw_sim = 0.0
        if embeddings is not None and cid in candidate_id_to_idx:
            idx = candidate_id_to_idx[cid]
            raw_sim = float(np.dot(embeddings_normed[idx], jd_norm.flatten()))
            raw_sim = max(0.0, raw_sim)

        pass1.append((cid, candidate, features, raw_sim))

        if total % 20000 == 0:
            print(f"  Processed {total} candidates ({filtered} filtered)...")

    print(f"Processed {total} candidates, filtered {filtered}, scoring {len(pass1)}...")

    # --- Normalize semantic sims to 0-1 so the 15% weight earns its full range ---
    sim_vals = [r for _, _, _, r in pass1]
    sim_min = min(sim_vals) if sim_vals else 0.0
    sim_max = max(sim_vals) if sim_vals else 1.0

    # --- Pass 2: compute final scores with normalized sim ---
    scored = []
    for cid, candidate, features, raw_sim in pass1:
        if sim_max > sim_min:
            norm_sim = (raw_sim - sim_min) / (sim_max - sim_min)
        else:
            norm_sim = 0.5
        score = compute_final_score(features, norm_sim)
        scored.append((score, cid, candidate, features))

    print(f"Scored {len(scored)} candidates.")

    # Sort: descending score, ascending candidate_id for ties (validator requirement)
    scored.sort(key=lambda x: (-x[0], x[1]))
    top = scored[:top_k]

    if len(top) == 0:
        raise ValueError("No candidates survived filtering — check honeypot/filter thresholds")

    max_score = top[0][0]
    min_score = top[-1][0] if top else 0

    print(f"Writing top {top_k} to {output_path}...")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])

        for rank_idx, (raw_score, cid, candidate, features) in enumerate(top):
            rank = rank_idx + 1
            if max_score > min_score:
                normalized = (raw_score - min_score) / (max_score - min_score)
                # Use 6 decimal places to avoid tied display scores triggering
                # validator tie-break errors (raw scores are unique; rounding to 4dp
                # can collapse distinct raw scores into the same display value)
                display_score = round(0.20 + 0.80 * normalized, 6)
            else:
                display_score = 1.0

            reasoning = generate_reasoning(candidate, features, raw_score)
            writer.writerow([cid, rank, f"{display_score:.6f}", reasoning])

    elapsed = time.time() - start
    print(f"Done in {elapsed:.1f}s. Output: {output_path}")
    print(f"Top candidate: {top[0][1]} (score {top[0][0]:.4f})")
    return output_path