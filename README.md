# Persona-Adaptive Customer Support Agent

**AI Intern Assignment – Adsparkx Media**

---

## 1. Overview

This project implements a **Persona-Adaptive Customer Support Agent** capable of:

* Detecting customer persona (Technical Expert, Frustrated User, Business Executive)
* Retrieving relevant knowledge base content using semantic search
* Dynamically adapting response tone and structure
* Escalating complex or sensitive cases to a human agent
* Providing structured context handoff during escalation

The system is built with modularity, clarity, and extensibility in mind.

---

## 2. System Architecture

### Backend Framework

* **FastAPI** – lightweight, production-ready, async-compatible

### LLM Provider

* **OpenRouter API** (with offline fallback mode)

### Embeddings

* **SentenceTransformers (all-MiniLM-L6-v2)**

### Vector Search

* **FAISS (in-memory index)**

### Knowledge Base

* Text-based documentation files chunked and embedded at startup

---

## 3. How the System Works (Step-by-Step Flow)

### Step 1 – User Query Received

A POST request is sent to `/chat` endpoint:

```json
{
  "message": "How does your analytics solution impact revenue growth?"
}
```

---

### Step 2 – Persona Detection

The system:

* Uses embedding-based classification
* Compares query embedding against multiple examples per persona
* Computes average cosine similarity per persona
* Returns:

  * Predicted persona
  * Confidence score

This avoids LLM latency and ensures deterministic, fast classification.

---

### Step 3 – Knowledge Retrieval

At startup:

* KB files are loaded
* Chunked into manageable segments
* Embedded using SentenceTransformers
* Indexed into FAISS

At runtime:

* Query embedding is computed
* Top-k semantically similar chunks are retrieved
* Retrieved sources are tracked for transparency

---

### Step 4 – Persona-Conditioned Response Generation

The system modifies response structure based on persona:

| Persona            | Response Style                            |
| ------------------ | ----------------------------------------- |
| Technical Expert   | Structured steps, technical terminology   |
| Frustrated User    | Empathetic tone + short clear steps       |
| Business Executive | Concise summary + business impact bullets |

Prompt structure includes:

* SYSTEM instructions
* RETRIEVED KNOWLEDGE
* USER QUESTION
* Strict formatting instructions

---

### Step 5 – Intelligent Escalation

The system uses a **three-tier escalation strategy**:

1. Immediate escalation

   * Legal threats
   * Refund demands
   * Explicit human request

2. Conditional escalation

   * Frustrated persona
   * Multiple negative indicators
   * Long complaint-style message

3. Failure-aware escalation

   * If knowledge confidence is low
   * And persona indicates high frustration

When escalation is triggered:

* A structured handoff packet is created
* Includes persona, reason, context, and summary

---

## 4. Why This Architecture?

### Why Embedding-Based Persona Detection?

* Low latency
* No additional API cost
* Deterministic behavior
* Easy to extend with more examples

### Why FAISS?

* Efficient semantic retrieval
* Lightweight
* Ideal for small-to-medium KBs
* Thread-safe for read-only operations

### Why Modular Design?

Each component is isolated:

* persona.py
* retriever.py
* generator.py
* escalation.py
* main.py

This makes the system:

* Easy to test
* Easy to extend
* Production adaptable

---

## 5. API Response Structure

Normal response:

```json
{
  "persona": "Business Executive",
  "confidence": 0.52,
  "escalation": false,
  "response": "...",
  "retrieved_sources": [...]
}
```

Escalated response:

```json
{
  "persona": "Frustrated User",
  "confidence": 0.15,
  "escalation": true,
  "handoff_packet": {
      "persona": "...",
      "reason": "...",
      "user_query": "...",
      "retrieved_context": [...],
      "summary": "..."
