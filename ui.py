import streamlit as st
import pandas as pd
import base64
import io
import matplotlib.pyplot as plt
def setup_page():
    """Apply custom CSS and setup page (without setting page config)"""
    # Apply custom CSS only
    apply_custom_css()

st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    var logoImg = document.querySelector('.logo-image');
    if (logoImg) {
        logoImg.onerror = function() {
            var logoContainer = document.querySelector('.logo-container');
            if (logoContainer) {
                logoContainer.innerHTML = '<div style="font-size: 40px;">🚀</div>';
            }
        };
    }
});
</script>
""", unsafe_allow_html=True)

def display_header():
    try:
        with open("maiknit.jpg", "rb") as img_file:
            logo_base64 = base64.b64encode(img_file.read()).decode()
            logo_html = f'<img src="data:image/jpeg;base64, {logo_base64}" alt="MaiKnit Logo" class="logo-image" style="max-height: 100px;">'
    except:
        logo_html = '<div style="font-size: 50px; text-align: center;">🚀</div>'

    st.markdown(f"""
    <div class="main-header">
        <div class="header-container">
                <div class="logo-container" style="text-align: center; margin-bottom: 20px;">
                    {logo_html}
                </div>
                <div class="title-container" style="text-align: center;">
                    <h1>MaiKnit Recruitment Agent</h1>
                    <p>Smart Resume Analysis & Interview Preparation System</p>
                </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def apply_custom_css(accent_color="#d32f2f"):
    st.markdown(f"""
<style>
/* Main container */
.main {{
background-color: #000000 !important;
color: white !important;
}}
                
/* Active tabs and highlights based on accent color */
.stTabs [aria-selected=\"true\"] {{
background-color: #000000 !important;
border-bottom: 3px solid {accent_color} !important;
color: {accent_color} !important;
}}

.stButton>button {{
background-color: {accent_color} !important;
color: white !important;
}}

.stButton>button:hover {{
filter: brightness(85%) ;
}}

div.stAlert {{
background-color: #4a0000 !important;   
color: white !important;
}}

.stTextInput, .stTextArea textarea, .stSelectbox div {{
background-color: #222222 !important;
color: white !important;    
}}

hr {{
border: none;
height: 2px;
background-image: linear-gradient(to right, black 50%,
{accent_color} 50%);
}}

/* General markdown text */
.stMarkdown, stMarkdown p {{
color: white !important;
}}

/* Skill tags styling */
.skill-tag {{
display: inline-block;
background-color: {accent_color};   
color: white;
padding: 5px 10px;
border-radius: 15px;
margin: 2px;
font-weight: bold;
}}

.skill-tag missing {{   
background-color: #444;
color: #ccc;
}}

.strengths-improvement {{
display: flex;
gap: 20px;
}}

.strengths-improvement > div {{
flex: 1;
}}

.card{{
background-color: #111111;
padding: 20px;
border-radius: 10px;
margin-bottom: 20px;
border-left: 4px solid {accent_color};
}}

.improvement-item{{
background-color: #222222;
padding: 15px;  
margin:10px 0;
border-radius: 5px;
}}

.comparison container {{
display: flex;
gap: 20px;
margin-top: 15px;
}}

.comparison-box {{
flex: 1;
background-color: #111111;
padding: 15px;  
border-radius: 5px;
}}

.weakness-detail{{
background-color: #330000;
padding: 10px 15px;
border-radius: 5px;
margin: 5px 0;
border-left: 4px solid #ff6666;
}}

.solution-detail{{  
background-color: #003300;
padding: 10px 15px;
border-radius: 5px;
margin: 5px 0;
border-left: 4px solid #66ff66;
}}

.example-detail{{  
background-color: #000033;
padding: 10px 15px;
border-radius: 5px; 
margin: 5px 0;
border-left: 3px solid #6666ff;
}}

.download-btn {{
display: inline-block;
background-color: {accent_color};    
color: white;
padding: 8px 16px;
border-radius: 5px;
text-decoration: none;
margin: 10px 0;
text-align: center;
}}

.download-btn:hover {{
filter: brightness(85%);
}}

/* Pie chart styling */
.pie-chart-container {{
padding: 10px;
background-color: #111111;
border-radius: 10px;
margin-bottom: 15px;
}}
</style>
""", unsafe_allow_html=True)
    
def setup_sidebar():
    with st.sidebar:
        st.header("Configuration")

        st.subheader("API Keys")
        groq_api_key = st.text_input("Groq API Key (Free at https://console.groq.com)", type="password")
        st.caption("🎉 Free API - No credit card needed!")

        st.markdown("---")

        st.subheader("Theme")
        theme_color= st.color_picker("Accent Color", "#d32f2f")
        st.markdown (f"""
        <style>
        .stButton button, .main-header, .stTabs [aria-selected="true"] {{
        background-color: {theme_color} !important;
        border-color: {theme_color} !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown ("""
        <div style="text-align: center; margin-top: 20px;">
            <p> MaiKnit Recruitment Agent</p>
            <p style="font-size: 0.8rem; color: #666;">v1.0.0 - Powered by Groq</p>
        </div>
        """, unsafe_allow_html=True)

        return {
            "groq_api_key": groq_api_key,
            "theme_color": theme_color
        }
    
def role_selection_section(role_requirements):
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])

        with col1:
            role = st.selectbox("Select the role you're applying for:", list(role_requirements.keys()))
        
        with col2:
            upload_jd = st.checkbox("Upload custom job description instead")
           
        custom_jd = None
        if upload_jd:
            custom_jd_file = st.file_uploader("Upload job description (PDF or TXT)",type=["pdf", "txt"])
            if custom_jd_file:
                st.success("Custom job description uploaded!")
                custom_jd = custom_jd_file

        if not upload_jd:
            st.info (f"Required skills: {', '.join(role_requirements [role])}")
            st.markdown(f"<p>Cutoff Score for selection: <b>{75}/100</b></p>",unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        return role, custom_jd
    
def resume_upload_section():
    st.markdown ("""
    <div class="card">
        <h3> Upload Your Resume</h3>
        <p>Supported format: PDF</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_resume = st.file_uploader("Upload resume (PDF)", type=["pdf"])

    return uploaded_resume

def create_score_pie_chart(score):
    """Create a professional pie chart for the score visualization"""
    fig, ax = plt.subplots(figsize=(4, 4), facecolor='#111111')

    # Data
    sizes = [score, 100 - score]
    labels = ['', ''] # We'll use annotation instead
    colors = ["#d32f2f", "#333333"]
    explode = (0.05, 0) # explode the ft slice (Score)

    # Plot
    wedges, texts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        explode=explode,
        startangle=90,
        wedgeprops={'width': 0.5, 'edgecolor': 'black', 'linewidth': 1}
    )

    #Draw a circle in the center to make it a donut chart
    centre_circle = plt.Circle((0, 0), 0.25, fc='#111111')
    ax.add_artist(centre_circle)

    #Equal aspect ratio ensures that pie is drawn as a circle
    ax.set_aspect('equal')

    #Add score text in the center
    ax.text(0, 0, f"{score}%",
        ha='center', va='center',
        fontsize=24, fontweight='bold',
        color='white')
    
    #Add pass/fail indicator
    status = "PASS" if score >= 75 else "FAIL"
    status_color="#4CAF50" if score >= 75 else "#d32f2f"
    ax.text(0, -0.15, status,
        ha='center', va='center',
        fontsize=14, fontweight='bold',
        color=status_color)
    
    # Set the background color
    ax.set_facecolor('#111111')

    return fig

def display_analysis_results(analysis_result):
    if not analysis_result:
        return
    
    overall_score = analysis_result.get('overall_score', 0)
    selected = analysis_result.get("selected", False)
    skill_scores = analysis_result.get("skill_scores", {})
    detailed_weaknesses = analysis_result.get("detailed_weaknesses", [])

    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown (
    '<div style="text-align: right; font-size: 0.8rem; color: #888; margin-bottom: 10px;">Powered by MaiKnit Recruitment</div>',
    unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Overall Score", f" {overall_score}/100")
        fig = create_score_pie_chart(overall_score)
        st.pyplot(fig)

    with col2:
        if selected:
            st.markdown("<h2 style='color:#4CAF50;'> Congratulations! You have been shortlisted.</h2>", unsafe_allow_html=True)
        else:
            st.markdown("<h2 style='color:#d32f2f;'> Unfortunately, you were not selected.</h2>", unsafe_allow_html=True)
        st.write(analysis_result.get('reasoning', ''))
    
    st.markdown('<hr>', unsafe_allow_html=True)    

    st.markdown("<div class='strengths-improvement'>", unsafe_allow_html=True)

    st.markdown('<div>', unsafe_allow_html=True)
    st.subheader("* Strengths")
    strengths = analysis_result.get("strengths", [])
    if strengths:
        for skill in strengths:
            st.markdown(f'<div class="skill-tag">{skill} ({skill_scores.get(skill, "N/A")}/10)</div>', unsafe_allow_html=True)
    else:
        st.write("No notable strengths identified.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div>', unsafe_allow_html=True)
    st.subheader(" Areas for Improvement")
    missing_skills = analysis_result.get("missing_skills", [])
    if missing_skills:
        for skill in missing_skills:
            st.markdown(f'<div class="skill-tag missing">{skill} ({skill_scores.get(skill, "N/A")}/10)</div>', unsafe_allow_html=True)
    else:
        st.write("No significant areas for improvement.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if detailed_weaknesses:
        st.markdown('<hr>', unsafe_allow_html=True)
        st.subheader(" Detailed Weakness Analysis")

        for weakness in detailed_weaknesses:
            skill_name = weakness.get('skill', '')
            score = weakness.get('score', 0)

            with st.expander(f"{skill_name} (Score: {score}/10)"):
                detail = weakness.get('detail', 'No specific details provided.')
                if detail.startswith('```json') or '{' in detail:
                    detail = "The resume lacks examples of this skill."
                st.markdown(f'<div class="weakness-detail"><strong>Issue:</strong> {detail}</div>',
                unsafe_allow_html=True)
                
                if 'suggestions' in weakness and weakness['suggestions']:
                    st.markdown("<strong>How to improve:</strong>", unsafe_allow_html=True)
                    for i, suggestion in enumerate(weakness['suggestions']):
                        st.markdown(f'<div class="solution-detail">{i+1}. {suggestion}</div>',
                                    unsafe_allow_html=True)
                
                if 'example' in weakness and weakness['example']:
                    st.markdown("<strong>Example addition:</strong>",unsafe_allow_html=True)
                    st.markdown(f'<div class="example-detail">{weakness["example"]}</div>',unsafe_allow_html=True)
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            report_content = f"""
# Overall Score: {overall_score}/100

**Status:** {"Shortlisted" if selected else "Not Selected"}

{analysis_result.get('reasoning', 'No reasoning provided.')}

**Strengths:** {", ".join(strengths) if strengths else "None identified."}

**Areas for Improvement:** {", ".join(missing_skills) if missing_skills else "None identified."}

## Detailed Weakness Analysis
"""
            for weakness in detailed_weaknesses:
                skill_name = weakness.get('skill', '')
                score = weakness.get('score', 0)
                detail = weakness.get('detail', 'No specific details provided.')
                
                if detail.startswith('```json') or '{' in detail:
                    detail = "The resume lacks examples of this skill."
                report_content += f"\n### {skill_name} (Score: {score}/10)\n"
                report_content += f"**Issue:** {detail}\n"

                if 'suggestions' in weakness and weakness['suggestions']:
                    report_content += "\n**Improvement Suggestions:**\n"
                    for i, sugg in enumerate(weakness['suggestions']):
                        report_content += f"- {sugg}\n"

                if 'example' in weakness and weakness['example']:
                    report_content += f"\n**Example:**\n{weakness['example']}\n"

            report_content += "\n---\n*Analysis Provided by MaiKnit Recruitment Agent*"

            report_b64 = base64.b64encode(report_content.encode()).decode()
            href = f'<a class="download-btn" href="data:text/plain;base64,{report_b64}" download="maiknit_resume_analysis.txt">📥 Download Analysis Report</a>'
            st.markdown(href, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
        
def resume_qa_section(has_resume, ask_question_func=None):
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader(" Ask Questions About Your Resume")
    user_question = st.text_input("Enter your question about the resume:", placeholder="What is the candidate's most recent experience?")

    if user_question and ask_question_func:
        with st.spinner ("Searching resume and generating response..."):
            response = ask_question_func(user_question)
            st.markdown('<div style="background-color: #111122; padding: 15px; border-radius: 5px; border-left: 5px solid #d32f2f;">',
            unsafe_allow_html=True)
            st.write(response)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Add example questions
    with st.expander ("Example Questions"):
        example_questions = [
            "What is the candidate's most recent role?",
            "How many years of experience does the candidate have with Python?",
            "What educational qualifications does the candidate have?",
            "What are the candidate's key achievements?",
            "Has the candidate managed teams before?",
            "What projects has the candidate worked on?",
            "Does the candidate have experience with cloud technologies?" 
        ]

        for question in example_questions:
                if st.button(question, key=f"q_{question}"):
                    st.session_state.current_question = question
                    st.experimental_rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def interview_questions_section(has_resume, generate_questions_func=None):
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return

    st.markdown('<div class="card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        question_types = st.multiselect(
            "Select question types:",
            ["Basic", "Technical", "Experience", "Scenario", "Coding", "Behavioral"],
            default=["Basic", "Technical"]
        )

    with col2:
        difficulty = st.select_slider(
            "Question difficulty:",
            options=["Easy", "Medium", "Hard"],
            value="Medium"
        )

    num_questions = st.slider("Number of questions:", 3,15,5)

    if st.button("Generate Interview Questions"):
        if generate_questions_func:
            with st.spinner("Generating interview questions..."):
                questions = generate_questions_func(question_types, difficulty, num_questions)
                st.subheader("Personalized Interview Questions...")
                
                # Create Content for download
                download_content = f"# Interview Questions\n\n"
                download_content += f"Difficulty: {difficulty}\n"
                download_content += f"Types: {', '.join(question_types)}\n\n"
                for i, (q_type, question) in enumerate(questions):
                    with st.expander (f"{q_type}: {question[:50]}..."):
                        st.write(question)
               
                        # For coding questions, add code editor
                        if q_type == "Coding":
                            st.code("# Write your solution here", language="python")
                    
                    download_content += f"## {i+1}. [{q_type}] {question}\n\n"
                    download_content += f"{question}\n\n"
                    if q_type == "Coding":
                        download_content += "```python\n# Write your solution here\n```\n\n"

                download_content += "\n--\nQuestions generated by MaiKnit Recruitment Agent"

                # Add download button
                if questions:
                    st.markdown("---")
                    question_bytes = download_content.encode()
                    b64 = base64.b64encode(question_bytes).decode()
                    href = f'<a class="download-btn" href="data:text/markdown;base64,{b64}" download="maiknit_interview_questions.md">Download All Questions</a>'
                    st.markdown(href, unsafe_allow_html=True)
                
st.markdown('</div>', unsafe_allow_html=True)     

def resume_improvement_section(has_resume, improve_resume_func=None):
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)

    improvement_areas = st.multiselect(
        "Select areas to improve in your resume:",
        ["Content", "Format", "Skills Highlighting", "Experience Description", "Education", "Projects","Achievements","Overall Structure"],
        default=["Content", "Skills Highlighting"]
    )

    target_role = st.text_input("Target role (optional):", placeholder="e.g., Senior Data Scientist at Google")
    if st.button("Generate Resume Improvements"):
        if improve_resume_func:
            with st.spinner("Analyzing and generating improvements..."):
                improvements = improve_resume_func(improvement_areas, target_role)

                # Create content for download
                download_content = f"# MaiKnit Recruitment -Resume Improvement Suggestions\n\nTarget Role: {target_role if target_role else 'Not specified'}\n\n"
                
                for area, suggestions in improvements.items():
                    with st.expander (f"Improvements for {area}", expanded=True):
                        st.markdown (f"<p>{suggestions ['description']}</p>",
                        unsafe_allow_html=True)
                    
                    st.subheader("Specific Suggestions")
                    if "specific" in suggestions:
                        for i, suggestion in enumerate (suggestions ["specific"]): 
                            st.markdown(f'<div class="solution-detail"><strong>{i +1}.</strong> {suggestion}</div>',
                            unsafe_allow_html=True)
                    
                    if "before_after" in suggestions:
                        st.markdown('<div class="comparison-container">',
                        unsafe_allow_html=True)

                        st.markdown('<div class="comparison-box">', unsafe_allow_html=True)
                        st.markdown("<strong>Before:</strong>", unsafe_allow_html=True)
                        st.markdown(f"<pre>{suggestions ['before_after'].get('before', 'N/A')}</pre>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)

                        st.markdown('<div class="comparison-box">', unsafe_allow_html=True)
                        st.markdown("<strong>After:</strong>", unsafe_allow_html=True)
                        st.markdown(f"<pre>{suggestions ['before_after'].get('after', 'N/A')}</pre>", unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    download_content = f"## Improvements for {area}\n\n"
                    download_content += f"{suggestions ['description']}\n\n"
                    download_content += "### Specific Suggestions\n\n"
                    for i, suggestion in enumerate (suggestions ["specific"]):
                        download_content += f"{i+1}. {suggestion}\n"
                    download_content += "\n"

                    if "before_after" in suggestions:
                        download_content += "### Before\n\n"
                        download_content += f"```\n{suggestions ['before_after'] ['before']}\n```\n\n"
                        download_content += "### After\n\n"
                        download_content += f"```\n{suggestions ['before_after'] ['after']}\n```\n\n"

                    download_content += "\n--\nProvided by MaiKnit Recruitment Agent"

                    # Add download button
                    st.markdown("---")
                    report_bytes = download_content.encode()
                    b64 = base64.b64encode(report_bytes).decode()
                    href = f'<a class="download-btn" href="data:text/markdown;base64,{b64}" download="maiknit_resume_improvements.md">📥 Download All Suggestions</a>'
                    st.markdown(href, unsafe_allow_html=True)
              
    st.markdown('</div>', unsafe_allow_html=True)   

def improved_resume_section(has_resume, get_improved_resume_func=None):
    if not has_resume:
        st.warning("Please upload and analyze a resume first.")
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)     

    target_role = st.text_input("Target role:", placeholder="e.g., Senior Software Engineer")
    highlight_skills = st.text_area ("Paste your JD to get updated Resume", placeholder="e.g., Python, React, Cloud Architecture")
    if st.button("Generate Improved Resume"):
        if get_improved_resume_func:
            with st.spinner("Creating improved resume..."):
                improved_resume = get_improved_resume_func(target_role, highlight_skills)

                st.subheader("Improved Resume")
                st.text_area ("Your improved resume:", improved_resume, height=400)
                # Download buttons
                coll, col2 = st.columns (2)
                with coll:
                #Text file download
                    resume_bytes = improved_resume.encode()
                    b64 = base64.b64encode(resume_bytes).decode()
                    href = f'<a class="download-btn" href="data:file/txt;base64, {b64}" download="MaiKnit_improved_resume.txt"> Download as TXT</a>'
                    st.markdown(href, unsafe_allow_html=True)

                with col2:
                    #Markdown file download
                    md_content = f"""# {target_role if target_role else
                    'Professional'} Resume
{improved_resume}

----
Resume enhanced by MaiKnit Recruitment Agent
"""
                    
                    md_bytes = md_content.encode()
                    md_b64 = base64.b64encode(md_bytes).decode()  
                    md_href = f'<a class="download-btn" href="data:text/markdown;base64,{md_b64}" download="maiknit_improved_resume.md">Download as Markdown</a>'
                    st.markdown(md_href, unsafe_allow_html=True)
                    
    st.markdown('</div>', unsafe_allow_html=True)

def create_tabs():
    return st.tabs([
        "Resume Analysis",
        "Resume Q&A",
        "Interview Questions",
        "Resume Improvement",
        "Improved Resume"
    ])