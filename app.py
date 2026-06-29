"""Streamlit sandbox app for the AI Candidate Ranking System."""

import json
import csv
import io
import tempfile
import time
import streamlit as st
import numpy as np
from pathlib import Path

from ranker.features import extract_all_features
from ranker.scorer import compute_final_score, should_hard_filter
from ranker.reasoner import generate_reasoning
from ranker.honeypot import compute_honeypot_probability

st.set_page_config(page_title="AI Candidate Ranker", layout="wide")

st.title("AI Candidate Ranking System")
st.markdown("Rank candidates against a job description using semantic understanding, not keyword matching.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Job Description")
    default_jd = (
        "Senior AI Engineer — Founding Team\n"
        "Must have: Production embeddings-based retrieval, vector databases, "
        "strong Python, evaluation frameworks for ranking.\n"
        "Nice to have: LLM fine-tuning, learning-to-rank, HR-tech experience.\n"
        "Experience: 5-9 years. Location: Pune/Noida, India (Hybrid)."
    )
    jd_text = st.text_area("Paste job description:", value=default_jd, height=200)

with col2:
    st.subheader("Candidates")
    upload = st.file_uploader("Upload candidates JSON (array of candidate objects):", type=["json"])
    use_sample = st.checkbox("Use sample candidates (first 50 from dataset)", value=True)

if st.button("Rank Candidates", type="primary"):
    candidates = []

    if upload:
        raw = upload.read().decode("utf-8")
        candidates = json.loads(raw)
        if isinstance(candidates, dict):
            candidates = [candidates]
    elif use_sample:
        sample_path = Path("Dataset/sample_candidates.json")
        if sample_path.exists():
            candidates = json.load(open(sample_path))
        else:
            st.error("Sample file not found at Dataset/sample_candidates.json")

    if not candidates:
        st.warning("No candidates loaded.")
    else:
        start = time.time()
        progress = st.progress(0, text="Scoring candidates...")

        precomputed = Path("precomputed")
        embeddings = None
        jd_embedding = None
        candidate_id_to_idx = {}

        emb_path = precomputed / "embeddings.npy"
        jd_emb_path = precomputed / "jd_embedding.npy"
        ids_path = precomputed / "candidate_ids.json"

        if emb_path.exists() and jd_emb_path.exists() and ids_path.exists():
            embeddings = np.load(str(emb_path))
            jd_embedding = np.load(str(jd_emb_path))
            id_list = json.load(open(ids_path))
            candidate_id_to_idx = {cid: i for i, cid in enumerate(id_list)}
            jd_norm = jd_embedding / (np.linalg.norm(jd_embedding) + 1e-10)
            emb_norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10
            embeddings_normed = embeddings / emb_norms

        scored = []
        for i, c in enumerate(candidates):
            cid = c["candidate_id"]
            hp_prob = compute_honeypot_probability(c)
            features = extract_all_features(c)
            is_honeypot = hp_prob >= 0.4

            if should_hard_filter(features, is_honeypot):
                continue

            semantic_sim = 0.0
            if embeddings is not None and cid in candidate_id_to_idx:
                idx = candidate_id_to_idx[cid]
                semantic_sim = float(np.dot(embeddings_normed[idx], jd_norm.flatten()))
                semantic_sim = max(0.0, semantic_sim)

            score = compute_final_score(features, semantic_sim)
            reasoning = generate_reasoning(c, features, score)
            scored.append({
                "candidate_id": cid,
                "name": c.get("profile", {}).get("anonymized_name", "Unknown"),
                "title": c.get("profile", {}).get("current_title", ""),
                "company": c.get("profile", {}).get("current_company", ""),
                "yoe": c.get("profile", {}).get("years_of_experience", 0),
                "score": score,
                "reasoning": reasoning,
            })
            progress.progress((i + 1) / len(candidates), text=f"Scored {i + 1}/{len(candidates)}")

        elapsed = time.time() - start
        scored.sort(key=lambda x: (-x["score"], x["candidate_id"]))

        top_k = min(100, len(scored))
        top = scored[:top_k]

        st.success(f"Ranked {len(scored)} candidates in {elapsed:.1f}s ({len(candidates) - len(scored)} filtered)")

        st.subheader(f"Top {top_k} Candidates")
        for rank, entry in enumerate(top, 1):
            with st.expander(f"#{rank} — {entry['name']} | {entry['title']} at {entry['company']} | Score: {entry['score']:.4f}"):
                st.markdown(f"**Experience:** {entry['yoe']:.1f} years")
                st.markdown(f"**Reasoning:** {entry['reasoning']}")

        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        max_s = top[0]["score"] if top else 1
        min_s = top[-1]["score"] if top else 0

        # Compute display scores, then re-sort by the ROUNDED value
        # (candidate_id ascending as tie-break) — same fix as rank.py,
        # since raw-score order can disagree with ID order once rounded.
        export_rows = []
        for entry in top:
            if max_s > min_s:
                norm_score = round(0.20 + 0.80 * (entry["score"] - min_s) / (max_s - min_s), 4)
            else:
                norm_score = 1.0
            export_rows.append((norm_score, entry["candidate_id"], entry["reasoning"]))

        export_rows.sort(key=lambda r: (-r[0], r[1]))

        for rank, (norm_score, cid, reasoning) in enumerate(export_rows, 1):
            writer.writerow([cid, rank, f"{norm_score:.4f}", reasoning])

        st.download_button("Download CSV", csv_buf.getvalue(), "ranked_candidates.csv", "text/csv")

st.divider()
st.caption("Built for Redrob AI Hackathon — Semantic ranking with behavioral signal weighting")