from typing import Dict, Any, List
from backend.app.models.schemas import ResumeSchema, BaseATSScoreBreakdown
from backend.app.services.linguistic_analyzer import LinguisticAnalyzer


class ResumeQualityScorer:
    """
    Evaluates a candidate's resume for general ATS parseability, structure,
    linguistic quality, and recruiter impact WITHOUT requiring a Job Description.
    
    Weights:
    1. Section Completeness (25%)
    2. Contact & Professional Info (15%)
    3. Action Verbs & Linguistic Strength (25%)
    4. Quantified Business Impact (20%)
    5. Skills Breadth & Richness (15%)
    """

    @classmethod
    def evaluate(cls, resume: ResumeSchema) -> BaseATSScoreBreakdown:
        strengths: List[str] = []
        improvements: List[str] = []

        # 1. Section Completeness (Max 25 pts)
        section_score = 0
        if resume.name and (resume.email or resume.phone):
            section_score += 5
        if resume.summary and len(resume.summary.strip()) > 30:
            section_score += 5
            strengths.append("Professional summary provides quick context for ATS parsers.")
        else:
            improvements.append("Add a 2-3 sentence Professional Summary at the top of your resume.")

        if resume.experience and len(resume.experience) > 0:
            section_score += 5
            strengths.append(f"Work experience section detected with {len(resume.experience)} role(s).")
        else:
            improvements.append("Include detailed Work Experience or internships.")

        if resume.education and len(resume.education) > 0:
            section_score += 5
            strengths.append("Education history properly structured.")
        else:
            improvements.append("Add your Education details (degree, institution, graduation year).")

        if resume.skills and len(resume.skills) >= 4:
            section_score += 5
        else:
            improvements.append("List at least 6-8 core technical and soft skills in a dedicated Skills section.")

        # 2. Contact & Professional Presence (Max 15 pts)
        contact_score = 0
        if resume.name and len(resume.name.strip()) > 2:
            contact_score += 3
        if resume.email and "@" in resume.email:
            contact_score += 4
        else:
            improvements.append("Add a professional email address to ensure recruiters can reach you.")

        if resume.phone and len(resume.phone.strip()) >= 7:
            contact_score += 4
        else:
            improvements.append("Add a contact phone number.")

        has_links = bool(resume.links and len(resume.links) > 0) or any(
            domain in (resume.summary or "").lower() for domain in ["linkedin.com", "github.com"]
        )
        if has_links or resume.location:
            contact_score += 4
            strengths.append("Contact details and location/profiles verified.")
        else:
            improvements.append("Include links to your LinkedIn profile, GitHub, or portfolio website.")

        # 3 & 4. Linguistic Strength & Quantified Metrics (LinguisticAnalyzer)
        linguistic_res = LinguisticAnalyzer.analyze(resume)
        ling_raw = linguistic_res.get("linguistic_score", 50)
        # Scale to 25 pts
        linguistic_score = int(round((ling_raw / 100) * 25))

        verbs_count = len(linguistic_res.get("action_verbs_found", []))
        if verbs_count >= 5:
            strengths.append(f"Strong active voice with {verbs_count} impactful action verbs.")
        else:
            improvements.append("Begin bullet points with strong action verbs (e.g., 'Engineered', 'Optimized', 'Scaled').")

        # Quantified impact (Max 20 pts)
        quant_ratio = linguistic_res.get("quantified_ratio", 0.0)
        # Target: 30%+ of bullets having numbers/metrics gives full 20 pts
        quant_factor = min(1.0, quant_ratio / 30.0) if quant_ratio > 0 else 0.2
        quantified_impact_score = int(round(quant_factor * 20))

        if quant_ratio >= 25.0:
            strengths.append(f"{quant_ratio}% of your bullet points contain measurable metrics/numbers.")
        else:
            improvements.append("Add measurable outcomes to your bullet points (e.g., %, $, speedup, user counts).")

        # 5. Skills Breadth & Richness (Max 15 pts)
        skills_count = len(resume.skills)
        if skills_count >= 12:
            skills_breadth_score = 15
            strengths.append(f"Extensive skill profile ({skills_count} skills indexed).")
        elif skills_count >= 7:
            skills_breadth_score = 12
        elif skills_count >= 4:
            skills_breadth_score = 8
            improvements.append("Expand your skills list with relevant frameworks, tools, and databases.")
        else:
            skills_breadth_score = 4
            improvements.append("Add more specific technical and industry skills to increase ATS search matches.")

        overall_score = section_score + contact_score + linguistic_score + quantified_impact_score + skills_breadth_score
        overall_score = min(100, max(15, overall_score))

        return BaseATSScoreBreakdown(
            overall_score=overall_score,
            section_score=section_score,
            contact_score=contact_score,
            linguistic_score=linguistic_score,
            quantified_impact_score=quantified_impact_score,
            skills_breadth_score=skills_breadth_score,
            strengths=strengths[:4],
            improvements=improvements[:4],
        )
