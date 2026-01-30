import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="AI Interview Assistant", page_icon="🧠", layout="wide")

# ----------------------------
# Helpers (Safe requests)
# ----------------------------
def safe_get(url: str, **kwargs):
    try:
        return requests.get(url, timeout=10, **kwargs)
    except requests.exceptions.RequestException as e:
        st.error("❌ Backend is not running or not reachable.")
        st.caption("Start FastAPI first: `python -m uvicorn app.main:app --reload --port 8000`")
        st.text(str(e))
        st.stop()

def safe_post(url: str, **kwargs):
    try:
        return requests.post(url, timeout=60, **kwargs)
    except requests.exceptions.RequestException as e:
        st.error("❌ Backend is not running or not reachable.")
        st.caption("Start FastAPI first: `python -m uvicorn app.main:app --reload --port 8000`")
        st.text(str(e))
        st.stop()

# ----------------------------
# Session State init
# ----------------------------
if "resume_uploaded" not in st.session_state:
    st.session_state["resume_uploaded"] = False
if "jd_uploaded" not in st.session_state:
    st.session_state["jd_uploaded"] = False
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Upload"

if "questions" not in st.session_state:
    st.session_state["questions"] = []
if "answers" not in st.session_state:
    st.session_state["answers"] = {}
if "overall_result" not in st.session_state:
    st.session_state["overall_result"] = None

# ----------------------------
# Header
# ----------------------------
st.title("🧠 AI Interview Assistant")
st.caption("Upload Resume + JD → Generate questions → Answer → Get feedback + track progress")

# ✅ Professional “tabs” that can auto-switch
tabs = ["Upload", "Interview", "Dashboard"]
selected = st.radio(
    label="",
    options=tabs,
    index=tabs.index(st.session_state["active_tab"]),
    horizontal=True,
)
st.session_state["active_tab"] = selected

# ----------------------------
# TAB 1: Upload
# ----------------------------
if selected == "Upload":
    st.subheader("Upload Resume & Job Description")
    c1, c2 = st.columns(2)

    with c1:
        resume = st.file_uploader("Resume (PDF)", type=["pdf"], key="resume_file")
        if st.button("Upload Resume", use_container_width=False) and resume:
            r = safe_post(f"{API}/upload/resume", files={"file": resume.getvalue()})

            if r.status_code != 200:
                st.error(f"Upload failed ({r.status_code})")
                st.text(r.text)
            else:
                resp = r.json() if r.text else {}
                st.session_state["resume_uploaded"] = True
                st.success("✅ Resume uploaded successfully!")
                st.caption(f"File: **{resume.name}**  |  Pages: **{resp.get('pages', '-') }**")

    with c2:
        jd = st.file_uploader("Job Description (PDF)", type=["pdf"], key="jd_file")
        if st.button("Upload JD", use_container_width=False) and jd:
            r = safe_post(f"{API}/upload/jd", files={"file": jd.getvalue()})

            if r.status_code != 200:
                st.error(f"Upload failed ({r.status_code})")
                st.text(r.text)
            else:
                resp = r.json() if r.text else {}
                st.session_state["jd_uploaded"] = True
                st.success("✅ Job Description uploaded successfully!")
                st.caption(f"File: **{jd.name}**  |  Pages: **{resp.get('pages', '-') }**")

    st.divider()

    if st.session_state["resume_uploaded"] and st.session_state["jd_uploaded"]:
        st.success("✅ Upload complete! Redirecting to Interview tab...")
        st.session_state["active_tab"] = "Interview"
        st.rerun()
    elif st.session_state["resume_uploaded"] or st.session_state["jd_uploaded"]:
        st.warning("⚠️ Upload the remaining document to get the best interview questions.")
    else:
        st.info("📄 Upload both Resume and Job Description to start interview practice.")

# ----------------------------
# TAB 2: Interview (Questions + Answers + Overall Scoring)
# ----------------------------
elif selected == "Interview":
    st.subheader("Interview Practice (Questions → Answer → Overall Score)")

    # Guard: must upload both
    if not (st.session_state.get("resume_uploaded") and st.session_state.get("jd_uploaded")):
        st.warning("📄 Please upload both **Resume** and **Job Description** first.")
        st.stop()

    role = st.text_input("Role", value="", key="role_main")
    company = st.text_input("Company (optional)", value="", key="company_main")

    colA, colB = st.columns([1, 3])
    with colA:
        if st.button("Generate Questions", use_container_width=False):
            if not role.strip():
                st.warning("Please enter a role (ex: Machine Learning Intern).")
                st.stop()

            payload = {"role": role, "company": company, "num_questions": 8}
            r = safe_post(f"{API}/interview/generate", json=payload)

            if r.status_code != 200:
                st.error(f"Backend error: {r.status_code}")
                st.text(r.text)
                st.stop()

            data = r.json() if r.text else {}
            st.session_state["questions"] = data.get("questions", [])
            st.session_state["answers"] = {}
            st.session_state["overall_result"] = None

    questions = st.session_state.get("questions", [])
    if not questions:
        st.info("Click **Generate Questions** to start.")
        st.stop()

    st.divider()
    st.subheader("Questions")

    for idx, q in enumerate(questions):
        q_text = (q.get("question") or "").strip()
        if not q_text:
            continue

        st.markdown(f"### Q{idx+1}. {q_text}")

        answer = st.text_area(
            "Your Answer",
            value=st.session_state["answers"].get(idx, ""),
            key=f"answer_{idx}",
            height=120,
            placeholder="Type your answer here...",
        )
        st.session_state["answers"][idx] = answer
        st.divider()

    st.subheader("Overall Evaluation")

    if st.button("Score Overall", type="primary", use_container_width=False):
        results = []

        for idx, q in enumerate(questions):
            q_text = (q.get("question") or "").strip()
            ans = (st.session_state["answers"].get(idx) or "").strip()
            if not ans:
                continue

            payload = {"role": role, "company": company, "question": q_text, "answer": ans}
            r = safe_post(f"{API}/evaluation/score", json=payload)

            if r.status_code != 200:
                st.error(f"Scoring failed for Q{idx+1} ({r.status_code})")
                st.text(r.text)
                st.stop()

            out = r.json() if r.text else {}
            results.append(
                {
                    "q_no": idx + 1,
                    "question": q_text,
                    "total_score": out.get("total_score", 0),
                    "breakdown": out.get("breakdown", {}),
                }
            )

        if not results:
            st.warning("Please answer at least one question before scoring.")
            st.stop()

        total_sum = sum(r["total_score"] for r in results)
        avg_score = round(total_sum / len(results), 2)

        keys = ["relevance", "clarity", "technical_correctness", "structure", "impact"]
        cat_totals = {k: 0 for k in keys}
        for r in results:
            bd = r.get("breakdown") or {}
            for k in keys:
                cat_totals[k] += int(bd.get(k, 0))

        cat_avgs = {k: round(cat_totals[k] / len(results), 2) for k in keys}

        st.session_state["overall_result"] = {
            "answered": len(results),
            "total_sum": total_sum,
            "avg_score": avg_score,
            "cat_avgs": cat_avgs,
            "results": results,
        }

        st.session_state["active_tab"] = "Dashboard"
        st.rerun()
    # overall = st.session_state.get("overall_result")
    # if overall:
    #     st.success(f"✅ Scored {overall['answered']} answered question(s)")

    #     c1, c2 = st.columns(2)
    #     c1.metric("Overall Total Score", overall["total_sum"])
    #     c2.metric("Average Score", overall["avg_score"])

    #     st.write("### Category Averages")
    #     b1, b2, b3, b4, b5 = st.columns(5)
    #     b1.metric("Relevance", overall["cat_avgs"]["relevance"])
    #     b2.metric("Clarity", overall["cat_avgs"]["clarity"])
    #     b3.metric("Technical", overall["cat_avgs"]["technical_correctness"])
    #     b4.metric("Structure", overall["cat_avgs"]["structure"])
    #     b5.metric("Impact", overall["cat_avgs"]["impact"])

    #     st.write("### Question-wise Summary")
    #     table_data = [
    #         {
    #             "Q#": r["q_no"],
    #             "Score": r["total_score"],
    #             "Question": r["question"][:80] + ("..." if len(r["question"]) > 80 else ""),
    #         }
    #         for r in overall["results"]
    #     ]
    #     st.dataframe(table_data, use_container_width=True, hide_index=True)

# ----------------------------
# TAB 3: Dashboard (Professional, no JSON)
# ----------------------------
elif selected == "Dashboard":
    st.subheader("📊 Interview Performance Dashboard")


    r_hist = safe_get(f"{API}/analytics/history?limit=20")
    if r_hist.status_code != 200:
        st.error(f"Failed to load history ({r_hist.status_code})")
        st.stop()

    history_data = r_hist.json() if r_hist.text else {}

    # Accept {"items": []}, {"history": []}, or []
    if isinstance(history_data, dict):
        history = history_data.get("items") or history_data.get("history") or []
    elif isinstance(history_data, list):
        history = history_data
    else:
        history = []

    if not history:
        st.info("📭 No interview attempts yet. Start practicing to see progress here.")
        st.stop()

    total_attempts = len(history)
    scores = [h.get("total_score", 0) for h in history]
    avg_score = round(sum(scores) / total_attempts, 2) if total_attempts else 0
    best_score = max(scores) if scores else 0
    latest_score = scores[0] if scores else 0  # if backend returns latest first
    # If your backend returns oldest first, use: latest_score = scores[-1]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Attempts", total_attempts)
    c2.metric("Average Score", avg_score)
    c3.metric("Best Score", best_score)
    c4.metric("Latest Score", latest_score)

    st.divider()

    st.subheader("📈 Score Progress")
    st.line_chart({"Score": scores})

    st.divider()

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
    st.dataframe(table_data, use_container_width=False, hide_index=True)