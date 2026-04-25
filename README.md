# 💼 Resume & Interview Coach

An AI-powered career prep tool using **Streamlit + Ollama**.  
Fully local, no paid APIs. Three agents help you optimize your resume, ace interviews, and evaluate role fit.

## 🤖 AI Agents

| Agent | Role |
|-------|------|
| **Resume Optimizer** | ATS scoring, keyword gaps, bullet rewrites, and a pro summary |
| **Behavioral Interview Agent** | Generates questions and gives STAR-method feedback on your answers |
| **Role-Fit Analyzer** | Scores your fit %, identifies gaps, and builds a 90-day action plan |

## 📁 Project Structure

```
resume_coach/
├── app.py              # Main Streamlit UI (5 tabs)
├── agents.py           # 3 Ollama-powered AI agents
├── memory.py           # Per-user profile + session history persistence
├── requirements.txt    # Python dependencies
├── career_data/        # Auto-created: stores profiles and logs as JSON
└── README.md
```

## ⚙️ Setup

### 1. Install Ollama
Download from [ollama.com](https://ollama.com)

### 2. Pull a Model
```bash
ollama pull llama3.2
```
> Also works with `mistral`, `gemma2`, `phi3`. Update `MODEL` in `agents.py`.

### 3. Start Ollama
```bash
ollama serve
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App
```bash
streamlit run app.py
```

## 🚀 How to Use

1. **Create a profile** — Enter your name in the sidebar
2. **Tab 1 — Resume Optimizer**: Paste your resume + job description → get ATS score, rewrites, keywords
3. **Tab 2 — Mock Interview**: Generate questions by type and difficulty → submit answers → get STAR feedback
4. **Tab 3 — Role-Fit Analyzer**: Get a fit % score, gap analysis, and a 90-day improvement plan
5. **Tab 4 — History**: Review all past sessions, filter by type
6. **Tab 5 — Export**: Download your full career prep summary as `.txt`

## 💾 Data Storage

All data is stored locally in `career_data/`:
- `{name}_profile.json` — your profile and saved resume
- `{name}_logs.json` — all session history with timestamps

## 🔧 Customization

- **Change model**: Edit `MODEL = "llama3.2"` in `agents.py`
- **Add interview types**: Extend the selectbox options in `app.py`
- **Multi-user**: Each profile is stored separately — multiple users can use the same app
