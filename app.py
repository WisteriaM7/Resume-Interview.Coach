import streamlit as st
from datetime import datetime
from agents import resume_optimizer, behavioral_interview, role_fit_analyzer
from memory import (
    load_profile, save_profile, add_session_log,
    get_session_logs, list_profiles, delete_profile
)

st.set_page_config(page_title="Resume & Interview Coach", page_icon="💼", layout="wide")

st.title("💼 Resume & Interview Coach")
st.caption("AI-powered career prep using Ollama — resume feedback, mock interviews, role-fit analysis")

# ── Sidebar: Profile Setup ────────────────────────────────────────────────────
with st.sidebar:
    st.header("👤 Your Profile")

    all_profiles = list_profiles()
    profile_options = all_profiles + ["+ New Profile"]
    selected_profile = st.selectbox("Select Profile", profile_options)

    if selected_profile == "+ New Profile":
        new_name = st.text_input("Your Name", placeholder="e.g. Priya Sharma")
        if st.button("✅ Create Profile", use_container_width=True, type="primary"):
            if new_name:
                save_profile(new_name, {"name": new_name, "created": str(datetime.now())})
                st.success(f"Profile '{new_name}' created!")
                st.rerun()
        st.stop()

    user_name = selected_profile
    profile = load_profile(user_name)

    st.write(f"**Name:** {user_name}")
    logs = get_session_logs(user_name)
    st.write(f"**Sessions logged:** {len(logs)}")

    if logs:
        last = logs[-1]
        st.caption(f"Last session: {last['timestamp'][:16]} — {last['type']}")

    st.divider()
    if st.button("🗑️ Delete This Profile", use_container_width=True):
        delete_profile(user_name)
        st.success("Profile deleted.")
        st.rerun()

# Guard
if not all_profiles:
    st.info("👈 Create a profile in the sidebar to get started!")
    st.stop()

profile = load_profile(user_name)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Resume Optimizer",
    "🎤 Mock Interview",
    "🎯 Role-Fit Analyzer",
    "📜 History & Progress",
    "📤 Export"
])

# ── TAB 1: Resume Optimizer ───────────────────────────────────────────────────
with tab1:
    st.subheader("📄 Resume Optimizer Agent")

    col1, col2 = st.columns(2)
    with col1:
        target_role = st.text_input("Target Job Title", value=profile.get("target_role", ""), placeholder="e.g. Data Scientist")
        target_company = st.text_input("Target Company (optional)", value=profile.get("target_company", ""), placeholder="e.g. Google")
        years_exp = st.number_input("Years of Experience", min_value=0, max_value=40, value=profile.get("years_exp", 2))

    with col2:
        industry = st.selectbox("Industry", [
            "Technology", "Finance", "Healthcare", "Marketing", "Education",
            "Consulting", "Engineering", "Design", "Research", "Government", "Other"
        ], index=0)
        job_desc = st.text_area("Job Description (paste here)", height=120, placeholder="Paste the job posting you're applying to...")

    resume_text = st.text_area(
        "Paste Your Resume Text",
        height=300,
        value=profile.get("resume_text", ""),
        placeholder="Paste your full resume text here..."
    )

    if st.button("🚀 Optimize My Resume", type="primary", use_container_width=True):
        if not resume_text:
            st.warning("Please paste your resume text.")
        elif not target_role:
            st.warning("Please enter a target job title.")
        else:
            # Save inputs to profile
            profile.update({
                "target_role": target_role,
                "target_company": target_company,
                "years_exp": years_exp,
                "industry": industry,
                "resume_text": resume_text
            })
            save_profile(user_name, profile)

            with st.spinner("🤖 Resume Optimizer Agent is reviewing your resume..."):
                result = resume_optimizer(resume_text, target_role, target_company, industry, years_exp, job_desc)

            st.markdown("### 📋 Resume Feedback & Optimized Version")
            st.markdown(result)

            add_session_log(user_name, "resume_optimization", result, {
                "target_role": target_role,
                "target_company": target_company,
                "industry": industry
            })
            st.success("✅ Feedback saved to your history!")

    # Show previous resume feedback
    prev_resume_logs = [l for l in get_session_logs(user_name) if l["type"] == "resume_optimization"]
    if prev_resume_logs:
        st.divider()
        with st.expander(f"📌 Previous Resume Feedback ({len(prev_resume_logs)} sessions)"):
            for log in reversed(prev_resume_logs[-3:]):
                st.caption(f"**{log['timestamp'][:16]}** — {log['meta'].get('target_role', 'N/A')}")
                st.markdown(log["content"][:500] + "...")
                st.divider()

# ── TAB 2: Mock Interview ─────────────────────────────────────────────────────
with tab2:
    st.subheader("🎤 Behavioral Interview Agent")

    target_role_i = st.text_input("Role You're Interviewing For",
                                   value=profile.get("target_role", ""),
                                   placeholder="e.g. Product Manager",
                                   key="interview_role")
    interview_type = st.selectbox("Interview Type", [
        "Behavioral (STAR method)",
        "Situational",
        "Leadership & Management",
        "Technical Scenario",
        "Culture Fit"
    ])
    difficulty = st.select_slider("Difficulty", ["Entry Level", "Mid Level", "Senior", "Executive"])

    st.divider()
    st.markdown("#### 💬 Interview Session")

    # Generate question
    if st.button("🎯 Generate Interview Question", use_container_width=True):
        prev_questions = [l["meta"].get("question", "") for l in get_session_logs(user_name) if l["type"] == "interview"]
        with st.spinner("Generating question..."):
            question = behavioral_interview(
                mode="question",
                role=target_role_i,
                interview_type=interview_type,
                difficulty=difficulty,
                prev_questions=prev_questions
            )
        st.session_state["current_question"] = question
        st.session_state["interview_role"] = target_role_i

    if "current_question" in st.session_state:
        st.markdown(f"**❓ Question:** {st.session_state['current_question']}")

        user_answer = st.text_area("Your Answer", height=200, placeholder="Type your answer using the STAR method (Situation, Task, Action, Result)...")

        if st.button("📝 Get Feedback on My Answer", type="primary", use_container_width=True):
            if not user_answer:
                st.warning("Please write your answer first.")
            else:
                with st.spinner("🤖 Analyzing your answer..."):
                    feedback = behavioral_interview(
                        mode="feedback",
                        role=target_role_i,
                        interview_type=interview_type,
                        difficulty=difficulty,
                        question=st.session_state["current_question"],
                        answer=user_answer
                    )

                st.markdown("### 💡 Feedback on Your Answer")
                st.markdown(feedback)

                add_session_log(user_name, "interview", feedback, {
                    "question": st.session_state["current_question"],
                    "answer": user_answer,
                    "role": target_role_i,
                    "type": interview_type,
                    "difficulty": difficulty
                })
                st.success("✅ Session saved to your history!")

# ── TAB 3: Role-Fit Analyzer ──────────────────────────────────────────────────
with tab3:
    st.subheader("🎯 Role-Fit Analyzer Agent")
    st.caption("Analyze how well your background matches a specific role or company.")

    col1, col2 = st.columns(2)
    with col1:
        fit_role = st.text_input("Target Role", value=profile.get("target_role", ""), placeholder="e.g. ML Engineer", key="fit_role")
        fit_company = st.text_input("Target Company", value=profile.get("target_company", ""), placeholder="e.g. Stripe", key="fit_company")

    with col2:
        career_goal = st.text_area("Your Career Goal", height=100,
                                    value=profile.get("career_goal", ""),
                                    placeholder="e.g. Transition from data analyst to ML engineer at a fintech startup in 6 months")

    fit_job_desc = st.text_area("Job Description", height=150,
                                 placeholder="Paste the job description for accurate matching...")
    fit_resume = st.text_area("Your Resume / Background",
                               value=profile.get("resume_text", ""),
                               height=200,
                               placeholder="Paste your resume or describe your background...",
                               key="fit_resume")

    if st.button("🔍 Analyze Role Fit", type="primary", use_container_width=True):
        if not fit_resume or not fit_role:
            st.warning("Please enter your background and target role.")
        else:
            profile.update({"career_goal": career_goal, "target_role": fit_role, "target_company": fit_company})
            save_profile(user_name, profile)

            with st.spinner("🤖 Role-Fit Analyzer is evaluating your profile..."):
                result = role_fit_analyzer(fit_resume, fit_role, fit_company, fit_job_desc, career_goal, profile)

            st.markdown("### 🎯 Role-Fit Analysis")
            st.markdown(result)

            add_session_log(user_name, "role_fit", result, {
                "role": fit_role,
                "company": fit_company,
                "career_goal": career_goal
            })
            st.success("✅ Analysis saved to your history!")

# ── TAB 4: History & Progress ─────────────────────────────────────────────────
with tab4:
    st.subheader("📜 Your History & Progress")

    logs = get_session_logs(user_name)
    if not logs:
        st.info("No sessions yet. Use the other tabs to build your history.")
    else:
        type_counts = {}
        for l in logs:
            type_counts[l["type"]] = type_counts.get(l["type"], 0) + 1

        col1, col2, col3 = st.columns(3)
        col1.metric("📄 Resume Sessions", type_counts.get("resume_optimization", 0))
        col2.metric("🎤 Interview Sessions", type_counts.get("interview", 0))
        col3.metric("🎯 Role-Fit Analyses", type_counts.get("role_fit", 0))

        st.divider()

        filter_type = st.selectbox("Filter by type", ["All", "resume_optimization", "interview", "role_fit"])
        filtered = logs if filter_type == "All" else [l for l in logs if l["type"] == filter_type]

        for log in reversed(filtered):
            label_map = {
                "resume_optimization": "📄 Resume Optimization",
                "interview": "🎤 Mock Interview",
                "role_fit": "🎯 Role-Fit Analysis"
            }
            label = label_map.get(log["type"], log["type"])
            meta_str = " | ".join(f"{k}: {v}" for k, v in log.get("meta", {}).items() if v)
            with st.expander(f"{label} — {log['timestamp'][:16]}  |  {meta_str}"):
                if log["type"] == "interview" and log["meta"].get("question"):
                    st.markdown(f"**Question:** {log['meta']['question']}")
                    st.markdown(f"**Your Answer:** {log['meta'].get('answer', 'N/A')}")
                    st.divider()
                st.markdown(log["content"])

# ── TAB 5: Export ─────────────────────────────────────────────────────────────
with tab5:
    st.subheader("📤 Export Your Career Prep Summary")

    logs = get_session_logs(user_name)
    if not logs:
        st.info("Complete some sessions first, then export here.")
    else:
        export_type = st.multiselect(
            "Include in export",
            ["Resume Feedback", "Interview Sessions", "Role-Fit Analyses"],
            default=["Resume Feedback", "Interview Sessions", "Role-Fit Analyses"]
        )

        if st.button("📄 Build Export", type="primary", use_container_width=True):
            lines = [
                "CAREER PREP SUMMARY",
                "=" * 50,
                f"Name    : {user_name}",
                f"Profile : {profile.get('target_role', 'N/A')} at {profile.get('target_company', 'N/A')}",
                f"Industry: {profile.get('industry', 'N/A')}",
                f"Goal    : {profile.get('career_goal', 'N/A')}",
                f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "=" * 50,
                ""
            ]

            type_map = {
                "Resume Feedback": "resume_optimization",
                "Interview Sessions": "interview",
                "Role-Fit Analyses": "role_fit"
            }

            for section in export_type:
                t = type_map[section]
                section_logs = [l for l in logs if l["type"] == t]
                if section_logs:
                    lines += ["", f"{'=' * 50}", section.upper(), f"{'=' * 50}"]
                    for i, log in enumerate(section_logs, 1):
                        lines += [f"\n[Session {i}] {log['timestamp'][:16]}"]
                        meta_str = " | ".join(f"{k}: {v}" for k, v in log.get("meta", {}).items() if v and k not in ["answer"])
                        if meta_str:
                            lines.append(meta_str)
                        if t == "interview" and log["meta"].get("question"):
                            lines += [f"Q: {log['meta']['question']}", f"A: {log['meta'].get('answer', '')}"]
                        lines += [log["content"], ""]

            export_text = "\n".join(lines)
            filename = f"career_prep_{user_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"

            st.download_button(
                "⬇️ Download (.txt)",
                data=export_text,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
            with st.expander("Preview"):
                st.text(export_text[:2000] + ("..." if len(export_text) > 2000 else ""))
