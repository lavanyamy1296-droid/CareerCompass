import streamlit as st
from analyzer import extract_text, analyze

st.set_page_config(page_title="CareerCompass AI", page_icon="🧭", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1180px;}
.hero {padding: 1.5rem 1.7rem; border: 1px solid rgba(128,128,128,.25); border-radius: 18px; margin-bottom: 1.2rem;}
.hero h1 {margin: 0 0 .35rem 0; font-size: 2.35rem;}
.muted {opacity: .72;}
.pill {display:inline-block; padding:.3rem .65rem; border-radius:20px; border:1px solid rgba(128,128,128,.35); margin:.15rem .2rem .15rem 0; font-size:.88rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="muted">AI-POWERED CAREER TOOLKIT</div>
  <h1>🧭 CareerCompass AI</h1>
  <div class="muted">Understand how your resume aligns with a target role — with transparent, practical feedback.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("About this tool")
    st.write("CareerCompass compares resume text with a job description using TF-IDF similarity and a curated skill vocabulary.")
    st.caption("It is an educational aid, not an official ATS, hiring decision, or guarantee of selection.")
    st.divider()
    st.write("**Supported files**")
    st.write("PDF · DOCX · TXT")

left, right = st.columns([1, 1])
with left:
    st.subheader("1. Upload your resume")
    resume_file = st.file_uploader("Choose a resume file", type=["pdf", "docx", "txt"])
    st.caption("Tip: text-based PDFs work best. Scanned PDFs need OCR, which is not included.")
with right:
    st.subheader("2. Add the target job")
    job_text = st.text_area("Paste the complete job description", height=220, placeholder="Paste the role, responsibilities, requirements and skills here...")

if st.button("✨ Analyze my match", type="primary", use_container_width=True):
    if not resume_file:
        st.error("Please upload a resume first.")
    elif not job_text.strip():
        st.error("Please paste a job description first.")
    else:
        try:
            with st.spinner("Reading your resume and comparing role requirements..."):
                resume_text = extract_text(resume_file)
                if len(resume_text.strip()) < 40:
                    st.error("Very little text could be extracted. Try a text-based PDF, DOCX, or TXT file.")
                else:
                    result = analyze(resume_text, job_text)
                    st.session_state["analysis"] = result
                    st.session_state["resume_text"] = resume_text
                    st.session_state["job_text"] = job_text
        except Exception as exc:
            st.error(f"Could not read this file: {exc}")

if "analysis" in st.session_state:
    r = st.session_state["analysis"]
    st.divider()
    st.subheader("3. Your match overview")
    a, b, c, d = st.columns(4)
    a.metric("Text similarity", f'{r["score"]}%')
    b.metric("Resume words", f'{r["word_count"]:,}')
    c.metric("Skills matched", len(r["matched_skills"]))
    d.metric("Skills to review", len(r["missing_skills"]))
    st.progress(min(max(r["score"] / 100, 0.0), 1.0))
    st.caption(f'Method: {r["method"]}. Similarity is a text-overlap signal, not a hiring probability.')

    x, y = st.columns(2)
    with x:
        st.markdown("#### ✅ Skills found in both")
        if r["matched_skills"]:
            st.markdown("".join(f'<span class="pill">{s}</span>' for s in r["matched_skills"]), unsafe_allow_html=True)
        else:
            st.info("No skills from the built-in vocabulary were found in both texts.")
    with y:
        st.markdown("#### 🔎 Job skills not found in resume")
        if r["missing_skills"]:
            st.markdown("".join(f'<span class="pill">{s}</span>' for s in r["missing_skills"]), unsafe_allow_html=True)
        else:
            st.success("No gaps detected in the built-in skill vocabulary.")

    st.markdown("#### 🧩 Other job keywords to review")
    if r["keyword_gaps"]:
        st.write(", ".join(r["keyword_gaps"]))
    else:
        st.write("No obvious keyword gaps detected.")

    st.markdown("#### 💡 Suggested improvements")
    for item in r["suggestions"]:
        st.write(f"• {item}")

    report = [
        "# CareerCompass AI — Resume Match Report", "",
        f"- Text similarity: {r['score']}%",
        f"- Method: {r['method']}",
        f"- Resume word count: {r['word_count']}",
        f"- Skills matched: {', '.join(r['matched_skills']) or 'None detected'}",
        f"- Job skills not found: {', '.join(r['missing_skills']) or 'None detected'}",
        f"- Other keywords to review: {', '.join(r['keyword_gaps']) or 'None detected'}",
        "", "## Suggestions", *[f"- {s}" for s in r["suggestions"]],
        "", "> This report is a heuristic text analysis, not an official ATS score or hiring decision."
    ]
    st.download_button("⬇️ Download analysis report", "\n".join(report), file_name="careercompass_analysis.md", mime="text/markdown", use_container_width=True)

st.divider()
st.caption("🔒 Local-first demo: uploaded resume text is processed in the current app session and is not intentionally written to disk. Avoid using confidential resumes on public deployments.")
