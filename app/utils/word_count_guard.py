import re
from app.core.logging import logger


def count_words(text: str) -> int:
    """Simple whitespace word count, consistent with the rest of the codebase."""
    return len(text.split()) if text else 0


def enforce_word_limit(text: str, max_words: int, label: str = "content") -> str:
    """
    Hard-caps `text` at `max_words`. If the model overshoots the requested
    word count, this trims the text down at the nearest sentence boundary
    (so we never cut off mid-sentence) instead of silently allowing longer
    output than the user asked for.

    If the text is already within the limit, it is returned unchanged.
    """
    if not text or max_words <= 0:
        return text

    words = text.split()
    if len(words) <= max_words:
        return text

    logger.info(
        f"[WordLimitGuard] {label} exceeded limit ({len(words)} > {max_words} words). Trimming to nearest sentence boundary."
    )

    # Split into sentences so we can trim on a clean boundary rather than
    # mid-word/mid-sentence.
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    kept_sentences = []
    running_word_count = 0

    for sentence in sentences:
        sentence_word_count = len(sentence.split())
        if running_word_count + sentence_word_count > max_words:
            break
        kept_sentences.append(sentence)
        running_word_count += sentence_word_count

    # Edge case: a single sentence alone is longer than the entire limit.
    # Fall back to a hard word-level cut so we still respect the cap.
    if not kept_sentences:
        return " ".join(words[:max_words]).rstrip() + "."

    return " ".join(kept_sentences).strip()


def enforce_word_limit_lines(text: str, max_words: int, label: str = "outline") -> str:
    """
    Hard-caps markdown/outline `text` at `max_words` by trimming whole lines
    from the end. This is safer than sentence-splitting for outlines, since
    headings and bullet points don't reliably end in sentence punctuation
    and splitting mid-structure would produce broken Markdown.
    """
    if not text or max_words <= 0:
        return text

    total_words = count_words(text)
    if total_words <= max_words:
        return text

    logger.info(
        f"[WordLimitGuard] {label} exceeded limit ({total_words} > {max_words} words). Trimming trailing lines."
    )

    lines = text.split("\n")
    kept_lines = []
    running_word_count = 0

    for line in lines:
        line_word_count = count_words(line)
        if running_word_count + line_word_count > max_words and kept_lines:
            break
        kept_lines.append(line)
        running_word_count += line_word_count
        if running_word_count >= max_words:
            break

    return "\n".join(kept_lines).rstrip()
