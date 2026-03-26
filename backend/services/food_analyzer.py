"""
Ayurvedic food quality analyzer for Sevam.

Takes natural language food input and returns Ayurvedic qualities
(hot/cold, heavy/light, spicy/bland, oily/dry, dosha impact).
Uses rule-based keyword matching against a dictionary of ~40 common Indian foods.
"""

from typing import Optional


# Each food entry: (hot_cold, heavy_light, spicy_bland, oily_dry, vata, pitta, kapha)
# dosha values: "aggravates", "pacifies", "neutral"
FOOD_DB: dict[str, dict] = {
    # Grains & staples
    "rice":         {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "pacifies", "kapha": "neutral"},
    "roti":         {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "neutral", "kapha": "neutral"},
    "paratha":      {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "aggravates", "kapha": "aggravates"},
    "idli":         {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "pacifies", "kapha": "neutral"},
    "dosa":         {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "neutral", "kapha": "neutral"},
    "biryani":      {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "spicy", "oily_dry": "oily", "vata": "aggravates", "pitta": "aggravates", "kapha": "neutral"},
    "poha":         {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "neutral", "kapha": "neutral"},
    "upma":         {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "neutral", "kapha": "neutral"},
    "khichdi":      {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "pacifies", "kapha": "pacifies"},

    # Lentils & curries
    "dal":          {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "pacifies", "kapha": "neutral"},
    "sambar":       {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "spicy", "oily_dry": "dry", "vata": "pacifies", "pitta": "neutral", "kapha": "pacifies"},
    "rajma":        {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "spicy", "oily_dry": "oily", "vata": "aggravates", "pitta": "aggravates", "kapha": "neutral"},
    "chole":        {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "spicy", "oily_dry": "oily", "vata": "aggravates", "pitta": "aggravates", "kapha": "neutral"},

    # Dairy
    "curd":         {"hot_cold": "cold", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "neutral", "kapha": "aggravates"},
    "milk":         {"hot_cold": "cold", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "pacifies", "kapha": "aggravates"},
    "buttermilk":   {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "pacifies", "kapha": "pacifies"},
    "paneer":       {"hot_cold": "cold", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "neutral", "kapha": "aggravates"},
    "ghee":         {"hot_cold": "cold", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "pacifies", "kapha": "neutral"},

    # Beverages
    "chai":         {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "spicy", "oily_dry": "dry", "vata": "pacifies", "pitta": "aggravates", "kapha": "pacifies"},
    "coffee":       {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "aggravates", "pitta": "aggravates", "kapha": "pacifies"},
    "cold drink":   {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "aggravates", "pitta": "neutral", "kapha": "aggravates"},
    "coconut water":{"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "pacifies", "kapha": "neutral"},
    "alcohol":      {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "aggravates", "pitta": "aggravates", "kapha": "aggravates"},

    # Fruits
    "banana":       {"hot_cold": "cold", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "pacifies", "kapha": "aggravates"},
    "mango":        {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "aggravates", "kapha": "aggravates"},
    "apple":        {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "neutral", "pitta": "pacifies", "kapha": "pacifies"},
    "pomegranate":  {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "pacifies", "kapha": "pacifies"},
    "watermelon":   {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "neutral", "pitta": "pacifies", "kapha": "neutral"},

    # Vegetables
    "spinach":      {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "neutral", "pitta": "pacifies", "kapha": "pacifies"},
    "potato":       {"hot_cold": "cold", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "dry", "vata": "aggravates", "pitta": "neutral", "kapha": "aggravates"},
    "onion":        {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "spicy", "oily_dry": "dry", "vata": "pacifies", "pitta": "aggravates", "kapha": "pacifies"},
    "garlic":       {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "spicy", "oily_dry": "oily", "vata": "pacifies", "pitta": "aggravates", "kapha": "pacifies"},
    "salad":        {"hot_cold": "cold", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "aggravates", "pitta": "pacifies", "kapha": "pacifies"},
    "soup":         {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "bland", "oily_dry": "dry", "vata": "pacifies", "pitta": "neutral", "kapha": "pacifies"},

    # Spices (used as ingredients)
    "turmeric":     {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "spicy", "oily_dry": "dry", "vata": "pacifies", "pitta": "neutral", "kapha": "pacifies"},
    "ginger":       {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "spicy", "oily_dry": "dry", "vata": "pacifies", "pitta": "neutral", "kapha": "pacifies"},
    "pepper":       {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "spicy", "oily_dry": "dry", "vata": "pacifies", "pitta": "aggravates", "kapha": "pacifies"},
    "chilli":       {"hot_cold": "hot", "heavy_light": "light", "spicy_bland": "spicy", "oily_dry": "dry", "vata": "neutral", "pitta": "aggravates", "kapha": "pacifies"},

    # Sweets & fried
    "jalebi":       {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "aggravates", "kapha": "aggravates"},
    "ladoo":        {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "pacifies", "pitta": "aggravates", "kapha": "aggravates"},
    "fried food":   {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "aggravates", "pitta": "aggravates", "kapha": "aggravates"},
    "ice cream":    {"hot_cold": "cold", "heavy_light": "heavy", "spicy_bland": "bland", "oily_dry": "oily", "vata": "aggravates", "pitta": "neutral", "kapha": "aggravates"},
    "pizza":        {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "spicy", "oily_dry": "oily", "vata": "aggravates", "pitta": "aggravates", "kapha": "aggravates"},
    "burger":       {"hot_cold": "hot", "heavy_light": "heavy", "spicy_bland": "spicy", "oily_dry": "oily", "vata": "aggravates", "pitta": "aggravates", "kapha": "aggravates"},
}

# Aliases mapping common variants to canonical keys
_ALIASES: dict[str, str] = {
    "tea": "chai", "green tea": "chai",
    "soda": "cold drink", "cola": "cold drink", "pepsi": "cold drink", "coke": "cold drink",
    "soft drink": "cold drink", "sprite": "cold drink", "fanta": "cold drink",
    "chaas": "buttermilk", "lassi": "buttermilk",
    "yogurt": "curd", "yoghurt": "curd", "raita": "curd",
    "chapati": "roti", "naan": "roti", "puri": "roti",
    "chili": "chilli", "mirchi": "chilli",
    "aloo": "potato", "palak": "spinach",
    "fries": "fried food", "pakora": "fried food", "samosa": "fried food",
    "vada": "fried food", "bhaji": "fried food",
    "beer": "alcohol", "wine": "alcohol", "whiskey": "alcohol", "rum": "alcohol",
}

# Neutral default for unknown foods
_NEUTRAL = {
    "hot_cold": "neutral", "heavy_light": "light", "spicy_bland": "bland",
    "oily_dry": "dry", "vata": "neutral", "pitta": "neutral", "kapha": "neutral",
}


class FoodAnalyzer:
    """
    Analyzes natural language food descriptions and returns Ayurvedic qualities.

    Uses a rule-based keyword matching approach against a dictionary of
    ~40 common Indian foods with their Ayurvedic properties.
    """

    def __init__(self):
        """Initialize with the built-in food database and aliases."""
        self.food_db = FOOD_DB
        self.aliases = _ALIASES

    def analyze(self, raw_text: str) -> dict:
        """
        Analyze a food description and return Ayurvedic qualities.

        Args:
            raw_text: Natural language food description (e.g. "biryani and cold drink")

        Returns:
            Dict with detected_foods, qualities, dosha_impact, and ayurvedic_summary.
        """
        if not raw_text or not raw_text.strip():
            return self._empty_result(raw_text or "")

        text_lower = raw_text.lower().strip()
        detected_foods = self._detect_foods(text_lower)

        if not detected_foods:
            return self._empty_result(raw_text)

        qualities = self._aggregate_qualities(detected_foods)
        summary = self._build_summary(qualities)

        return {
            "raw_text": raw_text,
            "detected_foods": list(detected_foods.keys()),
            "qualities": qualities,
            "ayurvedic_summary": summary,
        }

    def _detect_foods(self, text: str) -> dict[str, dict]:
        """
        Detect known foods in the text by keyword matching.

        Args:
            text: Lowercased food description

        Returns:
            Dict mapping food name to its quality profile
        """
        found: dict[str, dict] = {}

        # Check aliases first (longer phrases matched before single words)
        for alias, canonical in sorted(self.aliases.items(), key=lambda x: -len(x[0])):
            if alias in text:
                found[alias] = self.food_db[canonical]

        # Check direct food names (longer names first to match "cold drink" before "cold")
        for food, props in sorted(self.food_db.items(), key=lambda x: -len(x[0])):
            if food in text and food not in found:
                found[food] = props

        return found

    def _aggregate_qualities(self, detected: dict[str, dict]) -> dict:
        """
        Aggregate qualities across all detected foods.

        Uses worst-case bias for health impact: if any food is heavy/spicy/oily,
        the overall quality reflects that. For dosha impact, if any food
        aggravates a dosha, the overall = aggravates.

        Args:
            detected: Dict of detected food name -> quality profile

        Returns:
            Aggregated quality dict with dosha_impact sub-dict
        """
        profiles = list(detected.values())

        # For health-relevant qualities, bias toward the more impactful value
        hot_cold = self._worst_case(profiles, "hot_cold", "neutral", priority=["hot", "cold", "neutral"])
        heavy_light = self._worst_case(profiles, "heavy_light", "light", priority=["heavy", "light"])
        spicy_bland = self._worst_case(profiles, "spicy_bland", "bland", priority=["spicy", "bland"])
        oily_dry = self._worst_case(profiles, "oily_dry", "dry", priority=["oily", "dry"])

        # Dosha impact: worst-case aggregation
        dosha_impact = {}
        for dosha in ("vata", "pitta", "kapha"):
            values = [p[dosha] for p in profiles]
            if "aggravates" in values:
                dosha_impact[dosha] = "aggravates"
            elif "pacifies" in values:
                dosha_impact[dosha] = "pacifies"
            else:
                dosha_impact[dosha] = "neutral"

        return {
            "hot_cold": hot_cold,
            "heavy_light": heavy_light,
            "spicy_bland": spicy_bland,
            "oily_dry": oily_dry,
            "dosha_impact": dosha_impact,
        }

    def _worst_case(self, profiles: list[dict], key: str, default: str, priority: list[str]) -> str:
        """
        Return the highest-priority value found for a quality key.

        Priority list is ordered from most impactful to least.
        If any food has the most impactful value, that wins.

        Args:
            profiles: List of food quality profiles
            key: Quality key to check
            default: Default if no profiles
            priority: Ordered list of values, first = highest priority
        """
        values = {p[key] for p in profiles}
        for pval in priority:
            if pval in values:
                return pval
        return default

    def _build_summary(self, qualities: dict) -> str:
        """
        Build a human-readable Ayurvedic summary from aggregated qualities.

        Args:
            qualities: Aggregated quality dict

        Returns:
            Summary string like "Heavy, spicy, oily meal -- aggravates Pitta and Vata doshas"
        """
        descriptors = []
        if qualities["heavy_light"] == "heavy":
            descriptors.append("Heavy")
        else:
            descriptors.append("Light")

        if qualities["spicy_bland"] == "spicy":
            descriptors.append("spicy")

        if qualities["oily_dry"] == "oily":
            descriptors.append("oily")

        if qualities["hot_cold"] == "cold":
            descriptors.append("cooling")
        elif qualities["hot_cold"] == "hot":
            descriptors.append("warming")

        aggravated = [
            dosha.capitalize()
            for dosha, impact in qualities["dosha_impact"].items()
            if impact == "aggravates"
        ]
        pacified = [
            dosha.capitalize()
            for dosha, impact in qualities["dosha_impact"].items()
            if impact == "pacifies"
        ]

        desc = ", ".join(descriptors) + " meal"

        if aggravated:
            desc += f" -- aggravates {' and '.join(aggravated)} dosha"
            if len(aggravated) > 1:
                desc += "s"
        if pacified:
            desc += f". Pacifies {' and '.join(pacified)}"

        return desc

    def _empty_result(self, raw_text: str) -> dict:
        """Return a neutral result when no foods are detected."""
        return {
            "raw_text": raw_text,
            "detected_foods": [],
            "qualities": {
                "hot_cold": "neutral",
                "heavy_light": "light",
                "spicy_bland": "bland",
                "oily_dry": "dry",
                "dosha_impact": {
                    "vata": "neutral",
                    "pitta": "neutral",
                    "kapha": "neutral",
                },
            },
            "ayurvedic_summary": "No known foods detected -- neutral impact assumed",
        }
