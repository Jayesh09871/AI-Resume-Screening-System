import re
import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.models.schemas import ResumeSchema, JobDescriptionSchema, SemanticMatchItem
from backend.app.utils.logger import logger
from backend.app.utils.text_cleaner import split_into_sentences

# Global singleton cache for embedding model to avoid reloading on every request
_EMBEDDING_MODEL = None


def get_embedding_model():
    global _EMBEDDING_MODEL
    # Skip loading heavy PyTorch model in 512MB containers (Render Free Tier)
    import os
    if os.getenv("RENDER") or os.getenv("LOW_MEMORY_MODE", "false").lower() in ("true", "1"):
        return None
    if _EMBEDDING_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            _EMBEDDING_MODEL = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
            _EMBEDDING_MODEL = None
    return _EMBEDDING_MODEL


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute cosine similarity between two 1D vectors."""
    dot = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(dot / (norm1 * norm2))


class SemanticMatcher:
    """
    Computes semantic similarity between Job Description requirements and
    Resume statements using sentence-transformers (all-MiniLM-L6-v2) and cosine similarity.
    """

    def __init__(self):
        self.model = get_embedding_model()
        self.threshold = settings.SEMANTIC_SIMILARITY_THRESHOLD

    def extract_resume_evidence_sentences(self, resume: ResumeSchema) -> List[str]:
        """Collect all distinct, meaningful sentences and highlights from the resume."""
        evidence_sentences = []

        if resume.summary:
            evidence_sentences.extend(split_into_sentences(resume.summary))

        for exp in resume.experience:
            evidence_sentences.append(f"{exp.title} at {exp.company}")
            for h in exp.highlights:
                if len(h.strip()) > 8:
                    evidence_sentences.append(h.strip())

        for proj in resume.projects:
            evidence_sentences.append(f"Project {proj.name}: {proj.description}")
            if proj.technologies:
                evidence_sentences.append(f"Built {proj.name} utilizing {', '.join(proj.technologies)}")
            for h in proj.highlights:
                if len(h.strip()) > 8:
                    evidence_sentences.append(h.strip())

        if resume.skills:
            evidence_sentences.append(f"Proficient in skills: {', '.join(resume.skills)}")

        return [s for s in evidence_sentences if len(s.strip()) > 5]

    def match(self, resume: ResumeSchema, jd: JobDescriptionSchema) -> Dict[str, Any]:
        """
        Compare each JD requirement and responsibility against the resume sentences.
        Returns matched evidence items with scores and an overall semantic score.
        """
        resume_sentences = self.extract_resume_evidence_sentences(resume)
        if not resume_sentences:
            return {
                "semantic_matches": [],
                "semantic_score": 0,
            }

        # Targets to match from the JD
        targets = []
        if jd.required_skills:
            targets.extend([f"Requires proficiency in {s}" for s in jd.required_skills[:6]])
        if jd.responsibilities:
            targets.extend(jd.responsibilities[:5])
        if jd.experience_requirements:
            targets.extend(jd.experience_requirements[:3])

        if not targets:
            targets = ["Software engineering and system implementation"]

        semantic_matches: List[SemanticMatchItem] = []

        # If sentence-transformers model is available, use embeddings
        if self.model is not None:
            try:
                resume_embeddings = self.model.encode(resume_sentences, convert_to_numpy=True)
                target_embeddings = self.model.encode(targets, convert_to_numpy=True)

                scores_for_overall = []

                for i, target in enumerate(targets):
                    t_emb = target_embeddings[i]
                    # Compute similarity against all resume sentences
                    sims = [cosine_similarity(t_emb, r_emb) for r_emb in resume_embeddings]
                    best_idx = int(np.argmax(sims))
                    best_score = float(sims[best_idx])
                    best_evidence = resume_sentences[best_idx]

                    # Status classification
                    if best_score >= 0.70:
                        status = "strong"
                    elif best_score >= 0.50:
                        status = "moderate"
                    else:
                        status = "weak"

                    clean_target = re.sub(r"^Requires proficiency in ", "", target)
                    semantic_matches.append(
                        SemanticMatchItem(
                            jd_requirement=clean_target,
                            resume_evidence=best_evidence,
                            similarity_score=round(best_score, 3),
                            status=status,
                        )
                    )
                    scores_for_overall.append(best_score)

                # Overall semantic score (0-100)
                avg_sim = float(np.mean(scores_for_overall)) if scores_for_overall else 0.5
                semantic_score = int(min(100, max(0, avg_sim * 100)))

                return {
                    "semantic_matches": semantic_matches,
                    "semantic_score": semantic_score,
                }
            except Exception as e:
                logger.error(f"Error during semantic embedding matching: {e}")

        # Lightweight TF-IDF & Cosine Similarity Matcher
        # Consumes < 5MB of RAM and computes in milliseconds (ideal for Render 512MB limit)
        fallback_matches = []
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity as sk_cosine_similarity

            vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
            corpus = targets + resume_sentences
            tfidf_matrix = vectorizer.fit_transform(corpus)

            target_vectors = tfidf_matrix[:len(targets)]
            resume_vectors = tfidf_matrix[len(targets):]
            sim_matrix = sk_cosine_similarity(target_vectors, resume_vectors)

            scores_for_overall = []
            for i, target in enumerate(targets):
                sims = sim_matrix[i]
                best_idx = int(np.argmax(sims))
                raw_score = float(sims[best_idx])
                calibrated_score = min(0.95, round(0.40 + (raw_score * 0.9), 3)) if raw_score > 0 else 0.35
                best_evidence = resume_sentences[best_idx]

                if calibrated_score >= 0.70:
                    status = "strong"
                elif calibrated_score >= 0.50:
                    status = "moderate"
                else:
                    status = "weak"

                clean_target = re.sub(r"^Requires proficiency in ", "", target)
                fallback_matches.append(
                    SemanticMatchItem(
                        jd_requirement=clean_target,
                        resume_evidence=best_evidence,
                        similarity_score=calibrated_score,
                        status=status,
                    )
                )
                scores_for_overall.append(calibrated_score)

            avg_sim = float(np.mean(scores_for_overall)) if scores_for_overall else 0.65
            semantic_score = int(min(100, max(0, avg_sim * 100)))

            return {
                "semantic_matches": fallback_matches,
                "semantic_score": semantic_score,
            }
        except Exception as e:
            logger.warning(f"TF-IDF semantic matching error, using word overlap fallback: {e}")

        # Fallback word-overlap heuristic if scikit-learn is unavailable
        for target in targets:
            target_words = set(re.findall(r"\w+", target.lower()))
            best_evidence = resume_sentences[0]
            best_ratio = 0.0

            for sent in resume_sentences:
                sent_words = set(re.findall(r"\w+", sent.lower()))
                common = target_words.intersection(sent_words)
                ratio = len(common) / max(1, len(target_words))
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_evidence = sent

            sim_score = min(0.95, round(best_ratio * 0.85 + 0.3, 2))
            status = "strong" if sim_score >= 0.7 else ("moderate" if sim_score >= 0.5 else "weak")
            clean_target = re.sub(r"^Requires proficiency in ", "", target)
            fallback_matches.append(
                SemanticMatchItem(
                    jd_requirement=clean_target,
                    resume_evidence=best_evidence,
                    similarity_score=sim_score,
                    status=status
                )
            )

        return {
            "semantic_matches": fallback_matches,
            "semantic_score": 75,
        }
