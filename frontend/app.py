import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Interview Assistant", page_icon="🧠", layout="wide")

st.title("🧠 AI Interview Assistant")
st.caption("Upload Resume + JD → Generate questions → Answer → Get feedback + track progress")

tab1, tab2, tab3, tab4 = st.tabs(["Upload", "Interview", "Evaluate", "Dashboard"])

# ----------------------------
# TAB 1: Upload
# ----------------------------
with tab1:
    st.subheader("Upload Resume & Job Description")
    c1, c2 = st.columns(2)

    if "resume_uploaded" not in st.session_state:
        st.session_state["resume_uploaded"] = False
    if "jd_uploaded" not in st.session_state:
        st.session_state["jd_uploaded"] = False

    with c1:
        resume = st.file_uploader("Resume (PDF)", type=["pdf"])
        if st.button("Upload Resume") and resume:
            r = requests.post(f"{API}/upload/resume", files={"file": resume.getvalue()})
            if r.status_code != 200:
                st.error(f"Upload failed ({r.status_code})")
                st.text(r.text)
            else:
                resp = r.json()
                st.session_state["resume_uploaded"] = True
                st.success("✅ Resume uploaded successfully!")
                st.caption(f"File: **{resume.name}**  |  Pages: **{resp.get('pages', '-') }**")

    with c2:
        jd = st.file_uploader("Job Description (PDF)", type=["pdf"])
        if st.button("Upload JD") and jd:
            r = requests.post(f"{API}/upload/jd", files={"file": jd.getvalue()})
            if r.status_code != 200:
                st.error(f"Upload failed ({r.status_code})")
                st.text(r.text)
            else:
                resp = r.json()
                st.session_state["jd_uploaded"] = True
                st.success("✅ Job Description uploaded successfully!")
                st.caption(f"File: **{jd.name}**  |  Pages: **{resp.get('pages', '-') }**")

    if st.session_state["resume_uploaded"] and st.session_state["jd_uploaded"]:
        st.info("✅ Upload complete. Go to the **Interview** tab to generate questions.")
    elif st.session_state["resume_uploaded"] or st.session_state["jd_uploaded"]:
        st.warning("⚠️ Upload the remaining document to get the best interview questions.")

# ----------------------------
# TAB 2: Generate Questions
# ----------------------------
with tab2:
    st.subheader("Generate interview questions")
    role = st.text_input("Role", value="")
    company = st.text_input("Company (optional)", value="")

    if st.button("Generate Questions"):
        payload = {"role": role, "company": company, "num_questions": 10}
        r = requests.post(f"{API}/interview/generate", json=payload)

        if r.status_code != 200:
            st.error(f"Backend error: {r.status_code}")
            st.text(r.text)
            st.stop()

        try:
            data = r.json()
        except Exception:
            st.error("Backend did not return JSON")
            st.text(r.text)
            st.stop()

        st.session_state["questions"] = data.get("questions", [])

    questions = st.session_state.get("questions", [])
    if questions:
        for i, q in enumerate(questions, 1):
            st.write(f"**{i}.** {q['question']}")

# ----------------------------
# TAB 3: Evaluate Answers
# ----------------------------
with tab3:
    st.subheader("Answer + score")
    role2 = st.text_input("Role (for scoring)", value="", key="role2")
    company2 = st.text_input("Company (optional)", value="", key="company2")

    q_text = st.text_area("Question", height=80, value="")
    ans = st.text_area("Your Answer", height=160, value="")

    if st.button("Score Answer"):
        payload = {"role": role2, "company": company2, "question": q_text, "answer": ans}
        r = requests.post(f"{API}/evaluation/score", json=payload)

        if r.status_code != 200:
            st.error(f"Backend error: {r.status_code}")
            st.text(r.text)
            st.stop()

        try:
            out = r.json()
        except Exception:
            st.error("Backend did not return JSON")
            st.text(r.text)
            st.stop()

        st.metric("Total Score", out.get("total_score", 0))
        st.write("### Breakdown")
        st.json(out.get("breakdown", {}))

        st.write("### Strengths")
        st.write("\n".join([f"- {s}" for s in out.get("strengths", [])]))

        st.write("### Improvements")
        st.write("\n".join([f"- {s}" for s in out.get("improvements", [])]))

        st.write("### Improved Answer")
        st.write(out.get("improved_answer", ""))

# ----------------------------
# TAB 4: Dashboard (Professional + Safe + NO JSON)
# ----------------------------
with tab4:
    st.subheader("📊 Interview Performance Dashboard")

    def safe_get(url: str):
        try:
            return requests.get(url, timeout=10)
        except requests.exceptions.RequestException:
            st.error("❌ Backend is not running.")
            st.caption("Start FastAPI first: `python -m uvicorn app.main:app --reload --port 8000`")
            st.stop()

    # ---- Summary ----
    r_summary = safe_get(f"{API}/analytics/summary")
    if r_summary.status_code != 200:
        st.error(f"Failed to load summary ({r_summary.status_code})")
        st.stop()

    try:
        summary = r_summary.json()
    except Exception:
        st.error("Summary endpoint did not return JSON")
        st.stop()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Attempts", summary.get("total_attempts", 0))
    c2.metric("Average Score", summary.get("average_score", 0))
    c3.metric("Best Score", summary.get("best_score", 0))
    c4.metric("Latest Score", summary.get("latest_score", 0))

    st.divider()

    # ---- History ----
    r_hist = safe_get(f"{API}/analytics/history?limit=20")
    if r_hist.status_code != 200:
        st.error(f"Failed to load history ({r_hist.status_code})")
        st.stop()

    try:
        history_data = r_hist.json()
    except Exception:
        st.error("History endpoint did not return JSON")
        st.stop()

    # ✅ Accept {"items": []}, {"history": []}, or []
    if isinstance(history_data, dict):
        if "items" in history_data:
            history = history_data["items"]
        elif "history" in history_data:
            history = history_data["history"]
        else:
            history = []
    elif isinstance(history_data, list):
        history = history_data
    else:
        history = []

    # ✅ If no attempts, show friendly message ONLY
    if not history:
        st.info("📭 No interview attempts yet. Start practicing to see progress here.")
        st.stop()

    history = [h for h in history if isinstance(h, dict)]

    # ---- Chart ----
    st.subheader("📈 Score Progress")
    scores = [h.get("total_score", 0) for h in history]
    st.line_chart({"Score": scores})

    st.divider()

    # ---- Table ----
    st.subheader("📝 Recent Attempts")
    table_data = [
        {
            "Date": (h.get("created_at", "")[:10] if h.get("created_at") else ""),
            "Role": h.get("role", ""),
            "Company": h.get("company", ""),
            "Score": h.get("total_score", 0),
        }
        for h in history
    ]
    st.dataframe(table_data, use_container_width=True, hide_index=True)