# 🚀 BrewBuddy: The Hyper-Personalized Customer Experience Automation (H-002)

> **Tagline:** A real-time AI agent that understands customer history, store proximity, inventory, and internal documents to generate highly specific, actionable responses—just like a trained store associate, but faster.

---

## 1. The Problem (Real-World Scenario)

**Context:**  
Retail customers today expect instant, accurate responses.  
Typical questions look like:

- “Is this store open right now?”
- “Do you have Hot Cocoa available?”
- “Where is the nearest branch?”
- “Do you have size 10 in stock?”

Most chatbots fail because they:
- Give generic templated answers  
- Ignore customer’s history  
- Don’t use location intelligence  
- Don’t check real-time stock  
- Cannot read internal documents (PDFs, policy manuals)  

**The Pain Point:**  
Someone standing outside a coffee shop might receive the useless reply:  
> “Please visit our website for more details.”

This leads to frustration and lost business.

**My Solution:**  
I built **BrewBuddy**, a hyper-personalized AI assistant that:
- Understands **vague inputs** (“I am cold”)  
- Uses **real Starbucks store locations** from a Kaggle dataset  
- Computes **exact distance** to the nearest store  
- Checks **product availability** dynamically  
- Reads **customer purchase history**  
- Uses a **RAG pipeline** to fetch information from internal documents  
- Applies **PII masking** before calling LLMs  
- Generates a short, helpful, fully contextual answer like:

> “You’re 48m away from Starbucks Pike Street. Hot Cocoa is in stock and you have a 10% winter coupon—want me to reserve one?”

---

## 2. Expected End Result

**For the User:**

### Input  
A natural language message + optional location

Example:
> “I am cold.”

### What Happens Internally  
The system:
- Locates the closest Starbucks store  
- Computes distance using the Haversine formula  
- Checks if Hot Cocoa (or relevant warm beverages) are in stock  
- Retrieves offers using RAG  
- Pulls the user’s history (favorite drink, last order)  
- Masks any PII  
- Builds a structured context packet  
- Generates the final reply through an LLM  

### Output (Actual System Response)

```json
{
  "answer": "It’s chilly outside! Starbucks Pike Street is 48m away. Hot Cocoa is available and your 10% winter coupon is active. Want me to reserve one?",
  "sources": ["offer_o100", "store_100"],
  "distance_m": 48
}
```

This output is short, friendly, specific, and fully data-grounded.

---

## 3. Technical Approach

My goal was to build something that resembles a **production-ready customer experience engine**, not a simple chatbot script.

### System Architecture Overview

1. **Data Ingestion**
   - Real Starbucks store locations from Kaggle  
   - Customer profiles (mock purchase history)  
   - Product inventory (per store)  
   - Seasonal offers + internal policy documents (PDF)

2. **Privacy / PII Redaction**
   - Emails → `[REDACTED_EMAIL]`  
   - Phone numbers → `[REDACTED_PHONE]`  
   - Card numbers → `[REDACTED_CARD]`  
   - No raw PII ever reaches the LLM.

3. **Context Engine**
   - Computes nearest store using geospatial math  
   - Calculates distance and estimated walking time  
   - Fetches that store’s inventory  
   - Identifies user preferences based on purchase history  
   - Filters offers based on product relevance + proximity  

4. **RAG Pipeline**
   - Internal PDF is parsed using `pdfplumber`  
   - Document is semantically chunked  
   - Embeddings generated via `sentence-transformers` (MiniLM)  
   - Stored in a **FAISS** vector index  
   - Relevant chunks retrieved based on the query  

5. **Generative LLM Layer**
   - Uses GPT-4o with a strict guardrail prompt  
   - Only allowed to use provided context  
   - Generates a <40-word, actionable response  
   - Cites source documents when appropriate  

6. **Output Validation**
   - Ensures accuracy of store distance, product availability, and offers  
   - Rejects hallucinated claims  
   - Final response is factual, actionable, and safe  

---

## 4. Tech Stack

- **Python 3.11**
- **FastAPI** (REST API backend)
- **FAISS** (vector DB)
- **Sentence Transformers** (`MiniLM-L6-v2`)
- **Pandas**
- **pdfplumber**
- **OpenAI GPT-4o** (masked context only)
- **Haversine Formula** for geolocation
- **Kaggle Starbucks Store Locations Dataset**

---

## 5. Challenges & Learnings

### Challenge 1 — Understanding Vague Inputs  
Some queries do not specify intent (“I am cold”).  
I needed to blend:
- weather inference  
- proximity  
- product mapping (“warm drinks”)  
- user preferences  

### Challenge 2 — PII Masking  
LLMs should never receive PII.  
I implemented a regex-based redaction module to wipe emails, phone numbers, and credit card patterns.

### Challenge 3 — RAG Relevance  
Raw PDF text produced noisy results.  
Semantic chunking + metadata filtering improved accuracy drastically.

---

## 6. Visual Proof

(You can replace these placeholders with screenshots)

- **Context Packet** (pre-LLM)  
- **RAG Retrieved Snippets**  
- **Final AI Response**  

---

## 7. How to Run

```bash
# 1. Clone the repo
git clone https://github.com/Sruthi1302/GTHakathon-SRUTHI.git
cd GTHakathon-SRUTHI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your LLM API key
export OPENAI_API_KEY="your_api_key_here"

# 4. Start the server
uvicorn app.main:app --reload --port 8000

# 5. Test request
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
        "user_id":"cust_001",
        "message":"I am cold",
        "location":{"lat":47.6097,"lon":-122.3425}
      }'
```

---

## 8. Output (Actual Example)

```json
{
  "answer": "It’s chilly outside! Starbucks Pike Street is 48m away. Hot Cocoa is in stock and you have a 10% winter coupon.",
  "sources": ["offer_o100", "store_100"],
  "distance_m": 48
}
```

---

## 9. Dataset Used

### Primary Dataset (Real Kaggle Dataset)
**Starbucks Store Locations Worldwide**  
Contains:
- 25K+ Starbucks branches  
- Real GPS coordinates  
- City, country, ownership type  

Used to compute:
- nearest store  
- distance  
- availability radius  

### Additional Supporting Datasets (Mock)
- `customers.csv` (user purchase history)
- `inventory.csv` (store-level stock)
- `offers.csv` (discounts, seasonal campaigns)
- `starbucks_offers.pdf` (internal doc for RAG)

---

## ⭐ Final Summary

BrewBuddy is a fully functional, production-style customer experience engine that combines:
- **location intelligence**,  
- **RAG**,  
- **LLM reasoning**,  
- **user personalization**,  
- **PII masking**,  
- **real-world datasets**, and  
- **structured output validation**  

to deliver actionable, human-like responses to real customer queries—exactly what the H-002 problem statement calls for.

