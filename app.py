import streamlit as st
import streamlit.components.v1 as components
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
components.html("""<script>
const d=window.parent.document;if(!d.getElementById("cc")){const c=d.createElement("canvas");c.id="cc";Object.assign(c.style,{position:"fixed",top:0,left:0,width:"100vw",height:"100vh",pointerEvents:"none",zIndex:0});d.body.prepend(c);const x=c.getContext("2d");let w=c.width=window.parent.innerWidth,h=c.height=window.parent.innerHeight,m={x:null,y:null};window.parent.onresize=()=>{w=c.width=window.parent.innerWidth;h=c.height=window.parent.innerHeight};window.parent.onmousemove=e=>{m.x=e.clientX;m.y=e.clientY};const pts=Array.from({length:50},()=>({x:Math.random()*w,y:Math.random()*h,vx:(Math.random()-.5)*.6,vy:(Math.random()-.5)*.6,r:Math.random()*2+1}));(function loop(){x.clearRect(0,0,w,h);pts.forEach((p,i)=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>w)p.vx*=-1;if(p.y<0||p.y>h)p.vy*=-1;x.beginPath();x.arc(p.x,p.y,p.r,0,6.28);x.fillStyle="rgba(56,189,248,.55)";x.fill();for(let j=i+1;j<pts.length;j++){let dist=Math.hypot(p.x-pts[j].x,p.y-pts[j].y);if(dist<130){x.beginPath();x.moveTo(p.x,p.y);x.lineTo(pts[j].x,pts[j].y);x.strokeStyle=`rgba(56,189,248,${.18*(1-dist/130)})`;x.stroke()}}if(m.x!==null){let md=Math.hypot(p.x-m.x,p.y-m.y);if(md<170){x.beginPath();x.moveTo(p.x,p.y);x.lineTo(m.x,m.y);x.strokeStyle=`rgba(192,132,252,${.45*(1-md/170)})`;x.stroke()}}});requestAnimationFrame(loop)})()}
</script>""", height=0, width=0)
st.markdown("""<style>
@import url("https://googleapis.com");
html,body,[class*="css"]{font-family:"Inter",sans-serif!important}h1,h2,h3,.career-title{font-family:"Space Grotesk",sans-serif!important}
header[data-testid="stHeader"]{background:transparent!important}#MainMenu,footer{visibility:hidden}
.stApp{background:radial-gradient(circle at 12% 10%,#0D1B3E 0%,#050814 55%,#090418 100%)!important;color:#F8FAFC!important}
.block-container{max-width:1200px;padding-top:1.5rem;padding-bottom:4rem;position:relative;z-index:1}
[data-testid="stSidebar"]{background:rgba(8,12,26,.88)!important;backdrop-filter:blur(20px)!important;border-right:1px solid rgba(56,189,248,.22)!important}
[data-testid="stSidebar"] *{color:#E2E8F0!important}
[data-testid="stSidebar"] [data-testid="stRadio"] label{background:rgba(30,41,59,.45);border:1px solid rgba(56,189,248,.18);border-radius:12px;padding:12px 16px!important;font-weight:600!important;margin-bottom:8px;transition:all .25s ease}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:rgba(56,189,248,.2);border-color:#38BDF8;box-shadow:0 0 20px rgba(56,189,248,.35);transform:translateX(5px)}
.hero-box{background:linear-gradient(135deg,rgba(13,19,38,.88),rgba(23,37,84,.82) 55%,rgba(88,28,135,.72));backdrop-filter:blur(16px);padding:42px 38px;border-radius:24px;margin-bottom:28px;border:1px solid rgba(56,189,248,.45);box-shadow:0 0 35px rgba(56,189,248,.15)}
.hero-badge{display:inline-block;background:rgba(56,189,248,.16);border:1px solid #38BDF8;color:#38BDF8!important;padding:5px 14px;border-radius:999px;font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:12px}
.hero-box h1{background:linear-gradient(90deg,#FFF,#38BDF8 55%,#C084FC);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:clamp(30px,4vw,44px)!important;font-weight:700!important;margin:0 0 10px!important}
.hero-box p{color:#CBD5E1!important;font-size:16px!important;margin:0!important}
.feature-card,.career-card{background:rgba(13,19,38,.78);backdrop-filter:blur(14px);padding:24px;border-radius:20px;border:1px solid rgba(56,189,248,.24);margin-bottom:16px;transition:all .25s ease}
.feature-card:hover,.career-card:hover{transform:translateY(-4px);border-color:#C084FC;box-shadow:0 12px 32px rgba(168,85,247,.22)}
.career-card{border-left:5px solid #38BDF8}.career-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.career-title{font-size:21px;font-weight:700;color:#F8FAFC;margin:0}
.match-pill{background:rgba(56,189,248,.15);color:#38BDF8;border:1px solid #38BDF8;padding:5px 14px;border-radius:999px;font-weight:700;font-size:13.5px}
.cat-tag{display:inline-block;background:rgba(168,85,247,.16);border:1px solid rgba(192,132,252,.35);color:#D8B4FE;padding:3px 10px;border-radius:6px;font-size:12px;font-weight:600;margin-bottom:10px}
.roadmap-box{background:rgba(5,8,20,.65);border:1px solid rgba(56,189,248,.2);border-radius:12px;padding:12px 16px;margin-top:12px;color:#CBD5E1;font-size:14px}
[data-testid="stMain"] .stButton>button,[data-testid="stMain"] .stDownloadButton>button{background:linear-gradient(90deg,#0284C7,#38BDF8 50%,#8B5CF6)!important;color:#050814!important;border:none!important;border-radius:12px!important;min-height:48px!important;font-weight:800!important;box-shadow:0 0 22px rgba(56,189,248,.45)!important}
[data-testid="stMetric"]{background:rgba(13,19,38,.82)!important;border:1px solid rgba(56,189,248,.25)!important;border-radius:18px!important;padding:16px 20px!important}
[data-testid="stMetricValue"]{color:#38BDF8!important;font-weight:800!important}
</style>""", unsafe_allow_html=True)
careers = load_careers()
def badges(skills, ok=True):
    if not skills: return "<span style='color:#64748B;font-size:13px'>None listed</span>"
    bg, bd, tx, ic = ("rgba(16,185,129,.14)","#10B981","#6EE7B7","✓") if ok else ("rgba(245,158,11,.14)","#F59E0B","#FCD34D","+")
    return "<div>" + "".join([f"<span style='display:inline-block;background:{bg};border:1px solid {bd};color:{tx};padding:4px 11px;border-radius:999px;font-size:12px;font-weight:600;margin:3px 5px 3px 0'>{ic} {escape(s.title())}</span>" for s in skills]) + "</div>"

all_skills = sorted({s.strip() for sk in careers["skills"] for s in sk.split(",")})
st.sidebar.markdown("## 🧭 CareerCompass AI")
st.sidebar.caption("INTERACTIVE CAREER ENGINE")
page = st.sidebar.radio("MENU", ["🏠 Home", "🔎 Career Finder", "📘 How It Works"])

if page == "🏠 Home":
    st.markdown('<div class="hero-box"><span class="hero-badge">Interactive Career Guidance</span><h1>Discover Your Ideal Career Path 🚀</h1><p>Move your cursor across the live network, rate your skills, compare roles head-to-head, and download your personalized report.</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="feature-card"><h3>🧠 Skill Level Rating</h3><p>Rate your skills from Beginner to Expert so our AI weighs your strongest abilities accurately.</p></div>', unsafe_allow_html=True)
    c2.markdown('<div class="feature-card"><h3>🕸️ Interactive Radar & Compare</h3><p>Explore a live spider chart of your top matches and compare any two careers side-by-side.</p></div>', unsafe_allow_html=True)
    c3.markdown('<div class="feature-card"><h3>🧪 Skill Growth Simulator</h3><p>Preview how learning missing skills boosts your match score before you start studying.</p></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.metric("Career Guidance", "Personalized", "Tailored to You")
    b.metric("Visual Analytics", "Radar + Gauge", "Interactive Charts")
    c.metric("Career Report", "Sleek PDF", "Ready to Download")
    st.info("👈 Open **Career Finder** in the sidebar to start your interactive career scan.")
elif page == "🔎 Career Finder":
    st.markdown('<div class="hero-box"><span class="hero-badge">Career Assessment</span><h1>Find Your Ideal Career 🎯</h1><p>Enter your details, rate your skill levels, and explore your interactive career dashboard.</p></div>', unsafe_allow_html=True)
    col_l, col_r = st.columns(2)
    with col_l:
        name = st.text_input("Your Name", placeholder="e.g. Hithesh Kumar")
        education = st.selectbox("Education Level", ["High School", "Diploma", "Undergraduate", "Postgraduate", "Other"])
    with col_r:
        interests = st.multiselect("Preferred Career Fields (Optional)", ["Data Science", "Artificial Intelligence", "Web Development", "Software Development", "Cybersecurity", "Cloud Computing", "App Development", "Design", "Database Management"])
    selected_skills = st.multiselect("Select the skills you already have", options=all_skills)
    skill_weights = {}
    if selected_skills:
        cols = st.columns(min(len(selected_skills), 3))
        pmap = {"Beginner": 0.7, "Intermediate": 1.0, "Expert": 1.4}
        for idx, skill in enumerate(selected_skills):
            with cols[idx % 3]:
                lvl = st.select_slider(f"**{skill}**", options=["Beginner", "Intermediate", "Expert"], value="Intermediate", key=f"prof_{skill}")
                skill_weights[skill] = pmap[lvl]
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
            st.session_state["student_name"], st.session_state["education"], st.session_state["skill_weights"] = name, education, skill_weights
    if "results" in st.session_state:
        results = st.session_state["results"]
        best = results.iloc.__getitem__(0)
        st.divider()
        st.markdown(f"## 🏆 Career Dashboard for {escape(st.session_state['student_name'])}")
        k1, k2 = st.columns(list((1.3, 1)))
        with k1:
            x, y = st.columns(2)
            x.metric("Top Career Match", best["career"])
            y.metric("Skills Evaluated", len(st.session_state["skill_weights"]), st.session_state["education"])
            st.success(f"Your strongest match is **{best['career']}** in **{best['category']}**.")
        with k2:
            gauge = go.Figure(go.Indicator(mode="gauge+number", value=float(best["match_percentage"]), number={"suffix": "%", "font": {"color": "#38BDF8", "size": 34}}, title={"text": "Top Match Readiness", "font": {"color": "#CBD5E1", "size": 14}}, gauge={"axis": {"range": list((0, 100))}, "bar": {"color": "#38BDF8"}, "bgcolor": "rgba(15,23,42,0.6)"}))
            gauge.update_layout(height=210, margin=dict(l=20, r=20, t=35, b=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(gauge, use_container_width=True)

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Visual Analytics", "🗂️ Career Cards", "⚔️ Compare Roles", "🧪 Skill Simulator"])
        with tab1:
            c_bar, c_rad = st.columns(2)
            with c_bar:
                sr = results.sort_values("match_percentage", ascending=True)
                fig = go.Figure(go.Bar(x=sr["match_percentage"], y=sr["career"], orientation="h", text=[f"<b>{v:.1f}%</b>" for v in sr["match_percentage"]], textposition="outside", marker=dict(color=sr["match_percentage"], colorscale=[[0, "#0284C7"], [0.5, "#38BDF8"], [1, "#C084FC"]])))
                fig.update_layout(title="Top 5 Match Scores", height=340, margin=dict(l=10, r=55, t=40, b=15), xaxis=dict(range=list((0, 115)), gridcolor="rgba(56,189,248,0.12)", color="#94A3B8"), yaxis=dict(color="#F8FAFC"), plot_bgcolor="rgba(13,19,38,0.65)", paper_bgcolor="rgba(13,19,38,0.65)", font=dict(color="#F8FAFC"))
                st.plotly_chart(fig, use_container_width=True)
            with c_rad:
                radar = go.Figure(go.Scatterpolar(r=list(results["match_percentage"]) + [results["match_percentage"].iloc.__getitem__(0)], theta=list(results["career"]) + [results["career"].iloc.__getitem__(0)], fill="toself", fillcolor="rgba(56,189,248,0.22)", line=dict(color="#38BDF8", width=2.5)))
                radar.update_layout(title="Career Compatibility Radar", height=340, margin=dict(l=40, r=40, t=40, b=20), polar=dict(bgcolor="rgba(13,19,38,0.65)", radialaxis=dict(range=list((0, 100)), gridcolor="rgba(56,189,248,0.2)", color="#94A3B8"), angularaxis=dict(gridcolor="rgba(56,189,248,0.2)", color="#F8FAFC")), paper_bgcolor="rgba(13,19,38,0.65)", font=dict(color="#F8FAFC"))
                st.plotly_chart(radar, use_container_width=True)
        with tab2:
            for _, career in results.iterrows():
                st.markdown(f'<div class="career-card"><div class="career-header"><h3 class="career-title">{escape(career["career"])}</h3><span class="match-pill">{career["match_percentage"]:.1f}% Match</span></div><span class="cat-tag">{escape(career["category"])}</span><p style="color:#CBD5E1;font-size:15px">{escape(career["description"])}</p><div style="display:grid;grid-template-columns:1fr 1fr;gap:16px"><div><strong style="color:#38BDF8;font-size:13px">✓ Skills You Have</strong>{badges(career["matched_skills"], True)}</div><div><strong style="color:#FCD34D;font-size:13px">+ Skills to Learn</strong>{badges(career["missing_skills"], False)}</div></div><div class="roadmap-box"><strong style="color:#C084FC">📚 Learning Roadmap:</strong> {escape(career["learning_path"])}</div></div>', unsafe_allow_html=True)

        with tab3:
            role_names = list(results["career"])
            if len(role_names) >= 2:
                s1, s2 = st.columns(2)
                r1 = results.loc[results["career"] == s1.selectbox("Select First Career", role_names, index=0)].iloc.__getitem__(0)
                r2 = results.loc[results["career"] == s2.selectbox("Select Second Career", role_names, index=1)].iloc.__getitem__(0)
                ca, cb = st.columns(2)
                for box, role in [(ca, r1), (cb, r2)]:
                    with box:
                        st.markdown(f'<div class="career-card"><div class="career-header"><h3 class="career-title">{escape(role["career"])}</h3><span class="match-pill">{role["match_percentage"]:.1f}%</span></div><span class="cat-tag">{escape(role["category"])}</span><p style="color:#CBD5E1;font-size:14px">{escape(role["description"])}</p><strong>✓ Skills You Have</strong>{badges(role["matched_skills"], True)}<strong>+ Skills to Learn</strong>{badges(role["missing_skills"], False)}<div class="roadmap-box"><strong>📚 Roadmap:</strong> {escape(role["learning_path"])}</div></div>', unsafe_allow_html=True)

        with tab4:
            sim = st.multiselect("Select missing skills to simulate:", options=[s.title() for s in best["missing_skills"]], key="sim_skills")
            if sim:
                sw = st.session_state["skill_weights"].copy()
                for s in sim: sw[s] = 1.0
                sr = recommend_careers(sw, top_n=15)
                ns = float(sr.loc[sr["career"] == best["career"], "match_percentage"].values.__getitem__(0))
                st.metric(f"Projected Score for {best['career']}", f"{ns:.1f}%", f"+{round(ns - float(best['match_percentage']), 1)}% boost")

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, rightMargin=38, leftMargin=38, topMargin=45, bottomMargin=45)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="CyberTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, textColor=colors.HexColor("#38BDF8"), alignment=TA_CENTER, spaceAfter=4))
        styles.add(ParagraphStyle(name="CyberSub", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.HexColor("#C084FC"), alignment=TA_CENTER, spaceAfter=18))
        styles.add(ParagraphStyle(name="SecHead", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, textColor=colors.HexColor("#38BDF8"), spaceBefore=14, spaceAfter=8))
        styles.add(ParagraphStyle(name="CyberBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=14, textColor=colors.HexColor("#E2E8F0"), spaceAfter=5))
        styles.add(ParagraphStyle(name="CardTitle", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=12, textColor=colors.HexColor("#FFFFFF"), spaceAfter=4))
        fmt = lambda v: escape(", ".join(str(i).title() for i in v) or "None") if isinstance(v, (list, tuple, set)) else escape(str(v))
        story = [Paragraph("CAREERCOMPASS AI // CAREER REPORT", styles["CyberTitle"]), Paragraph(f"NAME: {escape(st.session_state['student_name']).upper()}  |  EDUCATION: {escape(st.session_state['education']).upper()}", styles["CyberSub"]), Paragraph("1. Assessment Summary", styles["SecHead"])]
        hud = Table([["TOP CAREER MATCH", "MATCH SCORE", "SKILLS EVALUATED"], [str(best["career"]).upper(), f"{best['match_percentage']:.1f}%", str(len(st.session_state["skill_weights"]))]], colWidths=list((210, 140, 165)))
        hud.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0F172A")),("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#38BDF8")),("BACKGROUND",(0,1),(-1,1),colors.HexColor("#1E293B")),("TEXTCOLOR",(0,1),(-1,1),colors.HexColor("#FFFFFF")),("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),("ALIGN",(0,0),(-1,-1),"CENTER"),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10),("BOX",(0,0),(-1,-1),1.2,colors.HexColor("#38BDF8")),("INNERGRID",(0,0),(-1,-1),0.5,colors.HexColor("#334155"))]))
        story.extend([hud, Paragraph("2. Recommended Career Paths", styles["SecHead"])])
        for idx, (_, c) in enumerate(results.iterrows(), 1):
            ct = Table([[Paragraph(f"{idx}. {fmt(c['career']).upper()}  —  [{float(c['match_percentage']):.1f}% MATCH]", styles["CardTitle"])], [Paragraph(f"<font color='#C084FC'><b>Field:</b></font> {fmt(c['category'])}<br/><font color='#94A3B8'>{fmt(c['description'])}</font><br/><br/><font color='#34D399'><b>Skills You Have:</b></font> {fmt(c['matched_skills'])}<br/><font color='#FBBF24'><b>Skills to Learn:</b></font> {fmt(c['missing_skills'])}<br/><font color='#38BDF8'><b>Learning Roadmap:</b></font> {fmt(c['learning_path'])}", styles["CyberBody"])]], colWidths=list((515,)))
            ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1E1B4B")),("BACKGROUND",(0,1),(-1,1),colors.HexColor("#0F172A")),("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9),("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12),("BOX",(0,0),(-1,-1),0.8,colors.HexColor("#38BDF8")),("LINEBELOW",(0,0),(-1,0),0.8,colors.HexColor("#8B5CF6"))]))
            story.append(KeepTogether([ct, Spacer(1, 10)]))
        def draw_bg(canvas, doc):
            canvas.saveState(); canvas.setFillColor(colors.HexColor("#050814")); canvas.rect(0, 0, A4.__getitem__(0), A4.__getitem__(1), fill=1, stroke=0); canvas.setStrokeColor(colors.HexColor("#38BDF8")); canvas.setLineWidth(1.5); canvas.line(38, A4.__getitem__(1)-32, A4.__getitem__(0)-38, A4.__getitem__(1)-32); canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#64748B")); canvas.drawString(38, 22, "CareerCompass AI | Personalized Career Report"); canvas.drawRightString(A4.__getitem__(0)-38, 22, f"Page {doc.page}"); canvas.restoreState()
        doc.build(story, onFirstPage=draw_bg, onLaterPages=draw_bg)
        st.download_button("📄 Download Career Assessment Report (PDF)", data=pdf_buffer.getvalue(), file_name="CareerCompass_Career_Report.pdf", mime="application/pdf")

elif page == "📘 How It Works":
    st.markdown('<div class="hero-box"><span class="hero-badge">Guide</span><h1>How CareerCompass AI Works</h1><p>Interactive skill matching paired with visual analytics and a skill growth simulator.</p></div>', unsafe_allow_html=True)
    st.markdown("- **Skill Level Rating:** Beginner (`0.7x`), Intermediate (`1.0x`), and Expert (`1.4x`) weights adjust your match score based on your real experience.\n- **Interactive Analytics:** View your top matches on a Radar Chart, Radial Gauge, and Head-to-Head Role Comparison.\n- **Skill Growth Simulator:** Test how learning missing skills increases your compatibility for your top career match.")
