import re
from typing import Dict, List, Optional, Set, Tuple

# Canonical Skill Map: maps various aliases/variations to standard canonical name
SKILL_ALIASES: Dict[str, str] = {
    # Languages
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "golang": "Go",
    "go": "Go",
    "c++": "C++",
    "cpp": "C++",
    "c#": "C#",
    "csharp": "C#",
    "java": "Java",
    "rust": "Rust",
    "ruby": "Ruby",
    "php": "PHP",
    "html": "HTML5",
    "html5": "HTML5",
    "css": "CSS3",
    "css3": "CSS3",
    "sql": "SQL",

    # Frontend
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "next": "Next.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "angular.js": "Angular",
    "svelte": "Svelte",
    "tailwind": "Tailwind CSS",
    "tailwindcss": "Tailwind CSS",
    "bootstrap": "Bootstrap",
    "redux": "Redux",
    "redux toolkit": "Redux Toolkit",

    # Backend
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express.js",
    "expressjs": "Express.js",
    "express.js": "Express.js",
    "fastapi": "FastAPI",
    "fast api": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    ".net": ".NET",
    "dotnet": ".NET",
    "asp.net": "ASP.NET",
    "nest": "NestJS",
    "nestjs": "NestJS",
    "graphql": "GraphQL",
    "rest": "REST APIs",
    "restful": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "grpc": "gRPC",

    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "psql": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",
    "elasticsearch": "Elasticsearch",

    # Cloud & DevOps
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "Google Cloud",
    "google cloud": "Google Cloud",
    "google cloud platform": "Google Cloud",
    "azure": "Microsoft Azure",
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "github actions": "GitHub Actions",
    "jenkins": "Jenkins",
    "terraform": "Terraform",
    "linux": "Linux",
    "git": "Git",

    # AI & ML & Data
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "opencv": "OpenCV",
    "rag": "RAG",
    "langchain": "LangChain",
    "llamaindex": "LlamaIndex",
    "huggingface": "Hugging Face",
    "hugging face": "Hugging Face",
}


def clean_skill_string(skill: str) -> str:
    """Clean punctuation, trailing spaces and casing for lookup."""
    if not skill:
        return ""
    # Strip bullet points and punctuation
    cleaned = skill.strip().lower()
    cleaned = re.sub(r"^[•\-*▪]\s*", "", cleaned)
    cleaned = re.sub(r"[,;]+$", "", cleaned).strip()
    return cleaned


def normalize_skill(skill: str) -> str:
    """
    Given any skill string, return the canonical name if recognized,
    or a nicely capitalized representation if not in the dictionary.
    """
    cleaned = clean_skill_string(skill)
    if not cleaned:
        return ""
    
    # Check alias dictionary
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    
    # Check without spaces or with hyphens
    condensed = re.sub(r"[\s\-_.]", "", cleaned)
    for alias_key, canonical in SKILL_ALIASES.items():
        if re.sub(r"[\s\-_.]", "", alias_key) == condensed:
            return canonical

    # If not recognized in alias map, return original with title casing
    return skill.strip()


def normalize_skill_list(skills: List[str]) -> List[str]:
    """Normalize a list of skills and remove duplicate entries preserving order."""
    normalized_list = []
    seen = set()
    for s in skills:
        norm = normalize_skill(s)
        if norm and norm.lower() not in seen:
            seen.add(norm.lower())
            normalized_list.append(norm)
    return normalized_list


def match_skills_deterministically(
    resume_skills: List[str], 
    jd_skills: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Perform exact and alias matching between resume skills and JD skills.
    Returns:
        (matched_skills, missing_skills)
    """
    norm_resume = {normalize_skill(s).lower(): normalize_skill(s) for s in resume_skills if s}
    matched = []
    missing = []

    for jd_skill in jd_skills:
        canonical_jd = normalize_skill(jd_skill)
        if canonical_jd.lower() in norm_resume:
            matched.append(canonical_jd)
        else:
            missing.append(canonical_jd)

    return sorted(list(set(matched))), sorted(list(set(missing)))
