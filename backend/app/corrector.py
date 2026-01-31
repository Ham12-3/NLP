import re
import language_tool_python
from .schemas import Change

# ---------------------------------------------------------------------------
# Spelling variant dictionaries
# Keys are US spellings, values are UK spellings.
# To go the other way we just reverse the dict.
# ---------------------------------------------------------------------------

_US_TO_UK: dict[str, str] = {
    # -or / -our
    "color": "colour",
    "colors": "colours",
    "colored": "coloured",
    "coloring": "colouring",
    "colorful": "colourful",
    "favor": "favour",
    "favors": "favours",
    "favorite": "favourite",
    "favorites": "favourites",
    "flavor": "flavour",
    "flavors": "flavours",
    "honor": "honour",
    "honors": "honours",
    "honored": "honoured",
    "humor": "humour",
    "humors": "humours",
    "labor": "labour",
    "labors": "labours",
    "neighbor": "neighbour",
    "neighbors": "neighbours",
    "neighborhood": "neighbourhood",
    "rumor": "rumour",
    "rumors": "rumours",
    "savior": "saviour",
    "valor": "valour",
    "vigor": "vigour",
    "behavior": "behaviour",
    "behaviors": "behaviours",
    "endeavor": "endeavour",
    "endeavors": "endeavours",
    # -ize / -ise
    "organize": "organise",
    "organizes": "organises",
    "organized": "organised",
    "organizing": "organising",
    "organization": "organisation",
    "organizations": "organisations",
    "recognize": "recognise",
    "recognizes": "recognises",
    "recognized": "recognised",
    "recognizing": "recognising",
    "realize": "realise",
    "realizes": "realises",
    "realized": "realised",
    "realizing": "realising",
    "apologize": "apologise",
    "apologizes": "apologises",
    "apologized": "apologised",
    "apologizing": "apologising",
    "authorize": "authorise",
    "authorized": "authorised",
    "capitalize": "capitalise",
    "capitalized": "capitalised",
    "categorize": "categorise",
    "categorized": "categorised",
    "centralize": "centralise",
    "centralized": "centralised",
    "characterize": "characterise",
    "characterized": "characterised",
    "customize": "customise",
    "customized": "customised",
    "emphasize": "emphasise",
    "emphasized": "emphasised",
    "finalize": "finalise",
    "finalized": "finalised",
    "generalize": "generalise",
    "generalized": "generalised",
    "initialize": "initialise",
    "initialized": "initialised",
    "maximize": "maximise",
    "minimized": "minimised",
    "minimize": "minimise",
    "modernize": "modernise",
    "normalize": "normalise",
    "normalized": "normalised",
    "optimize": "optimise",
    "optimized": "optimised",
    "prioritize": "prioritise",
    "prioritized": "prioritised",
    "specialize": "specialise",
    "specialized": "specialised",
    "standardize": "standardise",
    "standardized": "standardised",
    "summarize": "summarise",
    "summarized": "summarised",
    "symbolize": "symbolise",
    "symbolized": "symbolised",
    "utilize": "utilise",
    "utilized": "utilised",
    "visualize": "visualise",
    "visualized": "visualised",
    # -er / -re
    "center": "centre",
    "centers": "centres",
    "centered": "centred",
    "fiber": "fibre",
    "fibers": "fibres",
    "liter": "litre",
    "liters": "litres",
    "meter": "metre",
    "meters": "metres",
    "theater": "theatre",
    "theaters": "theatres",
    # -og / -ogue
    "analog": "analogue",
    "catalog": "catalogue",
    "dialog": "dialogue",
    "monolog": "monologue",
    # -ense / -ence
    "defense": "defence",
    "offense": "offence",
    "license": "licence",
    "pretense": "pretence",
    # -l- / -ll-
    "traveling": "travelling",
    "traveled": "travelled",
    "traveler": "traveller",
    "travelers": "travellers",
    "canceled": "cancelled",
    "canceling": "cancelling",
    "counselor": "counsellor",
    "counselors": "counsellors",
    "enrollment": "enrolment",
    "fulfillment": "fulfilment",
    "modeling": "modelling",
    "modeled": "modelled",
    "signaling": "signalling",
    "signaled": "signalled",
    # misc
    "program": "programme",
    "programs": "programmes",
    "programmed": "programmed",
    "gray": "grey",
    "grays": "greys",
    "tire": "tyre",
    "tires": "tyres",
    "airplane": "aeroplane",
    "airplanes": "aeroplanes",
    "artifact": "artefact",
    "artifacts": "artefacts",
    "check": "cheque",
    "checks": "cheques",
    "curb": "kerb",
    "curbs": "kerbs",
    "draft": "draught",
    "drafts": "draughts",
    "jewelry": "jewellery",
    "pajamas": "pyjamas",
    "plow": "plough",
    "plows": "ploughs",
    "skeptic": "sceptic",
    "skeptical": "sceptical",
    "skepticism": "scepticism",
}

_UK_TO_US: dict[str, str] = {v: k for k, v in _US_TO_UK.items()}

# Build fast lookup sets for each direction
_US_WORDS = set(_US_TO_UK.keys())
_UK_WORDS = set(_UK_TO_US.keys())

# Regex to split text into words and non-words while preserving structure
_TOKEN_RE = re.compile(r"([A-Za-z]+|[^A-Za-z]+)")

# URLs and common patterns to leave untouched
_URL_RE = re.compile(
    r"https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)


class TextCorrector:
    """Grammar + variant spelling corrector."""

    def __init__(self) -> None:
        self._tool = language_tool_python.LanguageTool("en-US")

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def correct(
        self, text: str, variant: str
    ) -> tuple[str, list[Change]]:
        changes: list[Change] = []

        # Step 1 - Grammar / punctuation fixes via LanguageTool
        grammar_fixed, grammar_changes = self._fix_grammar(text)
        changes.extend(grammar_changes)

        # Step 2 - Variant spelling conversion
        variant_fixed, spelling_changes = self._convert_variant(
            grammar_fixed, variant
        )
        changes.extend(spelling_changes)

        return variant_fixed, changes

    # ------------------------------------------------------------------
    # Grammar
    # ------------------------------------------------------------------

    def _fix_grammar(self, text: str) -> tuple[str, list[Change]]:
        matches = self._tool.check(text)
        changes: list[Change] = []

        # Apply fixes in reverse offset order so positions stay valid
        corrected = text
        for match in reversed(matches):
            if not match.replacements:
                continue
            replacement = match.replacements[0]
            original = corrected[match.offset : match.offset + match.errorLength]
            if original == replacement:
                continue

            change_type = self._classify_match(match)
            changes.append(
                Change(type=change_type, original=original, replacement=replacement)
            )
            corrected = (
                corrected[: match.offset]
                + replacement
                + corrected[match.offset + match.errorLength :]
            )

        # Reverse so changes appear in document order
        changes.reverse()
        return corrected, changes

    @staticmethod
    def _classify_match(match) -> str:  # type: ignore[no-untyped-def]
        rule_id = (match.ruleId or "").upper()
        category = (match.category or "").upper()
        if "PUNCT" in rule_id or "COMMA" in rule_id or "PUNCT" in category:
            return "punctuation"
        if "SPELL" in rule_id or "TYPO" in rule_id or "SPELL" in category:
            return "spelling"
        return "grammar"

    # ------------------------------------------------------------------
    # Variant spelling
    # ------------------------------------------------------------------

    def _convert_variant(
        self, text: str, variant: str
    ) -> tuple[str, list[Change]]:
        if variant == "uk":
            mapping = _US_TO_UK
            source_words = _US_WORDS
        else:
            mapping = _UK_TO_US
            source_words = _UK_WORDS

        # Find URL spans to skip
        url_spans: list[tuple[int, int]] = []
        for m in _URL_RE.finditer(text):
            url_spans.append((m.start(), m.end()))

        changes: list[Change] = []
        result_parts: list[str] = []
        pos = 0

        for token_match in _TOKEN_RE.finditer(text):
            token = token_match.group()
            start = token_match.start()

            # Skip tokens inside URLs
            in_url = any(s <= start < e for s, e in url_spans)
            if in_url or not token.isalpha():
                result_parts.append(token)
                continue

            lower = token.lower()
            if lower in source_words:
                replacement = mapping[lower]
                # Preserve original casing
                replacement = self._match_case(token, replacement)
                if replacement != token:
                    changes.append(
                        Change(type="spelling", original=token, replacement=replacement)
                    )
                    result_parts.append(replacement)
                    continue

            result_parts.append(token)

        return "".join(result_parts), changes

    @staticmethod
    def _match_case(original: str, replacement: str) -> str:
        if original.isupper():
            return replacement.upper()
        if original[0].isupper():
            return replacement[0].upper() + replacement[1:]
        return replacement


# Module-level singleton (created lazily on first import in main)
_corrector: TextCorrector | None = None


def get_corrector() -> TextCorrector:
    global _corrector
    if _corrector is None:
        _corrector = TextCorrector()
    return _corrector
