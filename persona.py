# Local persona classification using sentence-transformers and cosine similarity
from sentence_transformers import SentenceTransformer
import numpy as np

ALLOWED_PERSONAS = [
    "Technical Expert",
    "Frustrated User",
    "Business Executive"
]

PERSONA_EXAMPLES = {
    "Technical Expert": [
        "Can you provide detailed API authentication documentation?",
        "How do I set up webhooks for integration?",
        "What are the API rate limits and error codes?",
        "Explain the OAuth2 authentication flow.",
        "How do I troubleshoot API connection issues?",
        "Where can I find SDKs for your API?",
        "Is there a sandbox environment for API testing?"
    ],
    "Frustrated User": [
        "This dashboard never works. I am tired of this.",
        "I keep getting errors and nothing is loading.",
        "Your product is useless and I want my money back.",
        "Why does it always fail when I try to login?",
        "I'm really frustrated with the constant bugs.",
        "Support never helps and my issue is unresolved.",
        "I am angry about the poor service."
    ],
    "Business Executive": [
        "What’s the ROI impact of your analytics solution?",
        "How does your platform improve business outcomes?",
        "Can you summarize the value proposition for executives?",
        "What are the strategic benefits of your product?",
        "How does campaign analytics impact revenue growth?",
        "Is there a case study on business performance?",
        "How can your solution help us scale operations?"
    ]
}

_model = SentenceTransformer('all-MiniLM-L6-v2')

# Precompute embeddings for all examples
_persona_embeddings = {
    persona: np.array([_model.encode(example) for example in examples])
    for persona, examples in PERSONA_EXAMPLES.items()
}

def detect_persona(query: str) -> tuple[str, float]:
    query_emb = _model.encode(query)
    persona_scores = {}
    for persona, example_embs in _persona_embeddings.items():
        # Compute cosine similarity for each example
        sims = np.dot(example_embs, query_emb) / (
            np.linalg.norm(example_embs, axis=1) * np.linalg.norm(query_emb) + 1e-8
        )
        avg_sim = float(np.mean(sims))
        persona_scores[persona] = avg_sim
    # Select persona with highest average similarity
    predicted_persona = max(persona_scores, key=persona_scores.get)
    confidence = persona_scores[predicted_persona]
    return predicted_persona, confidence
