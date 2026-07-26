import re
from typing import List, Tuple

from app.schemas.generate import LintReport

AI_BUZZWORDS = [
    r"\bdelve\b", r"\btestament\b", r"\btapestry\b", r"\butilize\b", r"\butilizing\b",
    r"\bleveraging\b", r"\bsynergy\b", r"\bpivotal\b", r"\bparamount\b", r"\bfurthermore\b",
    r"\bmoreover\b", r"\bin conclusion\b", r"\bit is important to note\b", r"\bit should be noted\b",
    r"\bunderscores\b", r"\bseamlessly\b", r"\bgame-changer\b", r"\brobust\b",
]

BUZZWORD_FIXES = {
    r"\bdelve into\b": "explore",
    r"\bdelve\b": "look into",
    r"\butilize\b": "use",
    r"\butilizing\b": "using",
    r"\bleveraging\b": "using",
    r"\bfurthermore\b": "also",
    r"\bmoreover\b": "in addition",
}

# Words where restarting a sentence with "Additionally" reads more naturally than "In fact"
SOFT_STARTER_WORDS = {"the", "this", "these", "it"}


class HumanizationLinter:
    """Small set of mechanical text cleanup rules: no semicolons, no Oxford commas,
    no em-dashes, no repeated sentence openers, and fewer AI-sounding buzzwords."""

    def clean(self, text: str) -> Tuple[str, LintReport]:
        violations: List[str] = []
        cleaned = text

        cleaned, semicolons_removed = self._fix_semicolons(cleaned, violations)
        cleaned, oxford_commas_removed = self._fix_oxford_commas(cleaned, violations)
        cleaned, hyphens_removed = self._fix_dashes(cleaned, violations)
        cleaned, repetitive_starts_fixed = self._fix_repeated_openers(cleaned, violations)
        cleaned = self._fix_buzzwords(cleaned, violations)

        report = LintReport(
            semicolons_removed=semicolons_removed,
            hyphens_removed=hyphens_removed,
            oxford_commas_removed=oxford_commas_removed,
            repetitive_starts_fixed=repetitive_starts_fixed,
            violations_found=violations,
            is_clean=len(violations) == 0,
        )
        return cleaned, report

    def _fix_semicolons(self, text: str, violations: List[str]) -> Tuple[str, int]:
        count = len(re.findall(r";", text))
        if not count:
            return text, 0
        violations.append(f"Found {count} semicolon(s), split into separate sentences.")

        def split_sentence(match):
            after = match.group(1).lstrip()
            return f". {after[0].upper()}{after[1:]}" if after else "."

        text = re.sub(r";\s*([a-zA-Z])", split_sentence, text)
        text = text.replace(";", ".")
        return text, count

    def _fix_oxford_commas(self, text: str, violations: List[str]) -> Tuple[str, int]:
        and_count = len(re.findall(r",\s+and\b", text, re.IGNORECASE))
        or_count = len(re.findall(r",\s+or\b", text, re.IGNORECASE))
        total = and_count + or_count
        if not total:
            return text, 0
        violations.append(f"Removed {total} Oxford comma(s) before 'and'/'or'.")
        text = re.sub(r",\s+and\b", " and", text, flags=re.IGNORECASE)
        text = re.sub(r",\s+or\b", " or", text, flags=re.IGNORECASE)
        return text, total

    def _fix_dashes(self, text: str, violations: List[str]) -> Tuple[str, int]:
        count = len(re.findall(r"[—–]", text))
        if not count:
            return text, 0
        violations.append(f"Replaced {count} em-dash/en-dash character(s) with a comma.")
        text = re.sub(r"\s*[—–]\s*", ", ", text)
        return text, count

    def _fix_repeated_openers(self, text: str, violations: List[str]) -> Tuple[str, int]:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        fixed_count = 0
        streak = 0
        last_word = ""

        for i, sentence in enumerate(sentences):
            words = sentence.strip().split()
            if not words:
                continue

            first_word = re.sub(r"[^\w]", "", words[0]).lower()
            streak = streak + 1 if first_word == last_word else 1
            last_word = first_word

            if streak >= 3:
                violations.append(f"Sentence {i + 1} repeated the opening word '{words[0]}', reworded it.")
                lead_in = "Additionally, " if first_word in SOFT_STARTER_WORDS else "In fact, "
                words[0] = lead_in + words[0].lower()
                sentences[i] = " ".join(words)
                fixed_count += 1
                streak = 1

        return " ".join(sentences), fixed_count

    def _fix_buzzwords(self, text: str, violations: List[str]) -> str:
        found = []
        for pattern in AI_BUZZWORDS:
            found.extend(re.findall(pattern, text, re.IGNORECASE))

        if not found:
            return text

        violations.append(f"Flagged AI-sounding words: {', '.join(sorted(set(found)))}")
        for pattern, replacement in BUZZWORD_FIXES.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text


linter = HumanizationLinter()
