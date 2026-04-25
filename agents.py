import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"  # Change to: mistral, gemma2, phi3, etc.


def call_ollama(prompt: str, system_prompt: str = "") -> str:
    """Call local Ollama model and return response text."""
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    payload = {
        "model": MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        response.raise_for_status()
        return response.json().get("response", "No response received.")
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to Ollama. Run `ollama serve` and ensure the model is pulled."
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Try again or use a shorter prompt."
    except Exception as e:
        return f"❌ Error: {str(e)}"


def resume_optimizer(resume_text: str, target_role: str, target_company: str,
                     industry: str, years_exp: int, job_desc: str) -> str:
    """Agent 1: Analyzes and optimizes a resume for a target role."""
    system_prompt = """You are an expert resume coach and recruiter with 15+ years of experience 
    at top companies including FAANG, Fortune 500, and leading startups.
    You give honest, specific, actionable feedback that actually gets people hired.
    You understand ATS systems, keyword optimization, and what hiring managers look for."""

    jd_section = f"\nJob Description:\n{job_desc}" if job_desc else ""

    prompt = f"""Review and optimize this resume for a {years_exp}-year experienced candidate 
targeting a **{target_role}** role{' at ' + target_company if target_company else ''} in the {industry} industry.
{jd_section}

RESUME:
{resume_text}

Provide a complete review with:

**1. ATS SCORE** — Estimate ATS compatibility score (0-100) and explain why

**2. FIRST IMPRESSION** — What a recruiter thinks in the first 6 seconds

**3. STRENGTHS** — What's working well (be specific)

**4. CRITICAL IMPROVEMENTS** — Top 5 must-fix issues with exact rewrites

**5. KEYWORDS MISSING** — Important keywords for {target_role} in {industry} that are absent

**6. BULLET POINT REWRITES** — Take 3 weak bullets and rewrite them with strong action verbs + metrics

**7. SUMMARY SECTION** — Write an optimized professional summary for this candidate targeting {target_role}

**8. FORMATTING TIPS** — Layout, length, and structure suggestions

**9. QUICK WINS** — 3 things they can fix in under 10 minutes

**10. OVERALL RATING** — Score out of 10 with a one-line verdict"""

    return call_ollama(prompt, system_prompt)


def behavioral_interview(mode: str, role: str, interview_type: str, difficulty: str,
                         question: str = "", answer: str = "",
                         prev_questions: list = None) -> str:
    """Agent 2: Generates interview questions and gives feedback on answers."""
    system_prompt = """You are an expert interview coach who has conducted thousands of interviews 
    at top tech companies, consultancies, and Fortune 500 firms.
    You help candidates master behavioral interviews using the STAR method.
    You give detailed, honest feedback that builds confidence and skills."""

    if mode == "question":
        prev_q_text = ""
        if prev_questions:
            recent = prev_questions[-5:]
            prev_q_text = f"\n\nAvoid these recently asked questions:\n" + "\n".join(f"- {q}" for q in recent)

        prompt = f"""Generate ONE {difficulty} {interview_type} interview question for a {role} position.

The question should:
- Be realistic and commonly asked at top companies
- Match the {difficulty} level and {interview_type} category
- Test relevant competencies for a {role}
{prev_q_text}

Return ONLY the question itself, nothing else. No preamble, no explanation."""

        return call_ollama(prompt, system_prompt)

    elif mode == "feedback":
        prompt = f"""A candidate for a **{role}** position ({difficulty}) answered this {interview_type} question:

**Question:** {question}

**Their Answer:** {answer}

Provide detailed interview coaching feedback:

**1. STAR METHOD SCORE** — Rate each component (Situation/Task/Action/Result) out of 5

**2. OVERALL SCORE** — Rate the answer 1-10 with a one-line verdict

**3. WHAT WORKED** — Specific strengths in their answer

**4. WHAT'S MISSING** — Critical gaps or weak points

**5. IMPROVED ANSWER** — Rewrite their answer as a model response using STAR method

**6. FOLLOW-UP QUESTIONS** — 2 follow-ups an interviewer might ask, with tips to answer them

**7. BODY LANGUAGE & DELIVERY TIPS** — Practical tips for delivering this answer in person

**8. KEYWORDS TO USE** — Power words and phrases that resonate for {role} roles"""

        return call_ollama(prompt, system_prompt)

    return "Invalid mode specified."


def role_fit_analyzer(resume_text: str, target_role: str, target_company: str,
                      job_desc: str, career_goal: str, profile: dict) -> str:
    """Agent 3: Analyzes how well a candidate fits a target role."""
    system_prompt = """You are a senior career strategist and executive recruiter who helps 
    professionals navigate career transitions and land their dream roles.
    You give candid, data-driven assessments and build realistic action plans."""

    jd_section = f"\nJob Description:\n{job_desc}" if job_desc else ""
    goal_section = f"\nCareer Goal: {career_goal}" if career_goal else ""
    company_section = f" at {target_company}" if target_company else ""

    prev_roles = profile.get("target_role", "")
    years_exp = profile.get("years_exp", "unknown")

    prompt = f"""Analyze the fit between this candidate and the target role.

**Target Role:** {target_role}{company_section}
**Years of Experience:** {years_exp}
{goal_section}
{jd_section}

**Candidate Background / Resume:**
{resume_text}

Provide a thorough role-fit analysis:

**1. FIT SCORE** — Overall match percentage (0-100%) with breakdown:
   - Skills match: X%
   - Experience match: X%
   - Industry match: X%
   - Culture/Values (if company known): X%

**2. STRONG MATCHES** — Where the candidate clearly qualifies

**3. GAPS TO ADDRESS** — Skills, experience, or qualifications missing

**4. TRANSFERABLE STRENGTHS** — Underrated strengths that apply to this role

**5. COMPETITIVE LANDSCAPE** — How they compare to typical applicants for {target_role}

**6. 90-DAY ACTION PLAN** — Specific steps to become a stronger candidate:
   - Week 1-2: Quick wins
   - Month 1: Skills to learn/demonstrate
   - Month 2-3: Experience to build

**7. SHOULD YOU APPLY?** — Honest recommendation with reasoning

**8. ALTERNATIVE ROLES** — 3 similar roles where this candidate might have better odds

**9. INTERVIEW ANGLES** — How to frame their background to overcome gaps in interviews"""

    return call_ollama(prompt, system_prompt)
