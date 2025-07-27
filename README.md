# Adoberound1b
Round 1B submission for Adobe “Connecting the Dots” Hackathon – Persona-Driven Document Intelligence.
# Adobe Hackathon – Round 1B: Persona-Driven Document Intelligence 🧠📄

This repository contains the implementation for *Round 1B* of Adobe’s “Connecting the Dots” Hackathon 2025. The goal is to extract and rank the most relevant sections from a collection of PDF documents, tailored to a specific user *persona* and their *job-to-be-done*.

---

## 🧩 Challenge Summary

In Round 1B, the system must act like a domain-aware assistant. Given:
- A set of related PDFs
- A defined persona (e.g., researcher, analyst)
- A specific task or goal (job-to-be-done)

Your solution must extract the most relevant sections and subsections from the documents and present them in a structured format.

---

## 🧠 What the Code Does

### ✔ Inputs:
- PDF documents (3–10 files)
- Persona: e.g., "PhD Researcher in Computational Biology"
- Job-to-be-done: e.g., "Analyze revenue trends and R&D investments"

### ✔ Process:
- Extract all document structure using the logic from Round 1A
- Match and rank headings by keyword overlap with the job-to-be-done
- Generate:
  - Metadata block
  - Ranked list of relevant sections
  - Placeholder refined subsections

### ✔ Output Format (JSON):
```json
{
  "metadata": {
    "documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "Investment Analyst",
    "job_to_be_done": "Analyze revenue trends",
    "processed_at": "2025-07-26T12:00:00Z"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page": 4,
      "section_title": "Revenue Trends 2022",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "page": 4,
      "refined_text": "Sample refined snippet"
    }
  ]
}
🏗 Folder Structure
graphql
Copy
Edit
adoberound-1B/
├── extract_1b.py              # Core logic for Round 1B
├── approach_explanation.md    # Description of methodology (300–500 words)
├── Dockerfile                 # Docker build file
├── requirements.txt           # Python dependencies
├── input/                     # Sample input PDFs
├── output/                    # JSON outputs
└── README.md                  # You're reading it
