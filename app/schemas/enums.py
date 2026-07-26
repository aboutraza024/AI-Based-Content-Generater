from enum import Enum

class ContentType(str, Enum):
    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"

class Tone(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    PERSUASIVE = "persuasive"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"
    AUTHORITATIVE = "authoritative"

class RegionVariant(str, Enum):
    USA = "USA English"
    UK = "UK English"
    AUSTRALIA = "Australia English"
    CANADA = "Canada English"
