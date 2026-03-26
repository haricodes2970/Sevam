"""
Dosha Calculator for Sevam.

Pure-Python module (no async, no DB). Implements a 20-question Ayurvedic
prakriti questionnaire and scores responses to determine the user's
dominant dosha (Vata, Pitta, or Kapha).

Usage:
    calc = DoshaCalculator()
    questions = calc.get_questions()
    result = calc.calculate_prakriti({"1": "a", "2": "b", ...})
"""

from __future__ import annotations


class DoshaCalculator:
    """Calculates Ayurvedic prakriti from a 20-question questionnaire."""

    QUESTIONS: list[dict] = [
        # ── 1. Body frame ───────────────────────────────────────────────────
        {
            "id": 1,
            "category": "Body Frame & Weight",
            "question": "How is your body frame?",
            "options": {
                "a": {"text": "Thin, light, hard to gain weight", "dosha": "vata"},
                "b": {"text": "Medium, muscular, athletic build", "dosha": "pitta"},
                "c": {"text": "Large, heavy, gains weight easily", "dosha": "kapha"},
            },
        },
        # ── 2. Weight tendency ──────────────────────────────────────────────
        {
            "id": 2,
            "category": "Body Frame & Weight",
            "question": "How does your weight tend to change?",
            "options": {
                "a": {"text": "Difficulty gaining weight, lose it easily", "dosha": "vata"},
                "b": {"text": "Moderate; gain and lose weight fairly easily", "dosha": "pitta"},
                "c": {"text": "Gain weight easily, very hard to lose", "dosha": "kapha"},
            },
        },
        # ── 3. Skin type ────────────────────────────────────────────────────
        {
            "id": 3,
            "category": "Skin Type",
            "question": "How would you describe your skin?",
            "options": {
                "a": {"text": "Dry, rough, thin, cool to touch", "dosha": "vata"},
                "b": {"text": "Oily, warm, reddish, prone to rashes or inflammation", "dosha": "pitta"},
                "c": {"text": "Thick, moist, smooth, soft, cool", "dosha": "kapha"},
            },
        },
        # ── 4. Hair type ────────────────────────────────────────────────────
        {
            "id": 4,
            "category": "Hair Type",
            "question": "How is your hair naturally?",
            "options": {
                "a": {"text": "Dry, frizzy, brittle, thin", "dosha": "vata"},
                "b": {"text": "Fine, straight, oily, premature greying or thinning", "dosha": "pitta"},
                "c": {"text": "Thick, wavy, oily, lustrous", "dosha": "kapha"},
            },
        },
        # ── 5. Appetite ─────────────────────────────────────────────────────
        {
            "id": 5,
            "category": "Appetite & Digestion",
            "question": "How is your appetite?",
            "options": {
                "a": {"text": "Irregular — sometimes hungry, sometimes not", "dosha": "vata"},
                "b": {"text": "Strong — get irritable or headachy when I miss a meal", "dosha": "pitta"},
                "c": {"text": "Steady but not urgent — I can skip meals easily", "dosha": "kapha"},
            },
        },
        # ── 6. Digestion ────────────────────────────────────────────────────
        {
            "id": 6,
            "category": "Appetite & Digestion",
            "question": "How is your digestion?",
            "options": {
                "a": {"text": "Irregular — bloating, gas, constipation tendency", "dosha": "vata"},
                "b": {"text": "Sharp — heartburn, acid reflux, loose stools when stressed", "dosha": "pitta"},
                "c": {"text": "Slow but steady — heavy feeling after meals", "dosha": "kapha"},
            },
        },
        # ── 7. Sleep patterns ───────────────────────────────────────────────
        {
            "id": 7,
            "category": "Sleep Patterns",
            "question": "How do you sleep?",
            "options": {
                "a": {"text": "Light sleeper, wake easily, tend towards insomnia", "dosha": "vata"},
                "b": {"text": "Moderate — 6–8 hours, wake if too hot", "dosha": "pitta"},
                "c": {"text": "Deep, long sleeper — hard to wake up, feel groggy", "dosha": "kapha"},
            },
        },
        # ── 8. Energy levels ────────────────────────────────────────────────
        {
            "id": 8,
            "category": "Energy Levels",
            "question": "How are your energy levels through the day?",
            "options": {
                "a": {"text": "Burst of energy then sudden fatigue, inconsistent", "dosha": "vata"},
                "b": {"text": "Strong, intense energy — I push until I burn out", "dosha": "pitta"},
                "c": {"text": "Steady, sustained energy — slow to start but lasting", "dosha": "kapha"},
            },
        },
        # ── 9. Memory & learning ────────────────────────────────────────────
        {
            "id": 9,
            "category": "Memory & Learning",
            "question": "How do you learn and remember things?",
            "options": {
                "a": {"text": "Quick to learn but also quick to forget", "dosha": "vata"},
                "b": {"text": "Sharp memory, learn quickly, retain well", "dosha": "pitta"},
                "c": {"text": "Slow to learn but once learnt, never forget", "dosha": "kapha"},
            },
        },
        # ── 10. Emotional tendencies ────────────────────────────────────────
        {
            "id": 10,
            "category": "Emotional Tendencies",
            "question": "What emotions do you experience most under stress?",
            "options": {
                "a": {"text": "Anxiety, fear, insecurity, restlessness", "dosha": "vata"},
                "b": {"text": "Anger, irritability, frustration, criticism", "dosha": "pitta"},
                "c": {"text": "Attachment, depression, withdrawal, sadness", "dosha": "kapha"},
            },
        },
        # ── 11. Emotional balance ───────────────────────────────────────────
        {
            "id": 11,
            "category": "Emotional Tendencies",
            "question": "How do you handle change?",
            "options": {
                "a": {"text": "Excited by change but easily overwhelmed", "dosha": "vata"},
                "b": {"text": "Like purposeful change, dislike disorder or inefficiency", "dosha": "pitta"},
                "c": {"text": "Prefer routine, resist change, take time to adapt", "dosha": "kapha"},
            },
        },
        # ── 12. Speech pattern ──────────────────────────────────────────────
        {
            "id": 12,
            "category": "Speech Pattern",
            "question": "How would others describe your speech?",
            "options": {
                "a": {"text": "Fast, talkative, jump between topics", "dosha": "vata"},
                "b": {"text": "Sharp, precise, convincing, sometimes argumentative", "dosha": "pitta"},
                "c": {"text": "Slow, deliberate, melodious, thoughtful", "dosha": "kapha"},
            },
        },
        # ── 13. Weather preference ──────────────────────────────────────────
        {
            "id": 13,
            "category": "Weather Preference",
            "question": "Which climate do you dislike most?",
            "options": {
                "a": {"text": "Cold, dry, windy weather", "dosha": "vata"},
                "b": {"text": "Hot, humid, direct sun", "dosha": "pitta"},
                "c": {"text": "Cold, damp, cloudy weather", "dosha": "kapha"},
            },
        },
        # ── 14. Bowel movements ─────────────────────────────────────────────
        {
            "id": 14,
            "category": "Bowel Movements",
            "question": "How are your bowel movements typically?",
            "options": {
                "a": {"text": "Irregular, tendency towards constipation and dry stools", "dosha": "vata"},
                "b": {"text": "Regular, loose, soft — sometimes diarrhoea", "dosha": "pitta"},
                "c": {"text": "Slow, regular, well-formed, heavy", "dosha": "kapha"},
            },
        },
        # ── 15. Sweat pattern ───────────────────────────────────────────────
        {
            "id": 15,
            "category": "Sweat Pattern",
            "question": "How much do you sweat?",
            "options": {
                "a": {"text": "Minimal sweating, skin stays dry", "dosha": "vata"},
                "b": {"text": "Profuse sweating, body odour noticeable", "dosha": "pitta"},
                "c": {"text": "Moderate sweating, skin feels moist and cool", "dosha": "kapha"},
            },
        },
        # ── 16. Eye characteristics ─────────────────────────────────────────
        {
            "id": 16,
            "category": "Eye Characteristics",
            "question": "How would you describe your eyes?",
            "options": {
                "a": {"text": "Small, dry, active, nervous — blink often", "dosha": "vata"},
                "b": {"text": "Medium, sharp, penetrating, light-sensitive", "dosha": "pitta"},
                "c": {"text": "Large, calm, moist, attractive, long lashes", "dosha": "kapha"},
            },
        },
        # ── 17. Nail characteristics ────────────────────────────────────────
        {
            "id": 17,
            "category": "Nail Characteristics",
            "question": "How are your nails?",
            "options": {
                "a": {"text": "Dry, brittle, break easily, rough surface", "dosha": "vata"},
                "b": {"text": "Medium, pinkish, soft, flexible", "dosha": "pitta"},
                "c": {"text": "Thick, smooth, strong, pale white", "dosha": "kapha"},
            },
        },
        # ── 18. Stress response ─────────────────────────────────────────────
        {
            "id": 18,
            "category": "Stress Response",
            "question": "How do you typically respond to stress?",
            "options": {
                "a": {"text": "Worry, overthink, become scattered and anxious", "dosha": "vata"},
                "b": {"text": "Become focused but aggressive, driven by deadlines", "dosha": "pitta"},
                "c": {"text": "Withdraw, sleep more, seek comfort in food or company", "dosha": "kapha"},
            },
        },
        # ── 19. Activity level ──────────────────────────────────────────────
        {
            "id": 19,
            "category": "Activity Level",
            "question": "How active are you naturally?",
            "options": {
                "a": {"text": "Very active, restless, always moving or fidgeting", "dosha": "vata"},
                "b": {"text": "Moderately active, purposeful and goal-directed", "dosha": "pitta"},
                "c": {"text": "Prefer stillness, relaxed pace, dislike rushing", "dosha": "kapha"},
            },
        },
        # ── 20. Mind characteristics ────────────────────────────────────────
        {
            "id": 20,
            "category": "Mind Characteristics",
            "question": "How would you describe your mental nature?",
            "options": {
                "a": {"text": "Creative, imaginative, quick but scattered", "dosha": "vata"},
                "b": {"text": "Analytical, intelligent, critical, likes order", "dosha": "pitta"},
                "c": {"text": "Calm, steady, compassionate, sometimes overly attached", "dosha": "kapha"},
            },
        },
    ]

    # ── Descriptions & recommendations per prakriti ──────────────────────────

    _DESCRIPTIONS: dict[str, str] = {
        "Vata": (
            "You are predominantly Vata. Vata is governed by the elements of air and space. "
            "You tend to be creative, enthusiastic, and quick-thinking, but can become anxious, "
            "scattered, or exhausted when out of balance. Warmth, routine, and grounding practices "
            "are key to your wellbeing."
        ),
        "Pitta": (
            "You are predominantly Pitta. Pitta is governed by the elements of fire and water. "
            "You tend to be sharp, ambitious, and focused, but can become irritable, inflammatory, "
            "or overly competitive when aggravated. Cooling foods, moderation, and relaxation "
            "practices help keep you balanced."
        ),
        "Kapha": (
            "You are predominantly Kapha. Kapha is governed by the elements of earth and water. "
            "You tend to be calm, nurturing, and strong, but can become lethargic, possessive, "
            "or resistant to change when out of balance. Stimulation, lighter foods, and regular "
            "vigorous exercise are beneficial for you."
        ),
        "Vata-Pitta": (
            "You are predominantly Vata with secondary Pitta. You combine quick creativity with "
            "focused drive. Balance both by avoiding extremes of cold/dry and heat/spice."
        ),
        "Vata-Kapha": (
            "You are predominantly Vata with secondary Kapha. You alternate between restlessness "
            "and inertia. Warmth, light meals, and a steady routine support your balance."
        ),
        "Pitta-Vata": (
            "You are predominantly Pitta with secondary Vata. Your fiery focus combines with "
            "creative energy. Avoid excess heat, spice, and mental overload."
        ),
        "Pitta-Kapha": (
            "You are predominantly Pitta with secondary Kapha. You have strong digestion and "
            "endurance. Avoid heavy oily foods and excess heat."
        ),
        "Kapha-Vata": (
            "You are predominantly Kapha with secondary Vata. Ground yourself with warm, "
            "light, spiced foods and avoid cold, damp environments."
        ),
        "Kapha-Pitta": (
            "You are predominantly Kapha with secondary Pitta. You have strength and intensity. "
            "Light, warm, and mildly spiced foods support your balance."
        ),
    }

    _RECOMMENDATIONS: dict[str, dict[str, str]] = {
        "Vata": {
            "diet": (
                "Favour warm, cooked, oily, and grounding foods: soups, stews, ghee, dairy, "
                "sweet root vegetables, whole grains. Eat at regular times. Avoid raw, cold, "
                "dry, or very light foods."
            ),
            "lifestyle": (
                "Maintain a consistent daily routine. Warm oil massage (abhyanga) daily. "
                "Gentle yoga, pranayama, and meditation. Avoid excessive travel, screen time, "
                "and staying up late."
            ),
            "avoid": (
                "Cold drinks, raw salads, dried fruits, excessive fasting, caffeine, "
                "irregular schedules, and cold windy weather."
            ),
        },
        "Pitta": {
            "diet": (
                "Favour cooling, sweet, bitter, and astringent foods: coconut, cucumber, "
                "leafy greens, sweet fruits, dairy, basmati rice. Avoid spicy, sour, "
                "salty, fermented, or fried foods."
            ),
            "lifestyle": (
                "Avoid excessive heat and direct sun. Engage in moderate, non-competitive "
                "exercise (swimming, moonlit walks). Practice cooling pranayama (sheetali). "
                "Allow time for relaxation and play."
            ),
            "avoid": (
                "Chilli, vinegar, alcohol, red meat, excessive ambition or anger, "
                "working through lunch, hot environments."
            ),
        },
        "Kapha": {
            "diet": (
                "Favour light, warm, dry, and spiced foods: legumes, vegetables, honey, "
                "ginger, turmeric, light grains. Avoid heavy, oily, sweet, or cold foods."
            ),
            "lifestyle": (
                "Regular vigorous exercise — running, cycling, vinyasa yoga. Rise early. "
                "Avoid daytime napping. Seek new experiences and stimulation. "
                "Dry massage (garshana) to stimulate circulation."
            ),
            "avoid": (
                "Dairy, fried foods, excessive sweets, heavy grains like wheat, "
                "oversleeping, sedentary habits, cold and damp environments."
            ),
        },
    }

    # ── Public API ───────────────────────────────────────────────────────────

    def get_questions(self) -> list[dict]:
        """Return all 20 questionnaire questions for frontend rendering.

        Returns:
            List of question dicts (id, category, question, options).
            Options keys are 'a', 'b', 'c'; each has 'text' only (dosha hidden).
        """
        public = []
        for q in self.QUESTIONS:
            public.append(
                {
                    "id": q["id"],
                    "category": q["category"],
                    "question": q["question"],
                    "options": {
                        k: {"text": v["text"]}
                        for k, v in q["options"].items()
                    },
                }
            )
        return public

    def calculate_prakriti(self, answers: dict[str, str]) -> dict:
        """Score answers and determine the user's prakriti.

        Args:
            answers: Mapping of question_id (str) → option key (str 'a'/'b'/'c').
                     E.g. {"1": "a", "2": "b", "3": "c", ...}

        Returns:
            Dict containing:
                - prakriti: dominant dosha name (e.g. "Pitta")
                - dosha_scores: {"vata": int, "pitta": int, "kapha": int}
                - dosha_percentages: {"vata": float, "pitta": float, "kapha": float}
                - prakriti_description: narrative description
                - recommendations: {"diet": str, "lifestyle": str, "avoid": str}
        """
        scores: dict[str, int] = {"vata": 0, "pitta": 0, "kapha": 0}

        # Build a lookup from question id (int) -> options dict
        q_map: dict[int, dict] = {q["id"]: q["options"] for q in self.QUESTIONS}

        for qid_str, chosen in answers.items():
            try:
                qid = int(qid_str)
            except ValueError:
                continue

            options = q_map.get(qid)
            if not options:
                continue

            chosen_lower = chosen.strip().lower()
            option_data = options.get(chosen_lower)
            if option_data:
                dosha = option_data["dosha"]
                scores[dosha] = scores.get(dosha, 0) + 1

        total = sum(scores.values()) or 1  # avoid division by zero

        percentages = {
            d: round(s / total * 100, 1)
            for d, s in scores.items()
        }

        # Determine dominant and secondary doshas
        sorted_doshas = sorted(scores, key=lambda d: scores[d], reverse=True)
        dominant = sorted_doshas[0].capitalize()
        secondary = sorted_doshas[1].capitalize()

        # Build prakriti label
        dom_score = scores[sorted_doshas[0]]
        sec_score = scores[sorted_doshas[1]]

        # If dominant is clearly ahead (>= 3 points) call it single dosha
        if dom_score - sec_score >= 3:
            prakriti = dominant
        else:
            prakriti = f"{dominant}-{secondary}"

        description = self._DESCRIPTIONS.get(
            prakriti,
            self._DESCRIPTIONS.get(dominant, "Your prakriti is unique and balanced."),
        )

        # Recommendations: use dominant dosha
        recommendations = self._RECOMMENDATIONS.get(
            dominant,
            {
                "diet": "Follow a balanced diet suitable to your dominant dosha.",
                "lifestyle": "Maintain a regular daily routine.",
                "avoid": "Consult an Ayurvedic practitioner for personalised guidance.",
            },
        )

        return {
            "prakriti": prakriti,
            "dosha_scores": scores,
            "dosha_percentages": percentages,
            "prakriti_description": description,
            "recommendations": recommendations,
        }
