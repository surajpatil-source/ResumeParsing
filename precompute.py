"""Pre-computation: build embeddings, detect honeypots, save artifacts."""

import json
import time
import argparse
import numpy as np
from pathlib import Path

from ranker.loader import stream_candidates, load_jd_text
from ranker.honeypot import detect_honeypots, compute_honeypot_probability
from ranker.config import EMBEDDING_MODEL, EMBEDDING_DIM


def build_candidate_text(candidate: dict) -> str:
    profile = candidate.get("profile", {})
    parts = [
        profile.get("headline", ""),
        profile.get("summary", ""),
    ]
    for job in candidate.get("career_history", []):
        desc = job.get("description", "")
        title = job.get("title", "")
        if title:
            parts.append(title)
        if desc:
            parts.append(desc)

    for skill in candidate.get("skills", []):
        parts.append(skill.get("name", ""))

    return " ".join(p for p in parts if p).strip()


def main():
    parser = argparse.ArgumentParser(description="Pre-compute embeddings and honeypot index")
    parser.add_argument("--candidates", default="Dataset/candidates.jsonl")
    parser.add_argument("--jd", default="Dataset/job_description.docx")
    parser.add_argument("--output-dir", default="precomputed")
    parser.add_argument("--batch-size", type=int, default=256)
    args = parser.parse_args()

    output = Path(args.output_dir)
    output.mkdir(exist_ok=True)

    print("=" * 60)
    print("STEP 1: Loading candidates...")
    print("=" * 60)
    start = time.time()
    candidates = list(stream_candidates(args.candidates))
    print(f"Loaded {len(candidates)} candidates in {time.time() - start:.1f}s")

    print("\n" + "=" * 60)
    print("STEP 2: Detecting honeypots...")
    print("=" * 60)
    start = time.time()
    honeypot_ids = detect_honeypots(candidates, threshold=0.5)
    print(f"Detected {len(honeypot_ids)} honeypots in {time.time() - start:.1f}s")

    hp_details = []
    for c in candidates:
        prob = compute_honeypot_probability(c)
        if prob >= 0.3:
            hp_details.append({"id": c["candidate_id"], "probability": round(prob, 3)})
    hp_details.sort(key=lambda x: -x["probability"])
    print(f"Candidates with honeypot probability >= 0.3: {len(hp_details)}")

    with open(output / "honeypots.json", "w") as f:
        json.dump(sorted(honeypot_ids), f, indent=2)
    with open(output / "honeypot_details.json", "w") as f:
        json.dump(hp_details, f, indent=2)

    print("\n" + "=" * 60)
    print("STEP 3: Building text representations...")
    print("=" * 60)
    start = time.time()
    candidate_ids = []
    candidate_texts = []
    for c in candidates:
        candidate_ids.append(c["candidate_id"])
        candidate_texts.append(build_candidate_text(c))
    print(f"Built {len(candidate_texts)} text representations in {time.time() - start:.1f}s")

    with open(output / "candidate_ids.json", "w") as f:
        json.dump(candidate_ids, f)

    print("\n" + "=" * 60)
    print("STEP 4: Loading embedding model...")
    print("=" * 60)
    start = time.time()
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBEDDING_MODEL)
    print(f"Model loaded in {time.time() - start:.1f}s")

    print("\n" + "=" * 60)
    print("STEP 5: Encoding JD...")
    print("=" * 60)
    jd_text = load_jd_text(args.jd)
    jd_embedding = model.encode([jd_text], show_progress_bar=False, normalize_embeddings=True)
    np.save(str(output / "jd_embedding.npy"), jd_embedding[0])
    print(f"JD embedding shape: {jd_embedding.shape}")

    print("\n" + "=" * 60)
    print("STEP 6: Encoding candidates (this may take a while)...")
    print("=" * 60)
    start = time.time()
    embeddings = model.encode(
        candidate_texts,
        batch_size=args.batch_size,
        show_progress_bar=True,
        normalize_embeddings=True,
    )
    np.save(str(output / "embeddings.npy"), embeddings)
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"Encoding took {time.time() - start:.1f}s")

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"Artifacts saved to {output}/")
    for p in output.iterdir():
        size_mb = p.stat().st_size / 1024 / 1024
        print(f"  {p.name}: {size_mb:.1f} MB")


if __name__ == "__main__":
    main()
