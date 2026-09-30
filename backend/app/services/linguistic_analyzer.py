import re
from typing import Dict, Any, List
from backend.app.models.schemas import ResumeSchema

STRONG_ACTION_VERBS = {
    # Engineering & Building
    "architected", "engineered", "developed", "built", "implemented", "constructed", "designed",
    "deployed", "configured", "automated", "refactored", "integrated", "programmed", "orchestrated",
    # Optimization & Growth
    "accelerated", "optimized", "reduced", "scaled", "boosted", "maximized", "streamlined",
    "improved", "enhanced", "doubled", "generated", "decreased", "eliminated", "upgraded",
    # Leadership & Management
    "spearheaded", "led", "mentored", "directed", "established", "founded", "guided",
    "managed", "supervised", "championed", "delivered", "executed", "collaborated"
}

WEAK_PASSIVE_PHRASES = [
    "responsible for", "responsibilities included", "worked on", "assisted with",
    "helped in", "helped to", "duties included", "handled", "participated in",
    "was tasked with", "involved in"
]


class LinguisticAnalyzer:
    """
    Evaluates resume language against industry recruiter benchmarks:
    1. Strong Action Verbs vs Passive Phrases
    2. Quantified Impact (presence of numbers, percentages, metrics)
    3. Bullet Point Length & Readability
    4. Computes an ATS Linguistic Quality Score (0-100)
    """

    @classmethod
    def analyze(cls, resume: ResumeSchema) -> Dict[str, Any]:
        bullets = []
        for exp in resume.experience:
            for h in exp.highlights:
                if h.strip():
                    bullets.append(h.strip())
        for proj in resume.projects:
            for h in proj.highlights:
                if h.strip():
                    bullets.append(h.strip())

        total_bullets = len(bullets)
        if total_bullets == 0:
            return {
                "linguistic_score": 50,
                "action_verbs_found": [],
                "passive_phrases_detected": [],
                "quantified_bullets_count": 0,
                "quantified_ratio": 0.0,
                "bullet_length_warnings": ["No experience or project bullets detected to analyze."],
                "overall_feedback": "Add bullet points to your experience and projects to evaluate readability."
            }

        # 1. Action verbs detection
        action_verbs_found = set()
        quantified_count = 0
        passive_phrases_detected = []
        length_warnings = []

        # Metric pattern: numbers, percentages, currency, multipliers (e.g. 35%, $2M, 5x, 2,000+)
        metric_pattern = re.compile(r"(\b\d+[%xXkKMmB]?\b|\$\d+|\b\d{1,3}(?:,\d{3})+\+?)")

        for idx, bullet in enumerate(bullets):
            bullet_lower = bullet.lower()
            words = re.findall(r"\b[a-zA-Z]+\b", bullet_lower)

            # Check starting word for action verb
            if words and words[0] in STRONG_ACTION_VERBS:
                action_verbs_found.add(words[0].capitalize())
            else:
                # Check anywhere in bullet
                for w in words:
                    if w in STRONG_ACTION_VERBS:
                        action_verbs_found.add(w.capitalize())

            # Check passive phrases
            for phrase in WEAK_PASSIVE_PHRASES:
                if phrase in bullet_lower:
                    passive_phrases_detected.append(f'"{phrase}" in: "{bullet[:60]}..."')

            # Check quantified metric
            if metric_pattern.search(bullet):
                quantified_count += 1

            # Check bullet length
            word_count = len(words)
            if word_count < 6:
                length_warnings.append(f'Too brief ({word_count} words): "{bullet}"')
            elif word_count > 38:
                length_warnings.append(f'Too lengthy ({word_count} words) - consider splitting: "{bullet[:60]}..."')

        quantified_ratio = round((quantified_count / total_bullets) * 100, 1)
        action_verb_ratio = min(1.0, len(action_verbs_found) / max(3, total_bullets * 0.6))
        
        # Calculate Linguistic Score (0 - 100)
        # 40% action verbs, 40% quantified impact, 20% passive penalty
        passive_penalty = min(30, len(passive_phrases_detected) * 10)
        base_score = int((action_verb_ratio * 40) + ((quantified_ratio / 100) * 40) + 20)
        final_score = max(20, min(100, base_score - passive_penalty))

        # Overall summary feedback
        if final_score >= 80:
            feedback = "Excellent high-impact phrasing with strong action verbs and measurable metrics."
        elif final_score >= 60:
            feedback = "Good foundation, but replace passive phrases with strong action verbs and add more measurable outcomes."
        else:
            feedback = "Needs improvement: replace passive language (e.g. 'worked on') with strong verbs and add quantifiable metrics."

        return {
            "linguistic_score": final_score,
            "action_verbs_found": sorted(list(action_verbs_found)),
            "passive_phrases_detected": passive_phrases_detected[:5],
            "quantified_bullets_count": quantified_count,
            "total_bullets_count": total_bullets,
            "quantified_ratio": quantified_ratio,
            "bullet_length_warnings": length_warnings[:4],
            "overall_feedback": feedback,
        }
