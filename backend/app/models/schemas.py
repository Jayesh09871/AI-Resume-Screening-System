from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, HttpUrl


class ExperienceItem(BaseModel):
    title: str = Field(..., description="Job or role title")
    company: str = Field(..., description="Company or organization name")
    location: Optional[str] = Field(default="", description="Location")
    start_date: Optional[str] = Field(default="", description="Start date")
    end_date: Optional[str] = Field(default="", description="End date or Present")
    highlights: List[str] = Field(default_factory=list, description="Bullet points/achievements")


class EducationItem(BaseModel):
    degree: str = Field(..., description="Degree or program")
    institution: str = Field(..., description="College or university")
    location: Optional[str] = Field(default="", description="Location")
    graduation_year: Optional[str] = Field(default="", description="Graduation year or dates")
    gpa: Optional[str] = Field(default="", description="GPA or grade score if provided")


class ProjectItem(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(default="", description="Overview of the project")
    technologies: List[str] = Field(default_factory=list, description="Tech stack used")
    link: Optional[str] = Field(default="", description="Repository or live URL")
    highlights: List[str] = Field(default_factory=list, description="Key bullet points/contributions")


class ResumeSchema(BaseModel):
    name: str = Field(default="", description="Candidate's full name")
    email: str = Field(default="", description="Email address")
    phone: str = Field(default="", description="Phone number")
    location: Optional[str] = Field(default="", description="City, State / Country")
    summary: Optional[str] = Field(default="", description="Professional summary or objective")
    skills: List[str] = Field(default_factory=list, description="List of technical & soft skills")
    experience: List[ExperienceItem] = Field(default_factory=list, description="Work experience list")
    education: List[EducationItem] = Field(default_factory=list, description="Education list")
    projects: List[ProjectItem] = Field(default_factory=list, description="Project list")
    certifications: List[str] = Field(default_factory=list, description="Certifications list")
    achievements: List[str] = Field(default_factory=list, description="Honors and awards")
    links: List[str] = Field(default_factory=list, description="Portfolio, GitHub, LinkedIn URLs")


class BaseATSScoreBreakdown(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="Baseline ATS score of the resume without JD")
    section_score: int = Field(..., description="ATS Section completeness (out of 25)")
    contact_score: int = Field(..., description="Contact and profile details (out of 15)")
    linguistic_score: int = Field(..., description="Action verbs and voice (out of 25)")
    quantified_impact_score: int = Field(..., description="Metrics and numbers in bullets (out of 20)")
    skills_breadth_score: int = Field(..., description="Skill depth and indexing (out of 15)")
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)


class ResumeUploadResponse(BaseModel):
    resume_id: int
    raw_text: str
    page_count: int
    detected_sections: List[str]
    warnings: List[str]
    structured_data: ResumeSchema
    base_ats_score: Optional[BaseATSScoreBreakdown] = None


class JobDescriptionSchema(BaseModel):
    title: Optional[str] = Field(default="", description="Job title")
    company: Optional[str] = Field(default="", description="Company name")
    required_skills: List[str] = Field(default_factory=list, description="Mandatory skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Nice-to-have skills")
    technologies: List[str] = Field(default_factory=list, description="Tech tools and frameworks")
    responsibilities: List[str] = Field(default_factory=list, description="Key responsibilities")
    experience_requirements: List[str] = Field(default_factory=list, description="Experience requirements")
    education_requirements: List[str] = Field(default_factory=list, description="Education requirements")
    keywords: List[str] = Field(default_factory=list, description="Key domain keywords")
    domain_terms: List[str] = Field(default_factory=list, description="Industry domain terms")


class ATSScoreBreakdown(BaseModel):
    overall_score: int = Field(..., ge=0, le=100, description="Overall ATS compatibility score")
    required_skill_score: int = Field(..., ge=0, le=100)
    preferred_skill_score: int = Field(..., ge=0, le=100)
    experience_relevance: int = Field(..., ge=0, le=100)
    semantic_similarity: int = Field(..., ge=0, le=100)
    disclaimer: str = "This compatibility score is algorithmic and does not guarantee passing commercial ATS systems."


class SemanticMatchItem(BaseModel):
    jd_requirement: str
    resume_evidence: str
    similarity_score: float
    status: str = Field(..., description="strong, moderate, or weak")


class EvidenceBasedSuggestion(BaseModel):
    category: str = Field(..., description="keyword, summary, experience_bullet, project, skill_priority")
    recommendation: str
    reason: str
    resume_evidence: str
    related_jd_requirement: str


class MatchResultSchema(BaseModel):
    breakdown: ATSScoreBreakdown
    matched_required_skills: List[str]
    missing_required_skills: List[str]
    matched_preferred_skills: List[str]
    missing_preferred_skills: List[str]
    keywords_found: List[str]
    keywords_missing: List[str]
    semantic_matches: List[SemanticMatchItem]


class AnalyzeRequest(BaseModel):
    resume_id: Optional[int] = None
    resume_data: Optional[ResumeSchema] = None
    jd_text: str = Field(..., min_length=10, description="Job description text")


class LinguisticAnalysisSchema(BaseModel):
    linguistic_score: int = Field(..., ge=0, le=100)
    action_verbs_found: List[str] = Field(default_factory=list)
    passive_phrases_detected: List[str] = Field(default_factory=list)
    quantified_bullets_count: int = 0
    total_bullets_count: int = 0
    quantified_ratio: float = 0.0
    bullet_length_warnings: List[str] = Field(default_factory=list)
    overall_feedback: str = ""


class AnalysisResponse(BaseModel):
    analysis_id: Optional[int] = None
    resume_id: Optional[int] = None
    jd_id: Optional[int] = None
    match_data: MatchResultSchema
    suggestions: List[EvidenceBasedSuggestion]
    linguistic_analysis: Optional[LinguisticAnalysisSchema] = None
    created_at: str


class BulletImprovementRequest(BaseModel):
    bullet_text: str = Field(..., min_length=5)
    target_role: Optional[str] = ""
    context: Optional[str] = ""


class BulletImprovementResponse(BaseModel):
    original_bullet: str
    improved_bullet: str
    reasoning: str
    notes: str


class ResumeUpdateRequest(BaseModel):
    title: Optional[str] = None
    structured_data: ResumeSchema


class JDScrapeRequest(BaseModel):
    url: str = Field(..., description="Public job posting URL to scrape (e.g. Greenhouse, Lever, LinkedIn, etc.)")


class JDScrapeResponse(BaseModel):
    url: str
    title: Optional[str] = None
    company: Optional[str] = None
    jd_text: str
    word_count: int
    source: Optional[str] = None

