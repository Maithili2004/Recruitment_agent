import re
from urllib import response
import PyPDF2 
import io

from click import prompt
from langchain.embeddings.base import Embeddings
from langchain_community.vectorstores import FAISS
from groq import Groq
import numpy as np

# Simple embeddings using TF-IDF style approach (no torch needed)
class SimpleEmbeddings(Embeddings):
    """Simple embeddings using hash-based vectors"""
    def embed_documents(self, texts):
        """Embed a list of texts"""
        embeddings = []
        for text in texts:
            # Create a simple embedding from text
            hash_val = hash(text) % 10000
            embedding = np.random.RandomState(hash_val).randn(384).tolist()
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text):
        """Embed a single query"""
        hash_val = hash(text) % 10000
        return np.random.RandomState(hash_val).randn(384).tolist()
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os
import json

class ResumeAnalysisAgent:
    def __init__(self, groq_api_key, cutoff_score=75):
        self.groq_api_key = groq_api_key
        self.cutoff_score = cutoff_score
        self.groq_client = Groq(api_key=groq_api_key)
        self.resume_text = None
        self.rag_vectorstore = None
        self.analysis_result = None
        self.jd_text = None
        self.extracted_skills = None
        self.resume_weaknesses = []
        self.resume_strengths = []
        self.improvement_suggestions = {}

    def call_groq_llm(self, prompt):
        """Call Groq LLM to generate a response"""
        try:
            message = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
            )
            return message.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            # Check if it's an API key issue
            if "401" in error_msg or "invalid_api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                return "ERROR: Invalid Groq API Key. Please check your API key at https://console.groq.com/keys"
            elif "decommissioned" in error_msg.lower():
                return "ERROR: Model temporarily unavailable. Please try again later."
            else:
                return f"ERROR: {error_msg[:100]}"

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file"""
        try:
            if hasattr(pdf_file, 'getvalue'):
                pdf_data = pdf_file.getvalue()
                pdf_file_like = io.BytesIO(pdf_data)
                reader = PyPDF2.PdfReader(pdf_file_like)
            else:
                reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
        
            for page in reader.pages:
                text += page.extract_text()    
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

    def extract_text_from_txt(self, txt_file):
        """Extract text from a text file"""
        try:
            if hasattr(txt_file, 'getvalue'):
                return txt_file.getvalue().decode('utf-8')
            else:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            print(f"Error extracting text from text file: {e}")
        return ""
    
    def extract_text_from_file(self, file):
        """Extract text from a file (PDF or TXT)"""
        if hasattr(file, 'name'):
            file_extension = file.name.split('.')[-1].lower()
        else:
            file_extension = file.split('.')[-1].lower()
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(file)
        elif file_extension == 'txt':
            return self.extract_text_from_txt(file)
        else:
            print(f"Unsupported file extension: {file_extension}")
            return ""
        
    def create_rag_vector_store(self, text):
        """Create a vector store for RAG"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        embeddings = SimpleEmbeddings()
        vectorstore = FAISS.from_texts(chunks, embeddings)
        return vectorstore
    
    def create_vector_store(self, text):
        """Create a simpler vector store for skill analysis"""
        embeddings = SimpleEmbeddings()
        vectorstore = FAISS.from_texts([text], embeddings)
        return vectorstore
    
    def analyze_skill(self, qa_chain, skill):
        """Analyze a skill in the resume"""
        query = f"On a scale of 0-10, how clearly does the candidate mention proficiency in {skill}? Provide a numeric rating first, followed by reasoning."
        response = qa_chain.run(query)
        match = re.search(r" (\d{1,2})", response)
        score = int(match.group(1)) if match else 0
        reasoning = response.split('.', 1)[1].strip() if '.' in response and len(response.split('.')) > 1 else ""
        return skill, min(score, 10), reasoning
    
    def analyze_resume_weaknesses (self):
        """Analyze weaknesses in the resume based on missing skills"""
        if not self.resume_text or not self.extracted_skills or not self.analysis_result:
            return []
        
        weaknesses = []
        # Limit to top 3 missing skills to avoid timeout
        missing_skills = self.analysis_result.get("missing_skills", [])[:3]
        
        for skill in missing_skills:
            prompt = f"""For the skill "{skill}", provide improvement suggestions.

The resume lacks this skill or has minimal evidence.

Provide improvements in this EXACT format:
Issue: [one sentence problem]
Solution 1: [specific suggestion]
Solution 2: [specific suggestion]  
Solution 3: [specific suggestion]

Example resume excerpt:
{self.resume_text[:800]}"""
            
            try:
                weakness_content = self.call_groq_llm(prompt)
                
                # Parse structured response
                lines = weakness_content.split('\n')
                weakness_desc = "Needs improvement"
                suggestions = ["Add more details", "Include examples", "Use industry keywords"]
                
                for line in lines:
                    if line.strip().startswith("Issue:"):
                        weakness_desc = line.replace("Issue:", "").strip()
                    elif line.strip().startswith("Solution"):
                        suggestion_text = line.split(":", 1)[1].strip() if ":" in line else ""
                        if suggestion_text:
                            suggestions.append(suggestion_text)
                
                # Keep only first 3 suggestions
                suggestions = suggestions[:3]

                weakness_detail = {
                    "skill": skill,
                    "score": self.analysis_result.get("skill_scores", {}).get(skill, 0),
                    "detail": weakness_desc,
                    "suggestions": suggestions,
                    "example": ""
                }

                weaknesses.append(weakness_detail)
                self.improvement_suggestions[skill] = {"suggestions": suggestions}
            except Exception as e:
                # Fallback weakness if error occurs
                weakness_detail = {
                    "skill": skill,
                    "score": self.analysis_result.get("skill_scores", {}).get(skill, 0),
                    "detail": f"Limited evidence of {skill} in resume",
                    "suggestions": ["Learn and practice this skill", "Add projects using this skill", "Get certifications"],
                    "example": ""
                }
                weaknesses.append(weakness_detail)
                continue
        
        self.resume_weaknesses = weaknesses
        return weaknesses
    
    def extract_skills_from_jd(self, jd_text):
        """Extract skills from a job description"""
        try:
            prompt = f"""
            Extract a comprehensive list of technical skills, technologies, and
            competencies required from this job description.
            Format the output as a Python list of strings. Only include the list, nothing else.
            
            Job Description:
            {jd_text}
            """
            skills_text = self.call_groq_llm(prompt)
            
            match = re.search(r'\[(.*?)\]', skills_text, re.DOTALL)
            if match:
                skills_text = match.group(0)

                try:
                    skills_list = eval(skills_text)
                    if isinstance(skills_list, list):
                        return skills_list
                except:
                    pass

            skills = []
            for line in skills_text.split('\n'):
                line = line.strip()
                if line.startswith('-') or line.startswith('*'):
                    skill = line[2:].strip()
                    if skill:
                        skills.append(skill)
                elif line.startswith('"') and line.endswith('"'):
                    skill = line.strip('"')
                    if skill:
                        skills.append(skill)
            return skills
        except Exception as e:
            print(f"Error extracting skills from JD: {e}")
            return []
        
    def semantic_skill_analysis(self, resume_text, skills):
        """Analyze skills using Groq"""
        if not skills:
            return {
                "overall_score": 0,
                "skill_scores": {},
                "skill_reasoning": {},
                "strengths": [],
                "missing_skills": []
            }
        
        skill_scores = {}
        skill_reasoning = {}
        missing_skills = []
        total_score = 0

        for skill in skills:
            resume_lower = resume_text.lower()
            skill_lower = skill.lower()
            
            # Check if skill is mentioned in resume
            skill_found = (skill_lower in resume_lower or 
                          skill_lower.replace(" ", "") in resume_lower.replace(" ", ""))
            
            if not skill_found:
                # Not mentioned = score 1
                score = 1
                skill_reasoning_text = "Not mentioned in resume"
            else:
                # Count mentions and analyze depth
                skill_count = resume_lower.count(skill_lower)
                
                # Score based on mention frequency and depth
                # This is DETERMINISTIC - no LLM subjectivity
                if skill_count >= 5:
                    # Mentioned 5+ times = strong evidence of expertise
                    score = 8
                    skill_reasoning_text = f"Mentioned {skill_count} times - strong experience"
                elif skill_count >= 3:
                    # Mentioned 3-4 times = moderate experience
                    score = 6
                    skill_reasoning_text = f"Mentioned {skill_count} times - moderate experience"
                elif skill_count >= 2:
                    # Mentioned twice = some experience
                    score = 4
                    skill_reasoning_text = f"Mentioned {skill_count} times - basic experience"
                else:
                    # Mentioned once = minimal mention
                    score = 2
                    skill_reasoning_text = "Mentioned once - minimal evidence"
            
            skill_scores[skill] = score
            skill_reasoning[skill] = skill_reasoning_text
            total_score += score
            if score <= 4:
                missing_skills.append(skill)

        # Calculate overall score properly
        if skills:
            overall_score = int((total_score / (10 * len(skills))) * 100)
            overall_score = min(100, max(0, overall_score))  # Ensure between 0-100
        else:
            overall_score = 0
            
        selected = overall_score >= self.cutoff_score

        reasoning = "Candidate evaluated based on resume content"
        strengths = [skill for skill, score in skill_scores.items() if score >= 7]  # Strengths at 7+ (strong evidence)
        improvement_areas = missing_skills if not selected else []
        
        self.resume_strengths = strengths

        return {
            "overall_score": overall_score,
            "skill_scores": skill_scores,
            "skill_reasoning": skill_reasoning,
            "selected": selected,
            "reasoning": reasoning,
            "missing_skills": missing_skills,
            "strengths": strengths,
            "improvement_areas": improvement_areas
        }
    
    def analyze_resume(self, resume_file, role_requirements=None, custom_jd=None):
        """Analyze a resume against role requirements or a custom JD"""
        self.resume_text = self.extract_text_from_file(resume_file)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w',
        encoding='utf-8') as tmp:
            tmp.write(self.resume_text)
            self.resume_file_path = tmp.name

        self.rag_vectorstore = self.create_rag_vector_store(self.resume_text)

        if custom_jd:
            self.jd_text = self.extract_text_from_file(custom_jd)
            self.extracted_skills = self.extract_skills_from_jd(self.jd_text)
                    
            self.analysis_result = self.semantic_skill_analysis(self.resume_text, self.extracted_skills)
                
        elif role_requirements:
            self.extracted_skills = role_requirements
            
            self.analysis_result = self.semantic_skill_analysis(self.resume_text, role_requirements)

        if self.analysis_result and "missing_skills" in self.analysis_result and self.analysis_result["missing_skills"]:
            self.analyze_resume_weaknesses()
            
            self.analysis_result ["detailed_weaknesses"] = self.resume_weaknesses
        
        return self.analysis_result
    
    def ask_question(self, question):
        """Ask a question about the resume using Groq"""
        if not self.resume_text:
            return "Please analyze a resume first."
        
        prompt = f"""
        Answer this question about the resume: {question}
        
        Resume:
        {self.resume_text[:2000]}
        """
        return self.call_groq_llm(prompt)
    
    def generate_interview_questions(self, question_types, difficulty, num_questions):
        """Generate interview questions based on the resume"""
        if not self.resume_text or not self.extracted_skills:
            return []
        try:
            context = f"""
Resume Content:
{self.resume_text[:1500]}

Skills to focus on: {', '.join(self.extracted_skills[:10])}
Strengths: {', '.join(self.analysis_result.get('strengths', []))}
Areas for improvement: {', '.join(self.analysis_result.get('missing_skills', []))}
"""
           
            prompt = f"""Generate {num_questions} personalized {difficulty.lower()} level interview questions for this candidate.
Include ONLY these question types: {', '.join(question_types)}.

For each question:
1. Start with [Type: <type>]
2. Then write the question

{context}

Format each question on a new line starting with [Type: ...]"""

            questions_text = self.call_groq_llm(prompt)

            questions = []
            current_type = None
            
            for line in questions_text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if line starts with [Type:
                if line.startswith('[Type:'):
                    # Extract type from [Type: <type>]
                    type_match = re.search(r'\[Type:\s*([^\]]+)\]', line)
                    if type_match:
                        type_name = type_match.group(1).strip()
                        # Check if this type is in requested types
                        for req_type in question_types:
                            if req_type.lower() in type_name.lower():
                                current_type = req_type
                                # Get question text from same line if present
                                question_text = line.split(']', 1)[1].strip() if ']' in line else ""
                                if question_text:
                                    questions.append((current_type, question_text))
                                break
                elif current_type and line:
                    # This is a continuation of the question
                    if questions and questions[-1][0] == current_type:
                        # Append to last question
                        q_type, q_text = questions[-1]
                        questions[-1] = (q_type, q_text + " " + line)
                    else:
                        questions.append((current_type, line))

            # Limit to requested number
            questions = questions[:num_questions]
            
            # If no questions parsed, return at least default ones
            if not questions:
                for q_type in question_types[:num_questions]:
                    questions.append((q_type, f"Tell me about your experience with {q_type.lower()}."))
            
            return questions
        
        except Exception as e:
            print(f"Error generating interview questions: {e}")
            return []
        
    def improve_resume(self, improvement_areas, target_role=""):
        """Generate suggestions to improve the resume"""
        if not self.resume_text:
            return {}
        
        try:
            
            improvements = {}
        
            for area in improvement_areas:
                if area == "Skills Highlighting" and self.resume_weaknesses:
                    skill_improvements = {
                    "description": "Your resume needs to better highlight key skills that are important for the role.",
                    "specific": []
                    }
                
                    before_after_examples = {}

                    for weakness in self.resume_weaknesses:
                        skill_name  = weakness.get("skill", "")
                        if "suggestions" in weakness and weakness ["suggestions"]:
                            for suggestion in weakness ["suggestions"]:
                                skill_improvements ["specific"].append(f"**{skill_name}**: {suggestion}")

                        if "example" in weakness and weakness ["example"]:
                            resume_chunks = self.resume_text.split('\n\n')
                            relevant_chunk = ""
                            for chunk in resume_chunks:
                                if skill_name.lower() in chunk.lower() or "experience" in chunk.lower():
                                    relevant_chunk = chunk
                                    break
                                    
                            if relevant_chunk:
                                before_after_examples = {
                                "before": relevant_chunk.strip(),
                                "after": relevant_chunk.strip() + "\n• " +
                                weakness ["example"]
                                }
                                
                    if before_after_examples:
                        skill_improvements ["before_after"] = before_after_examples 

                    improvements["Skills Highlighting"] = skill_improvements   
            remaining_areas = [area for area in improvement_areas if area not in improvements]
            if remaining_areas:
                # Use Groq LLM instead of ChatOpenAI
                weaknesses_text = ""
                if self.resume_weaknesses:
                    weaknesses_text = "Resume Weaknesses:\n"
                    for i, weakness in enumerate(self.resume_weaknesses):
                        weaknesses_text += f"{i+1}. {weakness ['skill']}: {weakness['detail']}\n"
                        if "suggestions" in weakness:
                            for j, sugg in enumerate (weakness ["suggestions"]):
                                weaknesses_text += f" - {sugg}\n"
                context = f"""
                Resume Content (first 1000 chars):
                {self.resume_text[:1000]}

                Skills to focus on: {', '.join(self.extracted_skills[:10])}
                Strengths: {', '.join(self.analysis_result.get('strengths', []))}
                Areas for improvement: {', '.join(self.analysis_result.get('missing_skills', []))}
                {weaknesses_text}

                Target Role: {target_role if target_role else "Not specified"}
                """
                prompt = f"""Improve this resume in these areas: {', '.join(remaining_areas[:3])}.

{context}

For EACH improvement area, provide:
1. description: What needs improvement
2. specific: List of 3-5 actionable suggestions
3. before_after: Example with "before" and "after" text

Output ONLY valid JSON:
{{
  "area_name": {{
    "description": "text",
    "specific": ["suggestion1", "suggestion2"],
    "before_after": {{"before": "old example", "after": "improved example"}}
  }}
}}"""

                improve_text = self.call_groq_llm(prompt)

                ai_improvements = {}

                # Extract from markdown code blocks if present
                json_match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', improve_text)
                if not json_match:
                    json_match = re.search(r'\{[\s\S]*\}', improve_text)
                    
                if json_match:
                    try:
                        ai_improvements = json.loads(json_match.group(0) if json_match.group(0).startswith('{') else json_match.group(1))
                        # Merge with existing improvements
                        improvements.update(ai_improvements)
                    except (json.JSONDecodeError, AttributeError, IndexError):
                        pass
                
                # If JSON parsing failed, create basic improvements
                if not ai_improvements:
                    for area in remaining_areas:
                        improvements[area] = {
                            "description": f"Enhance {area} in your resume",
                            "specific": [f"Add more details about {area}", f"Include quantifiable achievements", f"Use industry keywords"],
                            "before_after": {"before": "Generic description", "after": "Specific, measurable achievement"}
                        }

            for area in improvement_areas:
                if area not in improvements:
                    improvements [area] = {
                        "description": f"Improvements needed in {area}",
                        "specific": ["Review and enhance this section"]
                    }
            
            return improvements
        
        except Exception as e:
            print(f"Error generating resume improvements: {e}")
            return {area: {"description": "Error generating improvements", "specific": []} for area in improvement_areas}
        
    def get_improved_resume(self, target_role="", highlight_skills=""):
        """Generate an improved version of the resume optimized for the job description"""
        if not self.resume_text:
            return "Please upload and analyze a resume first."
        
        try:
            # Parse highlight skills if provided
            skills_to_highlight = []
            if highlight_skills:
                if len(highlight_skills) > 100:
                    self.jd_text = highlight_skills
                    try:
                        parsed_skills = self.extract_skills_from_jd(highlight_skills)
                        if parsed_skills:
                            skills_to_highlight = parsed_skills
                        else:
                            skills_to_highlight = [s.strip() for s in highlight_skills.split(",") if s.strip()]
                    except:
                        skills_to_highlight = [s.strip() for s in highlight_skills.split(",") if s.strip()]
                else:
                    skills_to_highlight = [s.strip() for s in highlight_skills.split(",") if s.strip()]
            if not skills_to_highlight and self.analysis_result:
               
                skills_to_highlight = self.analysis_result.get('missing_skills', [])
                
                skills_to_highlight.extend([
                    skill for skill in self.analysis_result.get('strengths', [])
                    if skill not in skills_to_highlight
                ])

                if self.extracted_skills:
                    skills_to_highlight.extend([
                        skill for skill in self.extracted_skills
                        if skill not in skills_to_highlight
                    ])

            weakness_context =""
            improvement_examples = ""

            if self.resume_weaknesses:
                weakness_context = "Address these specific weaknesses: \n"
                
                for weakness in self.resume_weaknesses:
                    skill_name = weakness.get('skill', '')
                    weakness_context += f"- {skill_name}: {weakness.get('detail','')}\n"       

                    if 'suggestions' in weakness and weakness ['suggestions']:
                        weakness_context += "Suggested improvements:\n"
                        for suggestion in weakness ['suggestions']:
                            weakness_context += f" * {suggestion}\n"
                        
                        if 'example' in weakness and weakness ['example']:
                            improvement_examples + f"For (skill_name): {weakness['example']}\n\n"
                        
            jd_context = ""

            if self.jd_text:
                jd_context = f"Job Description:\n{self.jd_text}\n\n"
            elif target_role:
                jd_context = f"target Role: {target_role}\n\n"
                
            prompt = f"""
            Rewrite and improve this resume to make it highly optimized for the target job.
            
            {jd_context}
            Original Resume:
            {self.resume_text}

            Skills to highlight(in order of priority): {', '.join(skills_to_highlight)}

            {weakness_context}

            Here are specific examples of content to add:
            {improvement_examples}
            Please improve the resume by:
            1. Adding strong, quantifiable achievements
            2. Highlighting the specified skills strategically for ATS scanning
            3. Addressing all the weakness areas identified with the specific suggestions provided
            4. Incorporating the example improvements provided above
            5. Structuring information in a clear, professional format
            6. Using industry-standard terminology
            7. Ensuring all relevant experience is properly emphasized
            8. Adding measurable outcomes and achievements

            Return only the improved resume text, without any additional explanations.
            Format the resume in a modern ,clean style with clear section headings.
            """

            improved_resume = self.call_groq_llm(prompt).strip()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w',
                encoding='utf-8') as tmp:
                tmp.write(improved_resume)
                self.improved_resume_path = tmp.name
               
            return improved_resume
        
        except Exception as e:
            print(f"Error generating improved resume: {e}")
            return "Error generating improved resume. Please try again."
        
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if hasattr(self, 'resume_file_path') and os.path.exists(self.
            resume_file_path):
                os.unlink(self.resume_file_path)
            if hasattr(self, 'improved_resume_path') and os.path.exists(self.
            improved_resume_path):
                os.unlink(self.improved_resume_path)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")