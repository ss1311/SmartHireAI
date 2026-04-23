"""
AI Resume Analyzer - Professional Resume Analysis Tool
Brand New UI/UX Design - Dark Theme with Neon Accents
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime
import re
import base64
from io import BytesIO

# Import utility modules
from utils.text_extraction import extract_text, get_word_count, estimate_reading_time
from utils.skill_matcher import (
    initialize_skill_matcher, extract_skills, categorize_skills, calculate_skill_match
)
from utils.scoring_engine import (
    calculate_resume_strength, get_score_color, get_score_emoji
)


# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for NEW modern UI
def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 3rem 2rem;
        border-radius: 30px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1%, transparent 1%);
        background-size: 50px 50px;
        animation: shimmer 20s linear infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translate(0,0); }
        100% { transform: translate(50px,50px); }
    }
    
    .hero-title {
        font-size: 3.5em;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.2em;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    /* Modern Cards */
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
    }
    
    /* Score Cards */
    .score-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s;
    }
    
    .score-card:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .score-value {
        font-size: 3em;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .score-label {
        font-size: 0.9em;
        color: rgba(255,255,255,0.7);
        margin-top: 0.5rem;
    }
    
    /* Skill Tags - New Colors */
    .skill-tag {
        display: inline-block;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        margin: 0.3rem;
        font-size: 0.85em;
        font-weight: 500;
        transition: all 0.3s;
        cursor: pointer;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .skill-tag:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
    }
    
    .skill-tag-matched {
        background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%);
    }
    
    .skill-tag-missing {
        background: linear-gradient(90deg, #eb3349 0%, #f45c43 100%);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1em;
        transition: all 0.3s;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* File Uploader */
    .upload-area {
        border: 2px dashed #667eea;
        border-radius: 20px;
        padding: 2rem;
        text-align: center;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: rgba(118, 75, 162, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(255,255,255,0.05);
        border-radius: 60px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 50px;
        padding: 0.6rem 1.8rem;
        font-weight: 600;
        color: rgba(255,255,255,0.7);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        font-weight: 600;
        color: white;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2em;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: rgba(255,255,255,0.4);
        font-size: 0.8rem;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 2rem;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Badge */
    .badge {
        display: inline-block;
        background: rgba(102, 126, 234, 0.2);
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.7em;
        color: #667eea;
        margin-left: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    if 'nlp' not in st.session_state:
        st.session_state.nlp = None
        st.session_state.matcher = None
        st.session_state.skills_db = None
    
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = None
        st.session_state.jd_text = None
        st.session_state.resume_skills = []
        st.session_state.jd_skills = []
        st.session_state.analysis_done = False
        st.session_state.analysis_history = []


# Modern Header
def show_header():
    st.markdown("""
    <div class="hero-section">
        <h1 class="hero-title">🎯 AI Resume Analyzer</h1>
        <p class="hero-subtitle">
            Advanced Resume Analysis • Smart Skill Matching • ATS Optimization
            <span class="badge">v3.0</span>
        </p>
    </div>
    """, unsafe_allow_html=True)


# Load skill matcher
@st.cache_resource
def load_skill_matcher():
    with st.spinner("🎯 Initializing AI models..."):
        return initialize_skill_matcher()


# Animated metric display
def display_score_card(label, value, unit="", color="#667eea"):
    st.markdown(f"""
    <div class="score-card">
        <div class="score-value" style="background: linear-gradient(135deg, {color} 0%, #764ba2 100%); -webkit-background-clip: text;">
            {value}{unit}
        </div>
        <div class="score-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)


# Resume upload section
def resume_upload_section():
    st.markdown('<div class="animate">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Your Resume")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose your resume (PDF or DOCX)",
            type=['pdf', 'docx', 'doc'],
            help="Upload your resume in PDF or DOCX format",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("📁 Sample Resume", use_container_width=True):
            st.info("✨ Sample resume feature coming soon!")
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.resume_text = None
            st.rerun()
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]
        
        with st.spinner("📄 Extracting text..."):
            try:
                resume_text = extract_text(uploaded_file, file_type)
                st.session_state.resume_text = resume_text
                
                st.balloons()
                st.success(f"✅ Resume uploaded successfully!")
                
                # Stats row
                col1, col2, col3, col4 = st.columns(4)
                
                word_count = get_word_count(resume_text)
                reading_time = estimate_reading_time(resume_text)
                
                with col1:
                    st.metric("📝 Word Count", word_count)
                with col2:
                    st.metric("⏱️ Reading Time", f"{reading_time} min")
                with col3:
                    st.metric("📏 Characters", len(resume_text))
                with col4:
                    sections = ['experience', 'education', 'skills', 'projects']
                    found = sum(1 for s in sections if s in resume_text.lower())
                    st.metric("📚 Sections", f"{found}/{len(sections)}")
                
                # Preview
                with st.expander("🔍 Preview Extracted Text", expanded=False):
                    st.text_area(
                        "Resume Content",
                        resume_text[:1500] + "..." if len(resume_text) > 1500 else resume_text,
                        height=250,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.session_state.resume_text = None
    
    st.markdown('</div>', unsafe_allow_html=True)
    return st.session_state.resume_text


# Job description section
def job_description_section():
    st.markdown('<div class="animate">', unsafe_allow_html=True)
    st.markdown("### 💼 Job Description")
    
    tab1, tab2 = st.tabs(["📝 Paste Text", "📋 Templates"])
    
    with tab1:
        jd_text = st.text_area(
            "Paste the job description here",
            height=200,
            placeholder="Paste the complete job description you're applying for...",
            help="Include the full job description for best results",
            label_visibility="collapsed"
        )
    
    with tab2:
        st.markdown("**Quick Templates:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💻 Software Engineer", use_container_width=True):
                jd_text = """
                We are looking for a Software Engineer with 3+ years of experience in Python, 
                Machine Learning, and Data Science. Strong knowledge of SQL, Pandas, and Scikit-learn. 
                Experience with cloud platforms (AWS/GCP) is a plus.
                """
                st.session_state.jd_text = jd_text
                st.rerun()
        
        with col2:
            if st.button("📊 Data Scientist", use_container_width=True):
                jd_text = """
                Data Scientist position requiring expertise in Python, Statistics, Deep Learning, 
                and TensorFlow. Must have experience with data visualization, ETL pipelines, 
                and big data technologies.
                """
                st.session_state.jd_text = jd_text
                st.rerun()
    
    if jd_text and len(jd_text) >= 10:
        st.session_state.jd_text = jd_text
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📝 Word Count", get_word_count(jd_text))
        with col2:
            st.metric("📏 Characters", len(jd_text))
    
    st.markdown('</div>', unsafe_allow_html=True)
    return st.session_state.jd_text


# Analysis dashboard
def analysis_dashboard_section(resume_text, jd_text):
    st.markdown("---")
    st.markdown('<div class="animate">', unsafe_allow_html=True)
    st.markdown("### 🔍 Match Analysis")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        analyze_btn = st.button("🚀 Start Analysis", type="primary", use_container_width=True)
    
    if analyze_btn:
        with st.spinner("🤖 AI is analyzing your resume..."):
            try:
                nlp, matcher, skills_db = load_skill_matcher()
                
                # Progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("📊 Extracting skills from resume...")
                progress_bar.progress(20)
                resume_skills = extract_skills(resume_text, matcher, nlp)
                st.session_state.resume_skills = resume_skills
                
                status_text.text("📊 Extracting skills from job description...")
                progress_bar.progress(40)
                jd_skills = extract_skills(jd_text, matcher, nlp)
                st.session_state.jd_skills = jd_skills
                
                status_text.text("📈 Calculating match score...")
                progress_bar.progress(60)
                skill_match = calculate_skill_match(resume_skills, jd_skills)
                
                status_text.text("📊 Evaluating resume strength...")
                progress_bar.progress(80)
                resume_score = calculate_resume_strength(
                    nlp, resume_text, jd_text, resume_skills, jd_skills
                )
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Store results
                st.session_state.skill_match = skill_match
                st.session_state.resume_score = resume_score
                st.session_state.analysis_done = True
                
                st.balloons()
                st.success("✅ Analysis complete! Scroll down to see results.")
                
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                return
    
    if st.session_state.get('analysis_done', False):
        display_results()
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_results():
    """Display comprehensive results"""
    
    skill_match = st.session_state.skill_match
    resume_score = st.session_state.resume_score
    
    st.markdown("---")
    
    # Score cards
    st.markdown("### 📊 Performance Scores")
    
    col1, col2, col3, col4 = st.columns(4)
    
    match_pct = skill_match['match_percentage']
    color1 = "#10b981" if match_pct >= 80 else "#f59e0b" if match_pct >= 60 else "#ef4444"
    
    with col1:
        display_score_card("Match Score", f"{match_pct}", "%", color1)
    
    with col2:
        total_score = int(resume_score['total_score'])
        color2 = "#10b981" if total_score >= 70 else "#f59e0b" if total_score >= 50 else "#ef4444"
        display_score_card("Resume Strength", total_score, "/100", color2)
    
    with col3:
        ats_score = calculate_ats_score_simple(st.session_state.resume_text)
        color3 = "#10b981" if ats_score >= 70 else "#f59e0b" if ats_score >= 50 else "#ef4444"
        display_score_card("ATS Score", ats_score, "/100", color3)
    
    with col4:
        matched_count = skill_match['total_matched']
        total_jd = skill_match['total_jd_skills']
        display_score_card("Skills Matched", f"{matched_count}/{total_jd}", "", "#667eea")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Skill Analysis", 
        "📈 Score Details", 
        "📊 Visual Analytics", 
        "💡 Recommendations"
    ])
    
    with tab1:
        display_skill_analysis()
    
    with tab2:
        display_detailed_scores()
    
    with tab3:
        display_visual_analytics()
    
    with tab4:
        display_recommendations()


def display_skill_analysis():
    """Display skill analysis"""
    
    skill_match = st.session_state.skill_match
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ Matched Skills")
        st.markdown(f'<span class="badge">{len(skill_match["matched_skills"])} skills found</span>', unsafe_allow_html=True)
        st.markdown("---")
        
        if skill_match['matched_skills']:
            categorized = categorize_skills(
                skill_match['matched_skills'],
                st.session_state.skills_db
            )
            
            for category, skills in categorized.items():
                if skills:
                    st.markdown(f"**{category.replace('_', ' ').title()}**")
                    skills_html = " ".join([f'<span class="skill-tag skill-tag-matched">{s}</span>' for s in skills[:15]])
                    st.markdown(skills_html, unsafe_allow_html=True)
                    if len(skills) > 15:
                        st.caption(f"+ {len(skills) - 15} more")
                    st.markdown("---")
        else:
            st.info("No matched skills found")
    
    with col2:
        st.markdown("#### ❌ Missing Skills")
        st.markdown(f'<span class="badge">{len(skill_match["missing_skills"])} skills to add</span>', unsafe_allow_html=True)
        st.markdown("---")
        
        if skill_match['missing_skills']:
            categorized = categorize_skills(
                skill_match['missing_skills'],
                st.session_state.skills_db
            )
            
            for category, skills in categorized.items():
                if skills:
                    st.markdown(f"**{category.replace('_', ' ').title()}**")
                    skills_html = " ".join([f'<span class="skill-tag skill-tag-missing">{s}</span>' for s in skills[:15]])
                    st.markdown(skills_html, unsafe_allow_html=True)
                    if len(skills) > 15:
                        st.caption(f"+ {len(skills) - 15} more")
                    st.markdown("---")
        else:
            st.success("🎉 Perfect match! You have all required skills!")


def display_detailed_scores():
    """Display detailed scores"""
    
    resume_score = st.session_state.resume_score
    
    components = {
        '🎨 Keyword Density': resume_score.get('keyword_density', 0),
        '🎯 Skill Alignment': resume_score.get('skill_alignment', 0),
        '💼 Experience Relevance': resume_score.get('experience_relevance', 0),
        '📏 Length Optimization': resume_score.get('length_optimization', 0),
        '✨ Formatting': resume_score.get('formatting_score', 0)
    }
    
    for component, score in components.items():
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.markdown(f"**{component}**")
        
        with col2:
            percent = (score / 30 * 100) if component == '🎨 Keyword Density' else score
            st.progress(min(percent / 100, 1.0))
            st.caption(f"{score}/30" if component == '🎨 Keyword Density' else f"{score}/100")
    
    st.markdown("---")
    st.markdown("#### 📝 AI Feedback")
    
    feedbacks = resume_score.get('feedback', [])
    if feedbacks:
        for feedback in feedbacks:
            if "✅" in feedback:
                st.success(feedback)
            elif "⚠️" in feedback:
                st.warning(feedback)
            else:
                st.info(feedback)
    else:
        st.info("No specific feedback available")


def display_visual_analytics():
    """Display visual analytics"""
    
    skill_match = st.session_state.skill_match
    resume_skills = st.session_state.resume_skills
    jd_skills = st.session_state.jd_skills
    
    # Radar chart
    st.markdown("#### 🎯 Skill Category Distribution")
    
    resume_categorized = categorize_skills(resume_skills, st.session_state.skills_db)
    jd_categorized = categorize_skills(jd_skills, st.session_state.skills_db)
    
    all_categories = set(list(resume_categorized.keys()) + list(jd_categorized.keys()))
    
    if all_categories:
        categories = []
        resume_counts = []
        jd_counts = []
        
        for cat in all_categories:
            categories.append(cat.replace('_', ' ').title())
            resume_counts.append(len(resume_categorized.get(cat, [])))
            jd_counts.append(len(jd_categorized.get(cat, [])))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=jd_counts,
            theta=categories,
            fill='toself',
            name='Job Description',
            line=dict(color='#f093fb', width=2),
            fillcolor='rgba(240, 147, 251, 0.3)'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=resume_counts,
            theta=categories,
            fill='toself',
            name='Your Resume',
            line=dict(color='#4facfe', width=2),
            fillcolor='rgba(79, 172, 254, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, max(max(jd_counts), max(resume_counts)) + 2])
            ),
            showlegend=True,
            template="plotly_dark",
            height=450,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for radar chart")
    
    st.markdown("---")
    
    # Word cloud
    st.markdown("#### ☁️ Missing Skills Word Cloud")
    
    missing_skills = skill_match.get('missing_skills', [])
    
    if missing_skills:
        try:
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='#1a1a2e',
                colormap='plasma',
                relative_scaling=0.5,
                min_font_size=10,
                max_words=50
            ).generate(' '.join(missing_skills))
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            plt.tight_layout(pad=0)
            
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error creating word cloud: {str(e)}")
    else:
        st.success("🎉 No missing skills! Perfect match!")


def display_recommendations():
    """Display recommendations"""
    
    skill_match = st.session_state.skill_match
    missing_skills = skill_match.get('missing_skills', [])
    
    st.markdown("#### 💡 Actionable Recommendations")
    
    if missing_skills:
        st.markdown("**🔴 High Priority - Add These Skills**")
        
        for skill in missing_skills[:8]:
            st.markdown(f"- **{skill}** - Add this to your skills section")
        st.markdown("---")
    
    st.markdown("**📝 Resume Improvement Tips**")
    
    tips = [
        "✨ Add quantifiable achievements (e.g., 'Increased efficiency by 30%')",
        "⚡ Use strong action verbs (Managed, Led, Developed, Created)",
        "🎯 Tailor your resume for each job application",
        "📜 Include relevant certifications and courses",
        "🔧 Keep formatting simple for ATS compatibility",
        "📊 Use numbers and metrics to showcase impact",
        "🏆 Highlight leadership and teamwork experience"
    ]
    
    for tip in tips:
        st.markdown(f"- {tip}")
    
    st.markdown("---")
    
    # Download report
    if st.button("📥 Download Full Report", use_container_width=True):
        report = generate_report()
        st.download_button(
            label="💾 Save Report (TXT)",
            data=report,
            file_name=f"resume_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )


def calculate_ats_score_simple(text):
    """Calculate ATS score"""
    score = 70
    
    sections = ['experience', 'education', 'skills', 'summary']
    for section in sections:
        if section in text.lower():
            score += 5
    
    if re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text):
        score += 5
    if re.search(r'\b\d{10}\b|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
        score += 5
    
    action_verbs = ['managed', 'created', 'developed', 'led', 'achieved', 'improved']
    for verb in action_verbs:
        if verb in text.lower():
            score += 2
    
    return min(score, 100)


def generate_report():
    """Generate report"""
    
    skill_match = st.session_state.skill_match
    resume_score = st.session_state.resume_score
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    AI RESUME ANALYSIS REPORT                  ║
║              Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERALL SCORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Match Score:           {skill_match['match_percentage']}%
Resume Strength:       {int(resume_score['total_score'])}/100
ATS Compatibility:     {calculate_ats_score_simple(st.session_state.resume_text)}/100

🎯 SKILL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total JD Skills:       {skill_match['total_jd_skills']}
Skills in Resume:      {skill_match['total_resume_skills']}
Matched Skills:        {skill_match['total_matched']}
Missing Skills:        {skill_match['total_missing']}

✅ MATCHED SKILLS:
{chr(10).join(f'  • {s}' for s in skill_match['matched_skills'][:20]) if skill_match['matched_skills'] else '  None'}

❌ MISSING SKILLS:
{chr(10).join(f'  • {s}' for s in skill_match['missing_skills'][:20]) if skill_match['missing_skills'] else '  None'}

📈 SCORE BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Keyword Density:       {resume_score.get('keyword_density', 0)}/30
Skill Alignment:       {resume_score.get('skill_alignment', 0)}/30
Experience Relevance:  {resume_score.get('experience_relevance', 0)}/20
Length Optimization:   {resume_score.get('length_optimization', 0)}/10
Formatting:            {resume_score.get('formatting_score', 0)}/10

💡 RECOMMENDATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Add missing skills to your resume
2. Include quantifiable achievements
3. Use strong action verbs
4. Optimize for ATS with simple formatting
5. Tailor resume for each application

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated by AI Resume Analyzer v3.0
"""
    
    return report


# Sidebar
def sidebar():
    with st.sidebar:
        st.markdown("### 🎯 Quick Stats")
        
        if st.session_state.resume_text:
            st.success("✅ Resume Loaded")
        else:
            st.info("📄 No Resume")
        
        if st.session_state.jd_text:
            st.success("✅ JD Loaded")
        else:
            st.info("💼 No JD")
        
        if st.session_state.get('analysis_done'):
            st.success("✅ Analysis Done")
            if 'skill_match' in st.session_state:
                st.metric("🎯 Match Score", f"{st.session_state.skill_match['match_percentage']}%")
        else:
            st.info("🔍 Pending")
        
        st.markdown("---")
        st.markdown("### 🛠️ Features")
        st.markdown("""
        - ✅ Smart Skill Matching
        - ✅ ATS Score Check
        - ✅ Visual Analytics
        - ✅ Detailed Reports
        - ✅ Actionable Tips
        """)
        
        st.markdown("---")
        
        if st.button("🔄 Reset Everything", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['nlp', 'matcher', 'skills_db']:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        st.caption("Made with ❤️ using AI & Streamlit")


# Footer
def footer():
    st.markdown("""
    <div class="footer">
        <p>⚡ AI Resume Analyzer v3.0 | Powered by Machine Learning & NLP</p>
        <p>Upload your resume and job description to get instant analysis and recommendations</p>
    </div>
    """, unsafe_allow_html=True)


# Main app
def main():
    apply_custom_css()
    init_session_state()
    
    show_header()
    
    # Load skill matcher
    if st.session_state.nlp is None:
        try:
            nlp, matcher, skills_db = load_skill_matcher()
            st.session_state.nlp = nlp
            st.session_state.matcher = matcher
            st.session_state.skills_db = skills_db
        except Exception as e:
            st.error(f"Failed to initialize AI models: {str(e)}")
            st.stop()
    
    sidebar()
    
    resume_text = resume_upload_section()
    
    if resume_text:
        jd_text = job_description_section()
        
        if jd_text:
            analysis_dashboard_section(resume_text, jd_text)
    
    footer()


if __name__ == "__main__":
    main()