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
h1, h2, h3, .career-title { font-family: "Space Grotesk", sans-serif !important; }
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

@keyframes pulseGrid {
    0% { background-position: 0px 0px, 0% 50%; }
    50% { background-position: 40px 40px, 100% 50%; }
    100% { background-position: 0px 0px, 0% 50%; }
}

.stApp {
    background-color: #050814 !important;
    background-image:
        linear-gradient(rgba(56, 189, 248, 0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56, 189, 248, 0.07) 1px, transparent 1px),
        radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.18), transparent 42%),
        radial-gradient(circle at 85% 80%, rgba(168, 85, 247, 0.18), transparent 45%) !important;
    background-size: 40px 40px, 40px 40px, 100% 100%, 100% 100% !important;
    animation: pulseGrid 18s ease-in-out infinite;
    color: #F8FAFC !important;
}

.block-container { max-width: 1200px; padding-top: 1.5rem; padding-bottom: 4rem; }

[data-testid="stSidebar"] {
    background: rgba(9, 14, 30, 0.90) !important;
    backdrop-filter: blur(18px) !important;
    border-right: 1px solid rgba(56, 189, 248, 0.22) !important;
}
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(56, 189, 248, 0.18);
    border-radius: 12px;
    padding: 12px 16px !important;
    font-weight: 600 !important;
    margin-bottom: 8px;
    transition: all 0.25s ease;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(56, 189, 248, 0.18);
    border-color: #38BDF8;
    box-shadow: 0 0 18px rgba(56, 189, 248, 0.35);
    transform: translateX(4px);
}

@keyframes borderGlow {
    0%, 100% { border-color: rgba(56, 189, 248, 0.45); box-shadow: 0 0 35px rgba(56, 189, 248, 0.18); }
    50% { border-color: rgba(168, 85, 247, 0.55); box-shadow: 0 0 45px rgba(168, 85, 247, 0.24); }
}

.hero-box {
    background: linear-gradient(135deg, rgba(13, 19, 38, 0.94) 0%, rgba(23, 37, 84, 0.90) 55%, rgba(88, 28, 135, 0.80) 100%);
    backdrop-filter: blur(16px);
    padding: 44px 40px;
    border-radius: 24px;
    margin-bottom: 28px;
    border: 1px solid rgba(56, 189, 248, 0.45);
    animation: borderGlow 6s infinite ease-in-out;
}
.hero-badge {
    display: inline-block;
    background: rgba(56, 189, 248, 0.16);
    border: 1px solid #38BDF8;
    color: #38BDF8 !important;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.hero-box h1 {
    background: linear-gradient(90deg, #FFFFFF 0%, #38BDF8 55%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: clamp(30px, 4vw, 44px) !important;
    font-weight: 700 !important;
    margin: 0 0 10px 0 !important;
}
.hero-box p { color: #CBD5E1 !important; font-size: 16px !important; line-height: 1.6 !important; max-width: 680px; margin: 0 !important; }

.feature-card {
    background: rgba(13, 19, 38, 0.78);
    backdrop-filter: blur(14px);
    padding: 26px;
    border-radius: 20px;
    border: 1px solid rgba(56, 189, 248, 0.22);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    height: 100%;
    transition: all 0.28s ease;
}
.feature-card:hover {
    transform: translateY(-6px);
    border-color: #38BDF8;
    box-shadow: 0 14px 36px rgba(56, 189, 248, 0.25);
}
.feature-card h3 { color: #F8FAFC !important; font-size: 18px !important; margin-bottom: 8px !important; }
.feature-card p { color: #94A3B8 !important; font-size: 14.5px !important; line-height: 1.6 !important; }

.career-card {
    background: linear-gradient(145deg, rgba(13, 19, 38, 0.94), rgba(15, 23, 42, 0.88));
    backdrop-filter: blur(14px);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-left: 5px solid #38BDF8;
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 18px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    transition: all 0.25s ease;
}
.career-card:hover {
    border-color: #C084FC;
    border-left-color: #C084FC;
    box-shadow: 0 12px 35px rgba(168, 85, 247, 0.22);
}
.career-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.career-title { font-size: 22px; font-weight: 700; color: #F8FAFC; margin: 0; }
.match-pill {
    background: rgba(56, 189, 248, 0.15);
    color: #38BDF8;
    border: 1px solid #38BDF8;
    padding: 6px 15px;
    border-radius: 999px;
    font-weight: 700;
    font-size: 14px;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
}
.cat-tag {
    display: inline-block;
    background: rgba(168, 85, 247, 0.16);
    border: 1px solid rgba(192, 132, 252, 0.35);
    color: #D8B4FE;
    padding: 3px 11px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
}
.roadmap-box {
    background: rgba(5, 8, 20, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-radius: 12px;
    padding: 14px 18px;
    margin-top: 14px;
    color: #CBD5E1;
    font-size: 14px;
}

[data-testid="stMain"] .stButton > button, [data-testid="stMain"] .stDownloadButton > button {
    background: linear-gradient(90deg, #0284C7 0%, #38BDF8 50%, #8B5CF6 100%) !important;
    background-size: 200% auto !important;
    color: #050814 !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 50px !important;
    font-weight: 800 !important;
    box-shadow: 0 0 24px rgba(56, 189, 248, 0.45) !important;
    transition: all 0.3s ease !important;
}
[data-testid="stMain"] .stButton > button:hover, [data-testid="stMain"] .stDownloadButton > button:hover {
    background-position: right center !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 32px rgba(168, 85, 247, 0.65) !important;
}

[data-testid="stMetric"] {
    background: rgba(13, 19, 38, 0.85) !important;
    border: 1px solid rgba(56, 189, 248, 0.25) !important;
    border-radius: 18px !important;
    padding: 18px 22px !important;
}
[data-testid="stMetricValue"] { color: #38BDF8 !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #94A3B8 !important; }
</style>""", unsafe_allow_html=True)
careers = load_careers()

def render_skill_badges(skills, badge_type="matched"):
    if not skills:
        return "<span style='color:#64748B; font-size:13px;'>None listed</span>"
    if badge_type == "matched":
        bg, border, text, icon = "rgba(16, 185, 129, 0.14)", "#10B981", "#6EE7B7", "✓"
    else:
        bg, border, text, icon = "rgba(245, 158, 11, 0.14)", "#F59E0B", "#FCD34D", "+"
    pills = "".join([f"<span style='display:inline-block; background:{bg}; border:1px solid {border}; color:{text}; padding:4px 12px; border-radius:999px; font-size:12.5px; font-weight:600; margin:3px 6px 3px 0;'>{icon} {escape(s.title())}</span>" for s in skills])
    return f"<div style='margin: 4px 0 10px 0;'>{pills}</div>"

all_skills = sorted({skill.strip() for skills in careers["skills"] for skill in skills.split(",")})
st.sidebar.markdown("## 🧭 CareerCompass AI")
st.sidebar.caption("SMART CAREER GUIDANCE")
st.sidebar.divider()
page = st.sidebar.radio("MENU", ["🏠 Home", "🔎 Career Finder", "📘 How It Works"])

if page == "🏠 Home":
    st.markdown('<div class="hero-box"><span class="hero-badge">AI Career Guidance</span><h1>Discover Your Ideal Career Path 🚀</h1><p>Rate your current skills, test new ones in real time, and download a sleek personalized career report.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="feature-card"><h3>🧠 Skill Level Rating</h3><p>Rate your skills from Beginner to Expert so our AI weighs your strongest abilities accurately.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="feature-card"><h3>🎯 Smart Career Matching</h3><p>Compare your skills with industry roles to find the career paths that fit you best.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="feature-card"><h3>🧪 Skill Growth Simulator</h3><p>Preview how learning missing skills boosts your match score before you start studying.</p></div>', unsafe_allow_html=True)
    st.write("")
    a, b, c = st.columns(3)
    a.metric("Career Paths", len(careers), "Available Roles")
    b.metric("Matching Method", "Weighted AI", "Skill Similarity")
    c.metric("Career Report", "Sleek PDF", "Ready to Download")
    st.info("👈 Open **Career Finder** in the sidebar to start your career match.")

elif page == "🔎 Career Finder":
    st.markdown('<div class="hero-box"><span class="hero-badge">Career Assessment</span><h1>Find Your Ideal Career 🎯</h1><p>Enter your details, rate your skill levels, and explore your top career recommendations.</p></div>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("### 1. Your Profile")
        name = st.text_input("Your Name", placeholder="e.g. Hithesh Kumar")
        education = st.selectbox("Education Level", ["High School", "Diploma", "Undergraduate", "Postgraduate", "Other"])
    with col_r:
        st.markdown("### 2. Your Interests (Optional)")
        interests = st.multiselect("Preferred Career Fields", ["Data Science", "Artificial Intelligence", "Web Development", "Software Development", "Cybersecurity", "Cloud Computing", "App Development", "Design", "Database Management"])
    st.divider()
    st.markdown("### 3. Your Skills & Experience Level")
    selected_skills = st.multiselect("Select the skills you already have", options=all_skills)
    skill_weights = {}
    if selected_skills:
        cols = st.columns(min(len(selected_skills), 3))
        pmap = {"Beginner": 0.7, "Intermediate": 1.0, "Expert": 1.4}
        for idx, skill in enumerate(selected_skills):
            with cols[idx % 3]:
                lvl = st.select_slider(f"**{skill}**", options=["Beginner", "Intermediate", "Expert"], value="Intermediate", key=f"prof_{skill}")
                skill_weights[skill] = pmap[lvl]
    st.write("")
    if st.button("🚀 Find My Ideal Career", use_container_width=True):
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
        best = results.iloc.__getitem__(0)
        st.divider()
        st.markdown(f"## 🏆 Career Matches for {escape(st.session_state['student_name'])}")
        x, y, z = st.columns(3)
        x.metric("Top Career Match", best["career"])
        y.metric("Match Score", f"{best['match_percentage']:.1f}%", "Weighted Fit")
        z.metric("Skills Evaluated", len(st.session_state["skill_weights"]), st.session_state["education"])

        sorted_res = results.sort_values("match_percentage", ascending=True)
        fig = go.Figure(go.Bar(
            x=sorted_res["match_percentage"], y=sorted_res["career"], orientation="h",
            text=[f"<b>{v:.1f}%</b>" for v in sorted_res["match_percentage"]], textposition="outside",
            marker=dict(color=sorted_res["match_percentage"], colorscale=[[0, "#0284C7"], [0.5, "#38BDF8"], [1, "#C084FC"]])
        ))
        fig.update_layout(
            height=330, margin=dict(l=10, r=55, t=15, b=15),
            xaxis=dict(range=list((0, 115)), showgrid=True, gridcolor="rgba(56,189,248,0.12)", color="#94A3B8"),
            yaxis=dict(color="#F8FAFC"),
            plot_bgcolor="rgba(13,19,38,0.75)", paper_bgcolor="rgba(13,19,38,0.75)",
            font=dict(family="Space Grotesk, sans-serif", color="#F8FAFC", size=13)
        )
        st.plotly_chart(fig, use_container_width=True)

        for _, career in results.iterrows():
            m_html = render_skill_badges(career["matched_skills"], "matched")
            u_html = render_skill_badges(career["missing_skills"], "missing")
            st.markdown(f'<div class="career-card"><div class="career-header"><h3 class="career-title">{escape(career["career"])}</h3><span class="match-pill">{career["match_percentage"]:.1f}% Match</span></div><span class="cat-tag">{escape(career["category"])}</span><p style="color:#CBD5E1; font-size:15px;">{escape(career["description"])}</p><div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;"><div><strong style="color:#38BDF8; font-size:13px;">✓ Skills You Have</strong>{m_html}</div><div><strong style="color:#FCD34D; font-size:13px;">+ Skills to Learn</strong>{u_html}</div></div><div class="roadmap-box"><strong style="color:#C084FC;">📚 Learning Roadmap:</strong> {escape(career["learning_path"])}</div></div>', unsafe_allow_html=True)

        st.subheader("🧪 Skill Growth Simulator")
        sim = st.multiselect("Select missing skills to see how learning them boosts your score:", options=[s.title() for s in best["missing_skills"]], key="sim_skills")
        if sim:
            sw = st.session_state["skill_weights"].copy()
            for s in sim: sw[s] = 1.0
            sr = recommend_careers(sw, top_n=15)
            ns = float(sr.loc[sr["career"] == best["career"], "match_percentage"].values)
            st.metric(f"Projected Score for {best['career']}", f"{ns:.1f}%", f"+{round(ns - float(best['match_percentage']), 1)}% boost")

        # FUTURISTIC DARK-MODE PDF REPORT
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=38, leftMargin=38, topMargin=45, bottomMargin=45)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="CyberTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, textColor=colors.HexColor("#38BDF8"), alignment=TA_CENTER, spaceAfter=4))
        styles.add(ParagraphStyle(name="CyberSub", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.HexColor("#C084FC"), alignment=TA_CENTER, spaceAfter=18))
        styles.add(ParagraphStyle(name="SecHead", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, textColor=colors.HexColor("#38BDF8"), spaceBefore=14, spaceAfter=8))
        styles.add(ParagraphStyle(name="CyberBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=14, textColor=colors.HexColor("#E2E8F0"), spaceAfter=5))
        styles.add(ParagraphStyle(name="CardTitle", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#FFFFFF"), spaceAfter=4))

        def fmt(val):
            if isinstance(val, (list, tuple, set)):
                val = ", ".join(str(i).title() for i in val) or "None"
            return escape(str(val))

        story = [
            Paragraph("CAREERCOMPASS AI // CAREER REPORT", styles["CyberTitle"]),
            Paragraph(f"NAME: {escape(st.session_state['student_name']).upper()}  |  EDUCATION: {escape(st.session_state['education']).upper()}", styles["CyberSub"]),
            Paragraph("1. Assessment Summary", styles["SecHead"])
        ]

        hud_table = Table([
            ["TOP CAREER MATCH", "MATCH SCORE", "SKILLS EVALUATED"],
            [str(best["career"]).upper(), f"{best['match_percentage']:.1f}%", str(len(st.session_state["skill_weights"]))]
        ], colWidths=list((210, 140, 165)))
        hud_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#38BDF8")),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#1E293B")),
            ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#FFFFFF")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8.5),
            ("FONTSIZE", (0, 1), (-1, 1), 11),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#38BDF8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155"))
        ]))
        story.append(hud_table)
        story.append(Paragraph("2. Recommended Career Paths", styles["SecHead"]))

        for idx, (_, c) in enumerate(results.iterrows(), 1):
            card_table = Table([[
                Paragraph(f"{idx}. {fmt(c['career']).upper()}  —  [{float(c['match_percentage']):.1f}% MATCH]", styles["CardTitle"])
            ], [
                Paragraph(f"<font color='#C084FC'><b>Field:</b></font> {fmt(c['category'])}<br/>"
                          f"<font color='#94A3B8'>{fmt(c['description'])}</font><br/><br/>"
                          f"<font color='#34D399'><b>Skills You Have:</b></font> {fmt(c['matched_skills'])}<br/>"
                          f"<font color='#FBBF24'><b>Skills to Learn:</b></font> {fmt(c['missing_skills'])}<br/>"
                          f"<font color='#38BDF8'><b>Learning Roadmap:</b></font> {fmt(c['learning_path'])}", styles["CyberBody"])
            ]], colWidths=list((210, 140, 165)))
            card_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E1B4B")),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#0F172A")),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#38BDF8")),
                ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.HexColor("#8B5CF6"))
            ]))
            story.append(KeepTogether([card_table, Spacer(1, 10)]))

        def draw_cyber_bg(canvas, doc):
            canvas.saveState()
            canvas.setFillColor(colors.HexColor("#050814"))
            canvas.rect(0, 0, A4.__getitem__(0), A4.__getitem__(1), fill=1, stroke=0)
            canvas.setStrokeColor(colors.HexColor("#38BDF8"))
            canvas.setLineWidth(1.5)
            canvas.line(38, A4.__getitem__(1) - 32, A4.__getitem__(0) - 38, A4.__getitem__(1) - 32)
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.HexColor("#64748B"))
            canvas.drawString(38, 22, "CareerCompass AI | Personalized Career Report")
            canvas.drawRightString(A4.__getitem__(0) - 38, 22, f"Page {doc.page}")
            canvas.restoreState()

        doc.build(story, onFirstPage=draw_cyber_bg, onLaterPages=draw_cyber_bg)
        st.download_button("📄 Download Career Assessment Report (PDF)", data=pdf_buffer.getvalue(), file_name="CareerCompass_Career_Report.pdf", mime="application/pdf")

elif page == "📘 How It Works":
    st.markdown('<div class="hero-box"><span class="hero-badge">Guide</span><h1>How CareerCompass AI Works</h1><p>Smart skill matching paired with an interactive skill growth simulator.</p></div>', unsafe_allow_html=True)
    st.markdown("- **Skill Level Rating:** Beginner (`0.7x`), Intermediate (`1.0x`), and Expert (`1.4x`) weights adjust your match score based on your real experience.\n- **Skill Growth Simulator:** Test how learning missing skills increases your compatibility for your top career match.")
