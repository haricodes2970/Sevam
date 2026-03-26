"""
Food-symptom correlation engine for Sevam.

Analyzes recent food logs against reported symptoms to identify
Ayurvedic dosha-based correlations and dietary triggers.
"""

from datetime import datetime, timezone, timedelta


# Correlation rules: symptom -> list of (quality_check_fn, dosha, time_window_hours, strength)
# quality_check_fn receives the food log's qualities dict and returns True if correlated

def _is_spicy_or_oily(q: dict) -> bool:
    """Check if food is spicy or oily."""
    return q.get("spicy_bland") == "spicy" or q.get("oily_dry") == "oily"


def _is_heavy(q: dict) -> bool:
    """Check if food is heavy."""
    return q.get("heavy_light") == "heavy"


def _is_cold(q: dict) -> bool:
    """Check if food is cold."""
    return q.get("hot_cold") == "cold"


def _is_spicy(q: dict) -> bool:
    """Check if food is spicy."""
    return q.get("spicy_bland") == "spicy"


def _is_fried_or_spicy(q: dict) -> bool:
    """Check if food is spicy or oily (fried)."""
    return q.get("spicy_bland") == "spicy" or q.get("oily_dry") == "oily"


def _aggravates_pitta(q: dict) -> bool:
    """Check if food aggravates Pitta dosha."""
    impact = q.get("dosha_impact", {})
    return impact.get("pitta") == "aggravates"


def _aggravates_vata(q: dict) -> bool:
    """Check if food aggravates Vata dosha."""
    impact = q.get("dosha_impact", {})
    return impact.get("vata") == "aggravates"


def _aggravates_kapha(q: dict) -> bool:
    """Check if food aggravates Kapha dosha."""
    impact = q.get("dosha_impact", {})
    return impact.get("kapha") == "aggravates"


# Symptom keyword -> list of (check_fn, dosha, hours_window, explanation_template)
CORRELATION_RULES: dict[str, list[tuple]] = {
    "headache": [
        (_is_spicy_or_oily, "Pitta", 12,
         "Spicy and oily food directly aggravates Pitta dosha which governs "
         "digestion and can cause headaches, acidity, and inflammation."),
        (_aggravates_pitta, "Pitta", 12,
         "Pitta-aggravating food heats the blood and increases inflammation, "
         "which can manifest as headaches and migraines."),
    ],
    "migraine": [
        (_is_spicy_or_oily, "Pitta", 12,
         "Spicy, oily food aggravates Pitta and heats the blood, "
         "a common trigger for migraines in Ayurveda."),
    ],
    "acidity": [
        (_is_spicy_or_oily, "Pitta", 6,
         "Spicy and oily food increases Pitta's fire element, leading to "
         "excess acid production in the stomach."),
        (_is_heavy, "Pitta", 6,
         "Heavy meals overwhelm the digestive fire and cause acid buildup."),
    ],
    "bloating": [
        (_is_heavy, "Pitta", 6,
         "Heavy food weakens agni (digestive fire) and creates ama (toxins), "
         "leading to gas and bloating."),
        (_is_cold, "Vata", 6,
         "Cold foods dampen the digestive fire and aggravate Vata, "
         "causing gas accumulation and bloating."),
    ],
    "fatigue": [
        (_aggravates_vata, "Vata", 24,
         "Vata-aggravating foods deplete ojas (vital energy) and "
         "disrupt the body's natural rhythm, causing fatigue."),
    ],
    "cough": [
        (_is_cold, "Kapha", 24,
         "Cold foods and drinks increase Kapha dosha, producing excess "
         "mucus in the respiratory tract and triggering cough."),
        (_aggravates_kapha, "Kapha", 24,
         "Kapha-aggravating foods increase mucus production and "
         "congest the respiratory channels."),
    ],
    "cold": [
        (_is_cold, "Kapha", 24,
         "Cold foods dampen digestive fire and increase Kapha, weakening "
         "respiratory immunity and triggering cold symptoms."),
    ],
    "sore throat": [
        (_is_cold, "Kapha", 24,
         "Cold foods increase Kapha in the throat region, causing "
         "congestion and inflammation."),
    ],
    "stomach pain": [
        (_is_spicy, "Pitta", 6,
         "Spicy food directly irritates the stomach lining and "
         "aggravates Pitta, causing pain and inflammation."),
        (_is_heavy, "Pitta", 6,
         "Heavy meals overload the digestive system, weaken agni, "
         "and create ama that causes stomach pain."),
    ],
    "nausea": [
        (_is_spicy_or_oily, "Pitta", 6,
         "Spicy, oily food aggravates Pitta and disturbs Samana Vayu, "
         "reversing the natural downward flow of digestion and causing nausea."),
    ],
    "anxiety": [
        (_aggravates_vata, "Vata", 24,
         "Vata-aggravating foods destabilize Prana Vayu (the vital air "
         "governing the mind), increasing nervousness and anxiety."),
    ],
    "stress": [
        (_aggravates_vata, "Vata", 24,
         "Irregular and Vata-aggravating eating patterns deplete ojas "
         "and overstimulate the nervous system."),
    ],
    "skin": [
        (_is_fried_or_spicy, "Pitta", 48,
         "Spicy and fried foods heat the blood (Rakta Dhatu) and "
         "aggravate Bhrajaka Pitta, causing skin eruptions and irritation."),
        (_aggravates_pitta, "Pitta", 48,
         "Pitta-aggravating foods impair liver function and push toxins "
         "to the skin for elimination, causing rashes and irritation."),
    ],
    "dizziness": [
        (_aggravates_vata, "Vata", 12,
         "Vata-aggravating foods disturb Prana Vayu and reduce stable "
         "circulation to the brain, causing dizziness."),
    ],
    "vertigo": [
        (_aggravates_vata, "Vata", 12,
         "Vata-aggravating foods disturb the vestibular balance and "
         "Prana Vayu, triggering vertigo episodes."),
    ],
}

# Symptom aliases so partial matches work
_SYMPTOM_ALIASES: dict[str, str] = {
    "head pain": "headache",
    "gastric": "acidity",
    "heartburn": "acidity",
    "gas": "bloating",
    "tired": "fatigue",
    "tiredness": "fatigue",
    "low energy": "fatigue",
    "exhaustion": "fatigue",
    "throat pain": "sore throat",
    "throat hurts": "sore throat",
    "tummy ache": "stomach pain",
    "belly pain": "stomach pain",
    "vomiting": "nausea",
    "rash": "skin",
    "itching": "skin",
    "eczema": "skin",
    "skin irritation": "skin",
    "nervous": "anxiety",
    "panic": "anxiety",
    "worry": "anxiety",
    "insomnia": "anxiety",
    "lightheaded": "dizziness",
    "spinning": "vertigo",
}


class CorrelationEngine:
    """
    Analyzes food-symptom correlations using Ayurvedic principles.

    Takes a reported symptom and recent food logs, then identifies
    dietary triggers based on dosha-quality matching rules.
    """

    def analyze_correlation(self, symptom: str, food_logs: list[dict]) -> dict:
        """
        Analyze correlation between a symptom and recent food logs.

        Args:
            symptom: Reported symptom (e.g. "headache", "acidity")
            food_logs: List of food log dicts from last 48 hours.
                       Each should have 'qualities' dict and 'raw_text' str.
                       Optionally 'timestamp' for time-window filtering.

        Returns:
            Correlation result dict with has_correlation, likely_trigger,
            dosha_aggravated, correlation_strength, explanation, dietary_advice.
        """
        if not symptom or not food_logs:
            return self._no_correlation(symptom)

        # Normalize symptom
        symptom_key = self._normalize_symptom(symptom.lower().strip())
        rules = CORRELATION_RULES.get(symptom_key)

        if not rules:
            return self._no_correlation(symptom)

        # Check each rule against food logs
        for check_fn, dosha, hours_window, explanation_template in rules:
            matching_logs = self._find_matching_logs(
                food_logs, check_fn, hours_window
            )
            if matching_logs:
                trigger_foods = [log.get("raw_text", "unknown food") for log in matching_logs]
                trigger_str = ", ".join(trigger_foods[:3])

                qualities = matching_logs[0].get("qualities", {})
                quality_desc = self._describe_qualities(qualities)

                return {
                    "has_correlation": True,
                    "likely_trigger": f"{quality_desc} meal ({trigger_str})",
                    "dosha_aggravated": dosha,
                    "correlation_strength": self._calc_strength(len(matching_logs)),
                    "explanation": explanation_template,
                    "dietary_advice": self._get_advice(dosha),
                }

        return self._no_correlation(symptom)

    def _normalize_symptom(self, symptom: str) -> str:
        """
        Normalize a symptom string to a canonical key.

        Args:
            symptom: Raw symptom text

        Returns:
            Canonical symptom key for rule lookup
        """
        # Direct match
        if symptom in CORRELATION_RULES:
            return symptom

        # Alias match
        for alias, canonical in _SYMPTOM_ALIASES.items():
            if alias in symptom:
                return canonical

        # Partial match against rule keys
        for key in CORRELATION_RULES:
            if key in symptom:
                return key

        return symptom

    def _find_matching_logs(
        self, logs: list[dict], check_fn, hours_window: int
    ) -> list[dict]:
        """
        Filter food logs that match a quality check within a time window.

        Args:
            logs: Food log dicts with 'qualities' and optional 'timestamp'
            check_fn: Function that takes qualities dict and returns bool
            hours_window: How many hours back to look

        Returns:
            List of matching food log dicts
        """
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=hours_window)
        matches = []

        for log in logs:
            qualities = log.get("qualities", {})
            if not qualities:
                continue

            # Time filter if timestamp available
            ts = log.get("timestamp")
            if ts and isinstance(ts, datetime):
                # Ensure both datetimes are comparable (handle naive vs aware)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts < cutoff:
                    continue

            if check_fn(qualities):
                matches.append(log)

        return matches

    def _describe_qualities(self, qualities: dict) -> str:
        """
        Build a short description of food qualities.

        Args:
            qualities: Food quality dict

        Returns:
            Description string like "spicy oily"
        """
        parts = []
        if qualities.get("spicy_bland") == "spicy":
            parts.append("spicy")
        if qualities.get("oily_dry") == "oily":
            parts.append("oily")
        if qualities.get("heavy_light") == "heavy":
            parts.append("heavy")
        if qualities.get("hot_cold") == "cold":
            parts.append("cold")
        return " ".join(parts) if parts else "triggering"

    def _calc_strength(self, match_count: int) -> str:
        """
        Calculate correlation strength based on number of matching logs.

        Args:
            match_count: Number of food logs that matched the rule

        Returns:
            "HIGH", "MEDIUM", or "LOW"
        """
        if match_count >= 3:
            return "HIGH"
        elif match_count >= 2:
            return "MEDIUM"
        return "LOW"

    def _get_advice(self, dosha: str) -> str:
        """
        Return dietary advice based on the aggravated dosha.

        Args:
            dosha: The aggravated dosha name

        Returns:
            Dietary advice string
        """
        advice = {
            "Pitta": (
                "Avoid spicy, oily, and sour food today. "
                "Have light, cooling meals -- rice, moong dal, cucumber, coconut water. "
                "Eat at regular times and avoid skipping meals."
            ),
            "Vata": (
                "Eat warm, nourishing, grounding meals at regular times. "
                "Include ghee, warm soups, and cooked vegetables. "
                "Avoid cold, raw, and dry foods. Do not skip meals."
            ),
            "Kapha": (
                "Avoid cold, heavy, and sweet foods today. "
                "Have warm, light meals with ginger and pepper. "
                "Drink warm water throughout the day. Avoid dairy and ice cream."
            ),
        }
        return advice.get(dosha, "Eat warm, freshly cooked, balanced meals.")

    def _no_correlation(self, symptom: str) -> dict:
        """
        Return a result indicating no food-symptom correlation found.

        Args:
            symptom: The original symptom string

        Returns:
            Dict with has_correlation=False
        """
        return {
            "has_correlation": False,
            "likely_trigger": None,
            "dosha_aggravated": None,
            "correlation_strength": None,
            "explanation": f"No clear food-symptom correlation found for '{symptom}' in recent food logs.",
            "dietary_advice": "Continue eating balanced, freshly cooked meals at regular times.",
        }
