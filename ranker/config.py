"""All weights, thresholds, skill taxonomy, and constants."""

from datetime import date

REFERENCE_DATE = date(2026, 6, 14)

# --- Skill Taxonomy ---

MUST_HAVE_SKILLS = {
    "Sentence Transformers", "Embeddings", "FAISS", "Pinecone", "Weaviate",
    "Qdrant", "Milvus", "Vector Search", "RAG", "Information Retrieval",
    "Semantic Search", "pgvector", "OpenSearch", "Elasticsearch", "BM25",
    "Recommendation Systems", "Learning to Rank",
}

STRONG_SIGNAL_SKILLS = {
    "LLMs", "Fine-tuning LLMs", "NLP", "Deep Learning", "PyTorch",
    "TensorFlow", "Hugging Face Transformers", "LangChain", "LlamaIndex",
    "LoRA", "QLoRA", "PEFT", "scikit-learn", "MLOps", "MLflow", "BentoML",
    "Machine Learning", "Haystack", "Prompt Engineering", "Weights & Biases",
    "Kubeflow", "Feature Engineering",
}

SUPPORTING_SKILLS = {
    "Python", "Docker", "Kubernetes", "FastAPI", "Flask", "Django",
    "REST APIs", "gRPC", "Microservices", "CI/CD", "AWS", "GCP", "Azure",
    "Kafka", "Redis", "PostgreSQL", "MongoDB", "Spark", "Data Pipelines",
    "Airflow", "Terraform", "Go", "Rust", "Databricks", "BigQuery",
    "Snowflake", "dbt",
}

SYNONYM_GROUPS = {
    "vector_db": {"FAISS", "Pinecone", "Weaviate", "Qdrant", "Milvus", "pgvector", "OpenSearch", "Elasticsearch"},
    "embeddings": {"Embeddings", "Sentence Transformers", "Vector Search"},
    "retrieval": {"Information Retrieval", "Semantic Search", "RAG", "BM25"},
    "ranking": {"Learning to Rank", "Recommendation Systems"},
    "llm_finetuning": {"Fine-tuning LLMs", "LoRA", "QLoRA", "PEFT"},
    "ml_frameworks": {"PyTorch", "TensorFlow", "scikit-learn", "Hugging Face Transformers"},
    "mlops": {"MLOps", "MLflow", "BentoML", "Kubeflow", "Weights & Biases"},
    "nlp": {"NLP", "LLMs", "LangChain", "LlamaIndex", "Haystack", "Prompt Engineering"},
}

PROFICIENCY_WEIGHTS = {
    "beginner": 0.2,
    "intermediate": 0.5,
    "advanced": 0.8,
    "expert": 1.0,
}

# --- Title Relevance Mapping ---

TITLE_SCORES = {
    # Tier 1.0 — direct match
    "Senior AI Engineer": 1.0, "Lead AI Engineer": 1.0, "AI Engineer": 1.0,
    "NLP Engineer": 1.0, "Senior NLP Engineer": 1.0, "Search Engineer": 1.0,
    "Applied Scientist": 1.0, "Senior Applied Scientist": 1.0,
    "Staff Machine Learning Engineer": 1.0,
    # Tier 0.9
    "ML Engineer": 0.9, "Machine Learning Engineer": 0.9,
    "Senior Machine Learning Engineer": 0.9, "Junior ML Engineer": 0.9,
    "AI Research Engineer": 0.9, "AI Specialist": 0.9,
    # Tier 0.8
    "Data Scientist": 0.8, "Senior Data Scientist": 0.8,
    "Applied ML Engineer": 0.8,
    # Tier 0.6
    "Data Engineer": 0.6, "Senior Data Engineer": 0.6,
    "Analytics Engineer": 0.6, "Data Analyst": 0.6,
    # Tier 0.5
    "Backend Engineer": 0.5, "Senior Software Engineer": 0.5,
    "Software Engineer": 0.5, "Full Stack Developer": 0.5,
    # Tier 0.3
    "Cloud Engineer": 0.3, "DevOps Engineer": 0.3,
    "Computer Vision Engineer": 0.3,
    # Tier 0.15
    "Java Developer": 0.15, ".NET Developer": 0.15, "Mobile Developer": 0.15,
    "Frontend Engineer": 0.15, "QA Engineer": 0.15,
}

NON_TECH_TITLES = {
    "HR Manager", "Marketing Manager", "Sales Manager", "Accountant",
    "Content Writer", "Graphic Designer", "Customer Support",
    "Operations Manager", "Civil Engineer", "Mechanical Engineer",
    "Business Analyst", "Product Manager", "Project Manager",
    "Recruiter", "Admin", "Executive Assistant",
}

# --- Consulting Firms (disqualifier if career is entirely here) ---

CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "hcl", "hcl technologies", "mindtree", "tech mahindra", "mphasis",
    "l&t infotech", "ltimindtree",
}

# --- Location Scoring ---

IDEAL_LOCATIONS = {"pune", "noida"}
TIER1_INDIA_CITIES = {
    "delhi", "new delhi", "delhi ncr", "gurgaon", "gurugram",
    "hyderabad", "mumbai", "bangalore", "bengaluru", "chennai", "kolkata",
}

# --- Scoring Weights ---

FIT_WEIGHTS = {
    "skills": 0.30,
    "career": 0.25,
    "title": 0.15,
    "semantic": 0.10,
    "yoe": 0.10,
    "location": 0.05,
    "education": 0.05,
}

SKILLS_SUB_WEIGHTS = {
    "must_have": 0.50,
    "strong_signal": 0.30,
    "python": 0.10,
    "trust": 0.10,
}

BEHAVIORAL_WEIGHTS = {
    "availability": 0.50,
    "quality": 0.30,
    "notice_period": 0.20,
}

AVAILABILITY_SUB_WEIGHTS = {
    "open_to_work": 0.20,
    "response_rate": 0.30,
    "response_time": 0.15,
    "recency": 0.20,
    "interview_completion": 0.15,
}

# --- Career Text Keywords ---

RETRIEVAL_KEYWORDS = [
    "embedding", "vector", "retrieval", "search", "faiss", "pinecone",
    "rag", "semantic", "ranking", "recommendation", "rerank", "ndcg",
    "mrr", "recall", "bm25", "index", "query", "relevance",
]

ML_KEYWORDS = [
    "transformer", "bert", "fine-tun", "llm", "deep learning",
    "machine learning", "nlp", "natural language", "neural",
    "model", "inference", "training", "pytorch", "tensorflow",
]

PRODUCTION_KEYWORDS = [
    "production", "deployed", "serving", "scale", "user",
    "real-time", "latency", "sla", "pipeline", "monitoring",
    "a/b test", "million", "throughput",
]

EVAL_KEYWORDS = [
    "ndcg", "mrr", "map", "precision", "recall", "f1",
    "evaluation", "metric", "benchmark", "a/b test", "ablation",
]

# --- Experience ---

YOE_IDEAL = 7.0
YOE_SIGMA = 2.0

# --- Education ---

EDUCATION_TIER_SCORES = {
    "tier_1": 1.0,
    "tier_2": 0.75,
    "tier_3": 0.50,
    "tier_4": 0.30,
    "unknown": 0.40,
}

CS_AI_FIELDS = {
    "computer science", "artificial intelligence", "machine learning",
    "data science", "mathematics", "statistics", "information technology",
    "electronics", "electrical engineering", "ece",
    "electronics and communication", "computer engineering",
}

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
