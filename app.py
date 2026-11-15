import streamlit as st
import pandas as pd
from io import BytesIO
from html import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
import plotly.graph_objects as go
from utils.recommender import recommend_careers, load_careers

st.set_page_config(page_title="CareerCompass AI", page_icon="🧭", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url("https://googleapis.com");
html, body, [class*="css"] { font-family: "Inter", sans-serif !important; }
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
.stApp { background-color: #F8FAFC; background-image: radial-gradient(#CBD5E1 0.6px, transparent 0.6px); background-size: 24px 24px; }
.block-container { max-width: 1180px; padding-top: 1.5rem; padding-bottom: 4rem; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #090D16 0%, #111827 100%) !important; }
[data-testid="stSidebar"] * { color: #F1F5F9 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 12px 16px !important; font-weight: 600 !important; margin-bottom: 6px; }
.hero-box { background: linear-gradient(135deg, #090D16 0%, #1E293B 45%, #1D4ED8 100%); padding: 44px 40px; border-radius: 24px; margin-bottom: 28px; box-shadow: 0 20px 40px -12px rgba(15,23,42,0.28); }
.hero-badge { display: inline-block; background: rgba(59,130,246,0.25); border: 1px solid rgba(147,197,253,0.4); color: #93C5FD !important; padding: 4px 12px; border-radius: 999px; font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 12px; }
.hero-box h1 { color: #FFFFFF !important; font-size: 38px !important; font-weight: 800 !important; margin: 0 0 10px 0 !important; }
.hero-box p { color: #CBD5E1 !important; font-size: 16px !important; margin: 0 !important; }
.feature-card { background: #FFFFFF; padding: 26px; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 4px 20px rgba(15,23,42,0.04); height: 100%; }
.feature-card h3 { color: #0F172A !important; font-size: 18px !important; font-weight: 700 !important; }
.feature-card p { color: #475569 !important; font-size: 14.5px !important; }
.career-card { background: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #2563EB; border-radius: 18px; padding: 24px 28px; margin-bottom: 18px; box-shadow: 0 6px 24px rgba(15,23,42,0.04); }
.career-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.career-title { font-size: 21px; font-weight: 800; color: #0F172A; margin: 0; }
.match-pill { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; padding: 6px 14px; border-radius: 999px; font-weight: 800; font-size: 14px; }
.cat-tag { display: inline-block; background: #F1F5F9; color: #475569; padding: 3px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; margin-bottom: 12px; }
.roadmap-box { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 18px; margin-top: 14px; color: #334155; font-size: 14px; }
[data-testid="stMain"] .stButton > button, [data-testid="stMain"] .stDownloadButton > button { background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important; color: #FFFFFF !important; border: none !important; border-radius: 12px !important; min-height: 48px !important; font-weight: 700 !important; }
[data-testid="stMetric"] { background: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-radius: 18px !important; padding: 18px 22px !important; }
</style>""", unsafe_allow_html=True)
careers = load_careers()

def render_skill_badges(skills, badge_type="matched"):
    if not skills:
        return "<span style='color:#94A3B8; font-size:13px;'>None</span>"
    bg, border, text, icon = ("#ECFDF5", "#A7F3D0", "#065F46", "✓") if badge_type == "matched" else ("#FFFBEB", "#FDE68A", "#92400E", "+")
    pills = "".join([f"<span style='display:inline-block; background:{bg}; border:1px solid {border}; color:{text}; padding:4px 12px; border-radius:999px; font-size:12.5px; font-weight:600; margin:3px 6px 3px 0;'>{icon} {escape(s.title())}</span>" for s in skills])
    return f"<div style='margin: 4px 0 10px 0;'>{pills}</div>"

all_skills = sorted({skill.strip() for skills in careers["skills"] for skill in skills.split(",")})
st.sidebar.markdown("## 🧭 CareerCompass AI")
st.sidebar.caption("INTELLIGENT CAREER ARCHITECTURE")
st.sidebar.divider()
page = st.sidebar.radio("MENU", ["🏠 Overview", "🔎 Career Finder", "📘 Methodology"])

if page == "🏠 Overview":
    st.markdown('<div class="hero-box"><span class="hero-badge">AI Career Intelligence</span><h1>Map Your Skills to Your Ideal Career 🚀</h1><p>Rate your technical proficiency, simulate new skills, and get a data-driven career roadmap.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="feature-card"><h3>🧠 Weighted Skill Profiling</h3><p>Rate mastery from Beginner to Expert so the AI weighs your strongest skills accurately.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="feature-card"><h3>🎯 Precision Role Matching</h3><p>Compare your skill vector against industry roles to surface highest-fit careers.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="feature-card"><h3>🧪 What-If Skill Simulator</h3><p>Preview how learning missing skills boosts your match score in real time.</p></div>', unsafe_allow_html=True)
    st.write("")
    a, b, c = st.columns(3)
    a.metric("Career Roles Indexed", len(careers))
    b.metric("Matching Engine", "Weighted AI")
    c.metric("Export Format", "PDF Report")
    st.info("👈 Open **Career Finder** in the left sidebar to build your skill profile.")

elif page == "🔎 Career Finder":
    st.markdown('<div class="hero-box"><span class="hero-badge">Interactive Assessment</span><h1>Build Your Skill Profile 🎯</h1><p>Select your skills, set your proficiency level, and discover your strongest career paths.</p></div>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("### 1. Candidate Details")
        name = st.text_input("Full Name", placeholder="e.g. Hithesh Kumar")
        education = st.selectbox("Education Level", ["High School", "Diploma", "Undergraduate", "Postgraduate", "Other"])
    with col_r:
        st.markdown("### 2. Target Domains (Optional)")
        interests = st.multiselect("Preferred Career Fields", ["Data Science", "Artificial Intelligence", "Web Development", "Software Development", "Cybersecurity", "Cloud Computing", "App Development", "Design", "Database Management"])
    st.divider()
    st.markdown("### 3. Skills & Proficiency Mastery")
    selected_skills = st.multiselect("Select all skills you currently have", options=all_skills)
    skill_weights = {}
    if selected_skills:
        cols = st.columns(min(len(selected_skills), 3))
        pmap = {"Beginner": 0.7, "Intermediate": 1.0, "Expert": 1.4}
        for idx, skill in enumerate(selected_skills):
            with cols[idx % 3]:
                lvl = st.select_slider(f"**{skill}**", options=["Beginner", "Intermediate", "Expert"], value="Intermediate", key=f"prof_{skill}")
                skill_weights[skill] = pmap[lvl]
    if st.button("🚀 Analyze My Career Matches", use_container_width=True):
        if not name.strip(): st.warning("Please enter your name.")
        elif not selected_skills: st.warning("Please select at least one skill.")
        else:
            res = recommend_careers(skill_weights, top_n=15)
            if interests:
                res["interest_bonus"] = res["category"].apply(lambda cat: 10 if cat in interests else 0)
                res["final_score"] = res["match_percentage"] * 0.9 + res["interest_bonus"]
                res = res.sort_values("final_score", ascending=False)
            st.session_state["results"] = res.head(5).reset_index(drop=True)
            st.session_state["student_name"] = name
            st.session_state["education"] = education
            st.session_state["skill_weights"] = skill_weights
    if "results" in st.session_state:
        results = st.session_state["results"]
        best = results.iloc[0]
        st.divider()
        st.markdown(f"## 🏆 Assessment Results for {escape(st.session_state['student_name'])}")
        x, y, z = st.columns(3)
        x.metric("Top Recommended Role", best["career"])
        y.metric("Match Compatibility", f"{best['match_percentage']:.1f}%")
        z.metric("Skills Evaluated", len(st.session_state["skill_weights"]))
        sorted_res = results.sort_values("match_percentage", ascending=True)
        fig = go.Figure(go.Bar(x=sorted_res["match_percentage"], y=sorted_res["career"], orientation="h", text=[f"<b>{v:.1f}%</b>" for v in sorted_res["match_percentage"]], textposition="outside", marker=dict(color=sorted_res["match_percentage"], colorscale=[[0, "#93C5FD"], [0.5, "#3B82F6"], [1, "#1D4ED8"]])))
        fig.update_layout(height=320, margin=dict(l=10, r=50, t=10, b=10), xaxis=dict(range=[0, 115], showgrid=True, gridcolor="#F1F5F9"), plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF")
        st.plotly_chart(fig, use_container_width=True)
        for _, career in results.iterrows():
            m_html = render_skill_badges(career["matched_skills"], "matched")
            u_html = render_skill_badges(career["missing_skills"], "missing")
            st.markdown(f'<div class="career-card"><div class="career-header"><h3 class="career-title">{escape(career["career"])}</h3><span class="match-pill">{career["match_percentage"]:.1f}% Match</span></div><span class="cat-tag">{escape(career["category"])}</span><p style="color:#334155; font-size:15px;">{escape(career["description"])}</p><div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;"><div><strong>✅ Matching Skills</strong>{m_html}</div><div><strong>🎯 Skills to Acquire</strong>{u_html}</div></div><div class="roadmap-box"><strong>📚 Learning Path:</strong> {escape(career["learning_path"])}</div></div>', unsafe_allow_html=True)
        st.subheader("🧪 What-If Skill Simulator")
        sim = st.multiselect("Select missing skills to simulate:", options=[s.title() for s in best["missing_skills"]], key="sim_skills")
        if sim:
            sw = st.session_state["skill_weights"].copy()
            for s in sim: sw[s] = 1.0
            sr = recommend_careers(sw, top_n=15)
            ns = float(sr.loc[sr["career"] == best["career"], "match_percentage"].values[0])
            st.metric(f"Simulated Score for {best['career']}", f"{ns:.1f}%", f"+{round(ns - float(best['match_percentage']), 1)}% boost")
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [Paragraph("CAREERCOMPASS AI REPORT", styles["Title"]), Spacer(1, 12)]
        for idx, (_, c) in enumerate(results.iterrows(), 1):
            story.append(Paragraph(f"<b>{idx}. {escape(str(c['career']))} ({c['match_percentage']:.1f}%)</b> - {escape(str(c['description']))}", styles["BodyText"]))
            story.append(Spacer(1, 8))
        doc.build(story)
        st.download_button("📄 Download PDF Career Report", data=pdf_buffer.getvalue(), file_name="CareerCompass_Report.pdf", mime="application/pdf")

elif page == "📘 Methodology":
    st.markdown('<div class="hero-box"><span class="hero-badge">Under the Hood</span><h1>How CareerCompass AI Works</h1><p>Weighted vector similarity paired with interactive skill-gap simulation.</p></div>', unsafe_allow_html=True)
    st.markdown("- **Weighted Skill Vectors:** Beginner (0.7x), Intermediate (1.0x), and Expert (1.4x) weights refine cosine similarity.\n- **What-If Simulation:** Dynamically recalculates role compatibility when adding new skills.")
