from __future__ import annotations

from dataclasses import dataclass
from html import escape
import re


MIN_DREAM_WORDS = 8


THEMES = {
    "water": {
        "keywords": {"water", "ocean", "sea", "river", "rain", "wave", "flood", "lake"},
        "label": "emotional movement",
        "palette": ("#12355b", "#2f80a8", "#d8f3f0"),
        "symbol": "Water often points to changing feelings, memory, or the need to move through an uncertain state.",
    },
    "flight": {
        "keywords": {"fly", "flying", "float", "sky", "cloud", "wing", "air"},
        "label": "freedom and perspective",
        "palette": ("#2d3a73", "#79addc", "#f5d36c"),
        "symbol": "Flight can suggest a wish for perspective, freedom, or distance from a pressure point.",
    },
    "chase": {
        "keywords": {"chase", "chased", "running", "hide", "escape", "pursue", "pursued"},
        "label": "pressure and avoidance",
        "palette": ("#2b2d42", "#8d3b3b", "#f2c57c"),
        "symbol": "Being chased can reflect pressure, avoidance, or a conflict asking for attention.",
    },
    "home": {
        "keywords": {"home", "house", "room", "door", "window", "bed", "kitchen"},
        "label": "identity and safety",
        "palette": ("#344e41", "#a3b18a", "#f2e8cf"),
        "symbol": "Homes and rooms often connect to identity, privacy, comfort, or parts of life being reorganized.",
    },
    "forest": {
        "keywords": {"forest", "tree", "garden", "path", "mountain", "field", "flower"},
        "label": "growth and uncertainty",
        "palette": ("#1b4332", "#74c69d", "#fff3b0"),
        "symbol": "Natural places can suggest growth, uncertainty, renewal, or a search for direction.",
    },
}


STYLE_DESCRIPTIONS = {
    "Watercolor": "soft watercolor textures, translucent edges, gentle layered washes",
    "Surreal": "surreal dream logic, symbolic scale shifts, luminous impossible scenery",
    "Cinematic": "cinematic lighting, dramatic composition, atmospheric depth",
    "Abstract": "abstract symbolic forms, expressive shapes, emotional color fields",
}


@dataclass(frozen=True)
class ThemeMatch:
    key: str
    score: int


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z']+", text.lower()))


def _match_theme(text: str) -> str:
    tokens = _tokens(text)
    matches = [
        ThemeMatch(key=key, score=len(tokens & data["keywords"]))
        for key, data in THEMES.items()
    ]
    best = max(matches, key=lambda item: item.score)
    return best.key if best.score > 0 else "forest"


def _extract_symbols(text: str) -> list[str]:
    tokens = _tokens(text)
    symbols: list[str] = []
    for data in THEMES.values():
        found = sorted(tokens & data["keywords"])
        symbols.extend(found[:2])
    return symbols[:5]


def analyze_dream(dream_text: str, style: str = "Watercolor") -> dict:
    cleaned = " ".join(dream_text.split())
    word_count = len(cleaned.split())
    if word_count < MIN_DREAM_WORDS:
        return {
            "ready": False,
            "warnings": [
                "A fuller dream description is required before creating a respectful interpretation."
            ],
            "summary": "Add more detail about what happened, where it happened, and how it felt.",
            "insights": [],
            "visual": {},
        }

    selected_style = style if style in STYLE_DESCRIPTIONS else "Watercolor"
    theme_key = _match_theme(cleaned)
    theme = THEMES[theme_key]
    symbols = _extract_symbols(cleaned)
    symbol_text = ", ".join(symbols) if symbols else "the setting and emotional tone"

    insights = [
        {
            "label": "Emotional state",
            "text": (
                f"The dream carries a tone of {theme['label']}. Treat this as a cue to notice "
                "what feelings are asking for space rather than as a fixed conclusion."
            ),
        },
        {
            "label": "Symbolic pattern",
            "text": theme["symbol"],
        },
        {
            "label": "Personal aspiration",
            "text": (
                "The movement through the scene may point to a wish for more agency, clarity, "
                "or permission to approach something from a different angle."
            ),
        },
        {
            "label": "Tension to explore",
            "text": (
                f"The strongest symbols appear to be {symbol_text}. They may be useful prompts "
                "for reflection, especially if they connect to recent choices or transitions."
            ),
        },
    ]

    image_prompt = (
        f"{selected_style} artwork of a dream about {symbol_text}, "
        f"focused on {theme['label']}; {STYLE_DESCRIPTIONS[selected_style]}; "
        "respectful, contemplative, symbolic, no text in image"
    )

    return {
        "ready": True,
        "warnings": [
            "This is a creative reflection, not psychological diagnosis or professional advice."
        ],
        "summary": (
            f"This dream reads as a symbolic scene about {theme['label']}, with imagery that "
            "can support personal reflection without claiming one definitive meaning."
        ),
        "theme": theme["label"],
        "symbols": symbols,
        "insights": insights,
        "visual": {
            "style": selected_style,
            "palette": list(theme["palette"]),
            "alt_text": f"{selected_style} visual representation of a dream about {theme['label']}.",
            "image_prompt": image_prompt,
            "svg": render_dream_svg(theme_key, selected_style, symbols),
        },
    }


def render_dream_svg(theme_key: str, style: str, symbols: list[str] | None = None) -> str:
    theme = THEMES.get(theme_key, THEMES["forest"])
    dark, mid, light = theme["palette"]
    symbol_label = escape(", ".join(symbols or [theme["label"]]))
    style_label = escape(style)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 560" role="img" aria-label="{style_label} dream visual">
  <rect width="900" height="560" fill="{dark}"/>
  <circle cx="690" cy="120" r="92" fill="{light}" opacity="0.88"/>
  <circle cx="250" cy="220" r="150" fill="{mid}" opacity="0.42"/>
  <path d="M0 410 C140 330 255 475 405 390 C555 305 660 420 900 330 L900 560 L0 560 Z" fill="{mid}" opacity="0.84"/>
  <path d="M90 360 C220 290 330 405 460 335 C600 260 720 340 840 280" fill="none" stroke="{light}" stroke-width="9" opacity="0.72"/>
  <path d="M180 462 C280 410 385 470 480 425 C610 365 700 425 790 380" fill="none" stroke="#ffffff" stroke-width="4" opacity="0.38"/>
  <text x="56" y="78" fill="#ffffff" font-family="Arial, sans-serif" font-size="34" font-weight="700">{style_label} dreamscape</text>
  <text x="56" y="122" fill="#ffffff" font-family="Arial, sans-serif" font-size="22" opacity="0.82">{symbol_label}</text>
</svg>"""


def format_insight_count(result: dict) -> str:
    count = len(result.get("insights", []))
    return f"{count} insights generated"
