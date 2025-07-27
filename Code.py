# ✅ 1️⃣ Install all needed packages (force reinstall)
!pip install pdfminer.six -q
!pip install streamlit -q
!npm install -g localtunnel
!pip install PyPDF2
# ✅ 2️⃣ See IP (optional)
!wget -q -O - ipv4.icanhazip.com
!streamlit run app.py & npx localtunnel --port 8501

#app.y file code 
import streamlit as st
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextLineHorizontal
import re, json, tempfile
from datetime import datetime
import pandas as pd

# -------------- Text Extraction Helpers --------------

def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

def is_bold(tl):
    bold_count = sum(1 for c in tl if isinstance(c, LTChar) and 'Bold' in c.fontname)
    total_count = sum(1 for c in tl if isinstance(c, LTChar))
    return bold_count / total_count >= 0.5 if total_count else False

def is_numbered(text):
    return bool(re.match(r'^(\d+(\.\d+)*|[A-Z]\.)', text.strip()))

def is_all_caps(text):
    s = text.strip()
    return s.isupper() and len(s) > 3

# -------------- Challenge 1A Extraction --------------

def extract_1a(pdf_path):
    blocks = []
    for page_layout in extract_pages(pdf_path):
        lines = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for tl in element:
                    if isinstance(tl, LTTextLineHorizontal):
                        text = clean_text(tl.get_text())
                        if len(text) < 2:
                            continue
                        sizes = [c.size for c in tl if isinstance(c, LTChar)]
                        if not sizes:
                            continue
                        avg_size = sum(sizes) / len(sizes)
                        lines.append({
                            'text': text,
                            'size': avg_size,
                            'y0': tl.y0,
                            'page': page_layout.pageid,
                            'bold': is_bold(tl),
                            'numbered': is_numbered(text),
                            'all_caps': is_all_caps(text)
                        })
        lines = sorted(lines, key=lambda l: -l['y0'])
        merged = []
        if lines:
            current = lines[0]
            for l in lines[1:]:
                if abs(current['y0'] - l['y0']) < 5 and abs(current['size'] - l['size']) < 1:
                    current['text'] += ' ' + l['text']
                else:
                    merged.append(current)
                    current = l
            merged.append(current)
        blocks.extend(merged)

    seen = set()
    unique = []
    for b in blocks:
        if b['text'] not in seen:
            seen.add(b['text'])
            unique.append(b)

    title_candidates = [b for b in unique if b['page'] == 1]
    title = max(title_candidates, key=lambda x: x['size'])['text'] if title_candidates else max(unique, key=lambda x: x['size'])['text']
    content = [b for b in unique if b['text'] != title]

    max_size = max([b['size'] for b in content]) if content else 0
    outline = []
    for b in content:
        score = 0
        ratio = b['size'] / max_size if max_size else 0
        score += 2 if ratio >= 0.85 else 1 if ratio >= 0.65 else 0
        score += int(b['bold']) + int(b['numbered']) + int(b['all_caps'])
        level = 'H1' if score >= 4 else 'H2' if score == 3 else 'H3'
        outline.append({'level': level, 'text': b['text'], 'page': b['page']})

    return {'title': title, 'outline': outline}

# -------------- Challenge 1B Extraction --------------

def extract_1b(pdf_path, display_name, persona, job_to_be_done):
    base = extract_1a(pdf_path)
    metadata = {
        "documents": [display_name],
        "persona": persona,
        "job_to_be_done": job_to_be_done,
        "processed_at": datetime.utcnow().isoformat() + "Z"
    }

    keywords = [kw.lower() for kw in re.findall(r'\w+', job_to_be_done)]

    matched_sections = []
    for section in base['outline']:
        score = sum(1 for kw in keywords if kw in section['text'].lower())
        if score > 0:
            matched_sections.append({
                "document": display_name,
                "page": section["page"],
                "section_title": section["text"],
                "score": score
            })

    ranked_sections = sorted(matched_sections, key=lambda x: -x["score"])
    for i, sec in enumerate(ranked_sections):
        sec["importance_rank"] = i + 1

    subsections = [
        {"document": s["document"], "page": s["page"], "refined_text": "Sample refined snippet"}
        for s in ranked_sections
    ]

    return {
        "metadata": metadata,
        "extracted_sections": ranked_sections,
        "subsection_analysis": subsections
    }

# -------------- Streamlit App UI --------------

st.set_page_config(page_title="Adobe Hackathon PDF Processor")
st.title("📄 Adobe Hackathon PDF Processor")

st.sidebar.title("Configuration")
max_pages = st.sidebar.number_input("Max pages per PDF", min_value=1, max_value=200, value=50)
max_size = st.sidebar.number_input("Max file size (MB)", min_value=1, max_value=200, value=50)

challenge = st.selectbox("Select Challenge", [
    "Challenge 1A: PDF Title & Heading Extraction",
    "Challenge 1B: Persona-Driven Document Intelligence"
])

if challenge.startswith("Challenge 1B"):
    persona = st.selectbox("Persona", ["PhD Researcher", "Legal Analyst", "Medical Reviewer", "Food Contractor", "Investment Analyst"])
    job_to_be_done = st.text_input("Job to be Done", value="Analyze revenue trends, R&D investments, and market positioning strategies")

st.markdown("### 📂 Upload PDF File")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

st.markdown("### 🧩 Expected Output Schema")
if challenge.startswith("Challenge 1A"):
    st.json({
        "title": "Document Title",
        "outline": [{"level": "H1", "text": "Heading Text", "page": 1}]
    })
else:
    st.json({
        "metadata": {
            "documents": ["input.pdf"],
            "persona": "Investment Analyst",
            "job_to_be_done": "Analyze revenue trends, R&D investments, and market positioning strategies",
            "processed_at": "..."
        },
        "extracted_sections": [{"document": "input.pdf", "page": 1, "section_title": "...", "importance_rank": 1}],
        "subsection_analysis": [{"document": "input.pdf", "page": 1, "refined_text": "..."}]
    })

if uploaded_file:
    if uploaded_file.size > max_size * 1024 * 1024:
        st.error(f"❌ File size exceeds {max_size}MB. Please upload a smaller file.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        with st.spinner("🔍 Processing PDF..."):
            if challenge.startswith("Challenge 1A"):
                result = extract_1a(tmp_path)
                filename = "round1a_output.json"
            else:
                result = extract_1b(tmp_path, uploaded_file.name, persona, job_to_be_done)
                filename = "round1b_output.json"

        st.success("✅ Extraction complete!")

        if challenge.startswith("Challenge 1A"):
            st.subheader("📘 Extracted Title")
            st.markdown(f"**{result['title']}**")

            st.subheader("🧭 Document Outline")
            outline_df = pd.DataFrame(result["outline"])
            st.dataframe(outline_df)

        else:
            st.subheader("📎 Metadata")
            readable_time = datetime.fromisoformat(result["metadata"]["processed_at"].replace("Z", "")).strftime("%Y-%m-%d %H:%M:%S")
            st.markdown(f"- **Persona**: {result['metadata']['persona']}")
            st.markdown(f"- **Job to be Done**: {result['metadata']['job_to_be_done']}")
            st.markdown(f"- **Processed at**: {readable_time}")

            st.subheader("📊 Top Extracted Sections")
            st.dataframe(pd.DataFrame(result["extracted_sections"]))

            st.subheader("📝 Refined Subsections")
            for s in result["subsection_analysis"]:
                with st.expander(f"{s['document']} - Page {s['page']}"):
                    st.markdown(s['refined_text'])

        with st.expander("🧾 Full JSON Output"):
            st.json(result)

        st.download_button(
            label=f"📥 Download {filename}",
            data=json.dumps(result, indent=2),
            file_name=filename,
            mime="application/json"
        )
