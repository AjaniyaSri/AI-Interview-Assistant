```md
# 🧠 AI Interview Assistant

An end-to-end **AI-powered interview preparation platform** that helps candidates practice interviews using their **resume and job description**, receive **tailored interview questions**, **AI-based scoring**, and **performance analytics** — all through a clean, professional UI.

---

## 🚀 Features

### 📄 Resume & Job Description Upload
- Upload **PDF resume** and **job description**
- Extracts and understands context automatically
- Ensures questions and feedback are **context-aware**

### ❓ Intelligent Interview Question Generation
- Role-based and company-aware questions
- Technical, behavioral, project, and general questions
- No hallucination — strictly grounded on provided documents

### 🧪 Answer Evaluation & Feedback
- AI evaluates answers using:
  - Relevance
  - Clarity
  - Technical correctness
  - Structure
  - Impact
- Provides:
  - Total score
  - Strengths & improvements
  - Improved sample answer

### 📊 Performance Dashboard
- Total interview attempts
- Average, best, and latest scores
- Score progression over time
- Recent attempt history in a professional table view

---

## 🏗️ Architecture

```

AI-Interview-Assistant/
│
├── backend/                # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   │   ├── upload.py
│   │   │   ├── interview.py
│   │   │   ├── evaluation.py
│   │   │   └── analytics.py
│   │   ├── services/
│   │   │   └── prompts.py
│   │   └── utils/
│   └── requirements.txt
│
├── frontend/               # Streamlit frontend
│   └── app.py
│
├── .env
├── README.md
└── venv/

````

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**
- **Python**
- **Sentence Transformers**
- **Hugging Face models**
- **PDF parsing**
- **Prompt-engineered LLM evaluation**

### Frontend
- **Streamlit**
- **Professional multi-tab UI**
- Error-safe backend communication

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/AI-Interview-Assistant.git
cd AI-Interview-Assistant
````

---

### 2️⃣ Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install dependencies

#### Backend

```bash
cd backend
pip install -r requirements.txt
```

#### Frontend

```bash
cd ../frontend
pip install streamlit requests python-dotenv
```

---

### 4️⃣ Environment variables (`.env`)

```env
API_BASE=http://127.0.0.1:8000
HF_TOKEN=your_huggingface_token_optional
```

> ⚠️ `HF_TOKEN` is optional but recommended to avoid rate limits.

---

## ▶️ Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Verify backend:

```
http://127.0.0.1:8000/docs
```

---

### Start Frontend (Terminal 2)

```bash
cd frontend
streamlit run app.py
```

Frontend URL:

```
http://localhost:8501
```

---

## 📌 Usage Flow

1. Upload **Resume + Job Description**
2. Generate interview questions
3. Answer questions
4. Get AI scoring and feedback
5. Track progress in dashboard

---

## 🧠 Prompt Safety & Accuracy

* Strict **no-hallucination rules**
* AI uses **only resume + JD context**
* Unsupported claims are penalized
* Professional evaluation standards enforced

---

## 🎯 Use Cases

* Students preparing for internships
* Fresh graduates
* Professionals switching roles
* Mock interview practice
* Placement & career preparation

---

## 🚧 Future Enhancements

* Authentication & user profiles
* Multiple interview sessions
* Export feedback as PDF
* Role-specific scoring benchmarks
* Cloud deployment

---

## 👨‍💻 Author

**Ajaniya Kamalanathan**
🎓 Sri Lanka Institute of Information Technology (SLIIT)
📧 Email: [ajaniyaje23@gmail.com](mailto:ajaniyaje23@gmail.com)
🔗 GitHub: [https://github.com/AjaniyaSri](https://github.com/AjaniyaSri)
🔗 LinkedIn: [https://www.linkedin.com/in/ajaniyakamalanathan](https://www.linkedin.com/in/ajaniyakamalanathan)




