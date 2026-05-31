"""Career recommendation engine (Week 6 · Day 3)."""

from __future__ import annotations

from app.agents.career.paths import CAREER_PATHS
from app.agents.career.profile_builder import ProfileBuilder
from app.models.career import CareerAnalysisRequest, CareerMatch, CareerRecommendationResponse, StudentCareerProfile
from app.rag.llm import call_llm, llm_enabled


class CareerRecommendationEngine:
    @staticmethod
    def recommend(
        profile: StudentCareerProfile,
        message: str | None = None,
    ) -> CareerRecommendationResponse:
        matches: list[CareerMatch] = []
        for career_id, meta in CAREER_PATHS.items():
            score, rationale, strengths, gaps = CareerRecommendationEngine._score_career(
                profile, career_id, meta
            )
            matches.append(
                CareerMatch(
                    career_id=career_id,
                    title=meta["title"],
                    match_score=round(score, 1),
                    rationale=rationale,
                    strengths=strengths,
                    gaps=gaps,
                )
            )

        matches.sort(key=lambda m: m.match_score, reverse=True)
        top = matches[0]
        alts = matches[1:4]

        profile_summary = CareerRecommendationEngine._profile_summary(profile)
        analyzed = {
            "performance_score": profile.performance_score,
            "interview_overall": profile.interview_overall,
            "interests": profile.interests,
            "top_skills": sorted(profile.skills.items(), key=lambda x: -x[1])[:5],
        }

        return CareerRecommendationResponse(
            top_career=top,
            alternatives=alts,
            profile_summary=profile_summary,
            analyzed=analyzed,
            used_llm=False,
        )

    @staticmethod
    def _score_career(
        profile: StudentCareerProfile,
        career_id: str,
        meta: dict,
    ) -> tuple[float, str, list[str], list[str]]:
        # Subject component (0-40)
        sub_score = 0.0
        sub_weight_sum = 0.0
        for subject, weight in meta["subject_weights"].items():
            sc = profile.subject_scores.get(subject, 65)
            sub_score += sc * weight
            sub_weight_sum += weight
        subject_component = (sub_score / sub_weight_sum * 0.4) if sub_weight_sum else 26

        # Skills component (0-35)
        req = meta["required_skills"]
        skill_hits = []
        skill_gaps = []
        skill_total = 0.0
        for skill, required in req.items():
            current = profile.skills.get(skill, profile.skills.get(skill.replace("_", " "), 50))
            ratio = min(1.0, current / required) if required else 1.0
            skill_total += ratio * required
            if ratio >= 0.85:
                skill_hits.append(skill.replace("_", " ").title())
            elif ratio < 0.7:
                skill_gaps.append(skill.replace("_", " ").title())
        skill_component = (skill_total / sum(req.values())) * 35 if req else 17.5

        # Interview component (0-15)
        interview_component = 7.5
        iw = meta["interview_weights"]
        if profile.interview_technical is not None:
            interview_component = 0.0
            if "technical" in iw:
                interview_component += (profile.interview_technical / 10) * iw["technical"] * 100
            if "communication" in iw and profile.interview_communication is not None:
                interview_component += (profile.interview_communication / 10) * iw["communication"] * 100
            if "confidence" in iw and profile.interview_confidence is not None:
                interview_component += (profile.interview_confidence / 10) * iw["confidence"] * 100
            interview_component = min(15, interview_component)

        # Interest boost (0-10)
        interest_component = 0.0
        matched_interests = []
        for kw in meta["interest_keywords"]:
            for interest in profile.interests:
                if kw in interest or interest in kw:
                    interest_component = max(interest_component, 8)
                    matched_interests.append(kw)
        if not profile.interests:
            interest_component = 3  # neutral

        total = subject_component + skill_component + interview_component + interest_component
        total = min(100, max(0, total))

        strengths = skill_hits[:3]
        if profile.interview_technical and profile.interview_technical >= 7:
            strengths.append("Strong technical interview performance")
        gaps = skill_gaps[:3]

        rationale = (
            f"Match based on academic performance ({subject_component:.0f}/40 skills fit), "
            f"skill alignment ({skill_component:.0f}/35), "
        )
        if profile.interview_overall:
            rationale += f"interview scores ({interview_component:.0f}/15), "
        if matched_interests:
            rationale += f"and interest in {', '.join(matched_interests[:2])}."
        else:
            rationale += "and overall profile fit."

        return total, rationale, strengths, gaps

    @staticmethod
    def _profile_summary(profile: StudentCareerProfile) -> str:
        parts = [f"Performance avg: **{profile.performance_score:.0f}%**"]
        if profile.interview_overall is not None:
            parts.append(f"Interview avg: **{profile.interview_overall:.1f}/10**")
        if profile.interests:
            parts.append(f"Interests: {', '.join(profile.interests)}")
        top_subj = sorted(profile.subject_scores.items(), key=lambda x: -x[1])[:2]
        if top_subj:
            parts.append(
                "Strongest subjects: " + ", ".join(f"{s} ({v:.0f}%)" for s, v in top_subj)
            )
        return " · ".join(parts)

    @staticmethod
    async def from_request(req: CareerAnalysisRequest, message: str | None = None) -> CareerRecommendationResponse:
        profile = ProfileBuilder.build(
            message=message,
            interests=req.interests,
            subject_scores=req.subject_scores,
            interview_session_id=req.interview_session_id,
        )
        result = CareerRecommendationEngine.recommend(profile, message)
        if llm_enabled() and message:
            enhanced = await CareerRecommendationEngine._llm_narrative(result, profile, message)
            if enhanced:
                result.top_career.rationale = enhanced
                result.used_llm = True
        return result

    @staticmethod
    async def _llm_narrative(
        result: CareerRecommendationResponse,
        profile: StudentCareerProfile,
        message: str,
    ) -> str | None:
        prompt = (
            f"Student profile: performance {profile.performance_score}, "
            f"skills top 3: {sorted(profile.skills.items(), key=lambda x: -x[1])[:3]}, "
            f"interests: {profile.interests}. "
            f"Top career match: {result.top_career.title} ({result.top_career.match_score}%). "
            f"Write 2 sentences explaining why this is their strongest path. Be encouraging."
        )
        return await call_llm(
            [
                {"role": "system", "content": "You are a career counselor for tech students."},
                {"role": "user", "content": prompt + f"\n\nStudent asked: {message}"},
            ],
            max_tokens=150,
        )

    @staticmethod
    def to_markdown(result: CareerRecommendationResponse) -> str:
        top = result.top_career
        lines = [
            f"Based on your strengths, **{top.title}** is your strongest career path "
            f"(**{top.match_score:.0f}% match**).\n",
            result.profile_summary,
            "",
            f"**Why {top.title}?** {top.rationale}",
        ]
        if top.strengths:
            lines.append("\n**Your strengths**")
            for s in top.strengths:
                lines.append(f"• {s}")
        if top.gaps:
            lines.append("\n**Areas to develop**")
            for g in top.gaps:
                lines.append(f"• {g}")
        lines.append("\n**Other paths to consider**")
        for alt in result.alternatives:
            lines.append(f"• **{alt.title}** — {alt.match_score:.0f}% match")
        return "\n".join(lines)
