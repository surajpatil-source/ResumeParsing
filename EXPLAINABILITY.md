# Explainability — How This Ranker Thinks

This document walks through five real candidates from the dataset and shows
exactly why the system scored them the way it did. Each example is a real
`candidate_id` you can look up in `Dataset/candidates.jsonl` — nothing here
is illustrative or simplified.

The goal isn't just "the math works" — it's to show the scoring logic maps
directly to specific things the job description asked us to watch for.

---

## 1. A honeypot — structurally impossible profile

**`CAND_0003430`**

- Claims **13.7 years of experience**.
- The *only* job on record is at Infosys, started **2025-03-03**, still
  current, with a claimed duration of **11 months**.

The earliest job start date is barely a year ago, but the profile claims
13.7 years of total experience — a gap of roughly 12.7 years with zero
supporting career history. This is exactly the kind of profile our
`check_yoe_vs_career_span` honeypot check exists for:

```python
career_span_years = months_between(earliest_start, REFERENCE_DATE) / 12.0
if career_span_years > 0 and claimed_yoe > career_span_years + 3:
    return 0.6  # honeypot signal
```

`compute_honeypot_probability` combined this with the other three structural
checks (duration mismatch, expert-skill-with-zero-duration, start-after-end)
to land at **0.60**, above our 0.4 threshold → hard-filtered before scoring
ever begins. This candidate never reaches the fit/behavioral scoring layers
at all — it's removed at the door, the same way a human reviewer would
immediately distrust a resume where the math doesn't add up.

We deliberately keep this list of checks narrow (4 checks, all testing for
*logical impossibility* in the data) rather than folding in soft fit signals
like title/description mismatch. That kept our honeypot count at **64**,
in line with the dataset's stated ~80 planted honeypots — an earlier version
of this filter conflated "bad fit" with "fake profile" and was incorrectly
flagging ~4,700 candidates, which would have thrown out many real, strong
applicants.

---

## 2. The LangChain-wrapper trap

**`CAND_0015578`** — AI Engineer @ Zoho

Their most recent role (Zoho, started Dec 2022, still current) describes:

> *"Implemented a RAG-based customer support chatbot integrated with our
> existing ticketing system. Built the document ingestion pipeline
> (chunking, embedding..."*

On the surface this reads like solid retrieval experience. But their **entire
career history is two jobs, both describing the same LangChain/RAG-chatbot
work**, with no job at any point in their history showing pre-LLM-era IR or
ML substance — no BM25, no learning-to-rank, no classic ML modeling, nothing
that demonstrates they understand retrieval/ranking *underneath* the LLM
wrapper they're calling.

The JD specifically warns about this pattern: someone who can wire LangChain
to an API but has never built or reasoned about a ranking system from first
principles. Our trap detector checks two things on a 12-month recency window:

```python
recent_is_langchain_shallow = count_hits(recent_text, LANGCHAIN_KEYWORDS) > 0
has_pre_llm_substance = count_hits(full_career_text, PRE_LLM_KEYWORDS) >= 2
is_langchain_trap = recent_is_langchain_shallow and not has_pre_llm_substance
```

For this candidate: `is_langchain_trap = True` → **0.65x penalty** applied
to their final score. Not a hard filter — if they had even modest evidence
of pre-LLM substance elsewhere in their history, they'd pass through clean.
The penalty exists specifically for the "all wrapper, no substance" pattern.

---

## 3. A ghost candidate — strong on paper, not actually reachable

**`CAND_0007411`** — Senior Machine Learning Engineer @ Amazon

This candidate looks excellent by every fit metric: senior title at a
top-tier product company, 47.5-month average tenure (no job-hopping
concern), strong career relevance. But their behavioral signals tell a
different story:

- `recency_score = 0.0` — hasn't been active on the platform in 6+ months
- `response_rate = 0.12` — responds to roughly 1 in 8 recruiter messages
- `open_to_work_flag = False`

This is almost verbatim the JD's own stated test case: a candidate who's
perfect on paper but isn't actually reachable or looking. Our two-tier ghost
system catches this:

```python
is_hard_ghost = recency < 0.05 and response < 0.15 and not open_to_work
# → modifier capped at 0.55-0.70x instead of the normal 0.80-1.05x
```

This candidate triggers the **hard ghost** floor, dropping their behavioral
modifier to roughly 0.57x. Their raw fit score might be excellent, but the
multiplicative penalty meaningfully demotes them — they won't disappear
entirely (they may still be a real prospect worth a long-shot outreach), but
they won't crowd out candidates who are both strong *and* actually engageable
right now, which is what the JD explicitly asked us to prioritize.

---

## 4. A job-hopper — frequent moves, short average tenure

**`CAND_0000031`** — Recommendation Systems Engineer @ Swiggy

Four jobs, all relevant, all at recognizable product companies (Swiggy, Mad
Street Den, Uber, Zomato) — but durations of 14, 16, 27, and 13 months give
an average tenure of **17.5 months**, just under our 18-month threshold.

```python
avg_tenure_months = total_months / num_jobs
if avg_tenure_months < 18:
    job_hopper_penalty = 0.85
```

This candidate gets a **0.85x** penalty — noticeable but not severe. The JD
explicitly called out a pattern of switching companies every ~1.5 years
purely to chase title bumps (Senior → Staff → Principal) without
corresponding depth. We don't have visibility into *why* someone changed
jobs, so this stays a soft penalty rather than a disqualifier — a candidate
who's otherwise an excellent fit can still rank well, just not ahead of an
equally strong candidate with a more stable track record.

---

## 5. CV/speech background without real NLP/IR overlap

**`CAND_0000001`** — Backend Engineer @ Mindtree

Their skill list includes Diffusion Models, CNN, and Speech Recognition,
alongside some retrieval-adjacent skills (BM25, FAISS, Pinecone, RAG). The
trap check looks at the *ratio* of CV/speech/robotics-specific language
versus genuine NLP/IR overlap across their full career text:

```python
is_cv_speech_trap = cv_speech_hits >= 3 and nlp_ir_hits < 2
```

This candidate's career descriptions lean heavily on computer-vision and
audio terminology with minimal text/retrieval-specific substance, triggering
the trap at **0.70x**. This isn't a judgment that CV/speech work is less
valuable — it's specifically about whether someone applying to a
search/ranking role actually has hands-on text-retrieval experience, versus
a broadly "AI-adjacent" background that happens to share some vocabulary
(embeddings, vectors) with the JD without the underlying domain overlap.

---

## Why multiplicative, not additive

Every penalty in this system (ghost, job-hopper, langchain-trap, cv-speech-
trap, closed-source-soft, visa-blocker) is applied as a **multiplier** on
top of the base fit score, not summed or subtracted. This means:

- A candidate who's borderline on fit *and* triggers a trap gets hit hard
  (multipliers compound).
- A candidate who's exceptionally strong on fit can absorb one soft penalty
  (e.g. closed-source-senior at 0.98x) without falling out of contention —
  the penalty is proportional to how much margin they had to begin with.
- No single penalty can zero out a score on its own (the lowest individual
  multiplier is 0.55x, reserved for the visa-blocker case), which avoids the
  failure mode where one rule accidentally disqualifies a genuinely strong
  candidate based on a single signal.

This mirrors how we'd expect a thoughtful human recruiter to actually weigh
these signals — as adjustments to confidence, not binary pass/fail gates,
reserved only for the four narrow cases (honeypots, consulting-only,
non-tech, pure-research-no-production) where the data itself rules someone
out structurally.
