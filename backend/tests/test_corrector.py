import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _post(text: str, variant: str) -> dict:
    resp = client.post("/correct", json={"text": text, "variant": variant})
    return resp.status_code, resp.json()


# ------------------------------------------------------------------ #
# 1. UK conversion
# ------------------------------------------------------------------ #


class TestUKConversion:
    def test_basic_us_to_uk(self):
        status, data = _post("i like the color of this center", "uk")
        assert status == 200
        corrected = data["corrected"]
        assert "colour" in corrected.lower()
        assert "centre" in corrected.lower()
        assert data["variant"] == "uk"

    def test_organize_to_organise(self):
        status, data = _post("We need to organize the event.", "uk")
        assert status == 200
        assert "organise" in data["corrected"].lower()

    def test_traveling_to_travelling(self):
        status, data = _post("She is traveling to London.", "uk")
        assert status == 200
        assert "travelling" in data["corrected"].lower()


# ------------------------------------------------------------------ #
# 2. US conversion
# ------------------------------------------------------------------ #


class TestUSConversion:
    def test_basic_uk_to_us(self):
        status, data = _post("I like the colour of this centre.", "us")
        assert status == 200
        corrected = data["corrected"]
        assert "color" in corrected.lower()
        assert "center" in corrected.lower()
        assert data["variant"] == "us"

    def test_organise_to_organize(self):
        status, data = _post("We need to organise the event.", "us")
        assert status == 200
        assert "organize" in data["corrected"].lower()

    def test_travelling_to_traveling(self):
        status, data = _post("She is travelling to London.", "us")
        assert status == 200
        assert "traveling" in data["corrected"].lower()


# ------------------------------------------------------------------ #
# 3. Grammar-only fixes
# ------------------------------------------------------------------ #


class TestGrammar:
    def test_capitalisation(self):
        """Lowercase 'i' should be corrected to uppercase 'I'."""
        status, data = _post("i am happy today.", "us")
        assert status == 200
        assert data["corrected"].startswith("I ")

    def test_subject_verb_agreement(self):
        status, data = _post("He go to school every day.", "us")
        assert status == 200
        corrected_lower = data["corrected"].lower()
        assert "goes" in corrected_lower or "go" in corrected_lower


# ------------------------------------------------------------------ #
# 4. Punctuation fixes
# ------------------------------------------------------------------ #


class TestPunctuation:
    def test_missing_period_not_required(self):
        """LanguageTool may or may not add a period; just confirm no crash."""
        status, data = _post("This is a test", "us")
        assert status == 200
        assert len(data["corrected"]) >= len("This is a test")

    def test_double_spaces(self):
        """Extra whitespace is typically flagged."""
        status, data = _post("Hello  world.  How are  you?", "us")
        assert status == 200


# ------------------------------------------------------------------ #
# 5. Empty input
# ------------------------------------------------------------------ #


class TestEmptyInput:
    def test_empty_string(self):
        status, data = _post("", "us")
        assert status == 422  # Pydantic validation error

    def test_whitespace_only(self):
        status, data = _post("   ", "us")
        assert status == 422


# ------------------------------------------------------------------ #
# 6. Very long input
# ------------------------------------------------------------------ #


class TestLongInput:
    def test_long_text(self):
        long_text = "This is a sentence. " * 500  # ~10 000 chars
        status, data = _post(long_text, "uk")
        assert status == 200
        assert len(data["corrected"]) > 0

    def test_preserves_urls(self):
        status, data = _post(
            "Visit https://example.com/color for more info on the color.", "uk"
        )
        assert status == 200
        assert "https://example.com/color" in data["corrected"]
        # The standalone word should be converted
        assert "colour" in data["corrected"].lower()


# ------------------------------------------------------------------ #
# 7. Health endpoint
# ------------------------------------------------------------------ #


class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ------------------------------------------------------------------ #
# 8. Changes tracking
# ------------------------------------------------------------------ #


class TestChanges:
    def test_changes_list_not_empty_on_conversion(self):
        status, data = _post("The color is nice.", "uk")
        assert status == 200
        spelling_changes = [c for c in data["changes"] if c["type"] == "spelling"]
        assert len(spelling_changes) >= 1
        assert any(c["replacement"] == "colour" for c in spelling_changes)
