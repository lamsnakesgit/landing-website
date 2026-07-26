"""
Unit tests for granola-export.

Tests pure functions only — no live API calls. Run with:

    python3 -m unittest tests.test_api -v

…or:

    python3 tests/test_api.py
"""

import os
import sys
import unittest

# Make `scripts/api.py` importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from api import pm_to_md  # noqa: E402

# slugify lives in extract.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from extract import slugify, fmt_attendees, fmt_transcript  # noqa: E402


class TestProseMirrorToMarkdown(unittest.TestCase):
    """pm_to_md: ProseMirror JSON → Markdown."""

    def test_none(self):
        self.assertEqual(pm_to_md(None), "")

    def test_bare_string(self):
        # Defensive: Granola sometimes returns a string where a node is expected
        self.assertEqual(pm_to_md("hello"), "hello")

    def test_unknown_type(self):
        # Non-dict, non-string, non-list, non-None — coerced via str()
        self.assertEqual(pm_to_md(42), "42")

    def test_text_node(self):
        node = {"type": "text", "text": "hello"}
        self.assertEqual(pm_to_md(node), "hello")

    def test_text_with_bold_mark(self):
        node = {"type": "text", "text": "hello", "marks": [{"type": "bold"}]}
        self.assertEqual(pm_to_md(node), "**hello**")

    def test_text_with_italic_and_code(self):
        node = {"type": "text", "text": "hi", "marks": [{"type": "italic"}, {"type": "code"}]}
        # Marks compose in order
        self.assertEqual(pm_to_md(node), "`*hi*`")

    def test_text_with_link(self):
        node = {
            "type": "text",
            "text": "click",
            "marks": [{"type": "link", "attrs": {"href": "https://example.com"}}],
        }
        self.assertEqual(pm_to_md(node), "[click](https://example.com)")

    def test_paragraph(self):
        node = {"type": "paragraph", "content": [{"type": "text", "text": "hello"}]}
        self.assertEqual(pm_to_md(node), "hello\n\n")

    def test_heading_level_1(self):
        node = {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Title"}]}
        self.assertEqual(pm_to_md(node), "\n# Title\n\n")

    def test_heading_default_level(self):
        # Missing attrs defaults to level 2
        node = {"type": "heading", "content": [{"type": "text", "text": "Sub"}]}
        self.assertEqual(pm_to_md(node), "\n## Sub\n\n")

    def test_bullet_list(self):
        node = {
            "type": "bulletList",
            "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "one"}]}
                ]},
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "two"}]}
                ]},
            ],
        }
        result = pm_to_md(node)
        self.assertIn("- one", result)
        self.assertIn("- two", result)

    def test_code_block_with_language(self):
        node = {
            "type": "codeBlock",
            "attrs": {"language": "python"},
            "content": [{"type": "text", "text": "print('hi')"}],
        }
        self.assertIn("```python", pm_to_md(node))
        self.assertIn("print('hi')", pm_to_md(node))

    def test_blockquote(self):
        node = {
            "type": "blockquote",
            "content": [{"type": "paragraph", "content": [{"type": "text", "text": "quoted"}]}],
        }
        self.assertIn("> quoted", pm_to_md(node))

    def test_hard_break(self):
        self.assertEqual(pm_to_md({"type": "hardBreak"}), "\n")

    def test_doc_root(self):
        node = {
            "type": "doc",
            "content": [
                {"type": "heading", "attrs": {"level": 1}, "content": [{"type": "text", "text": "Title"}]},
                {"type": "paragraph", "content": [{"type": "text", "text": "Body"}]},
            ],
        }
        result = pm_to_md(node)
        self.assertIn("# Title", result)
        self.assertIn("Body", result)

    def test_list_of_nodes(self):
        # Top-level list (e.g. content array passed directly)
        nodes = [
            {"type": "text", "text": "a"},
            {"type": "text", "text": "b"},
        ]
        self.assertEqual(pm_to_md(nodes), "ab")

    def test_marks_with_non_dict_skipped(self):
        # Defensive: malformed marks shouldn't crash
        node = {"type": "text", "text": "hi", "marks": ["not a dict", {"type": "bold"}]}
        self.assertEqual(pm_to_md(node), "**hi**")

    def test_text_with_None_marks(self):
        # marks: None should not crash
        node = {"type": "text", "text": "hi", "marks": None}
        self.assertEqual(pm_to_md(node), "hi")

    def test_unknown_node_type_recurses_into_content(self):
        # Unknown types fall through to recursing into .content
        node = {"type": "weirdCustomType", "content": [{"type": "text", "text": "still works"}]}
        self.assertEqual(pm_to_md(node), "still works")


class TestSlugify(unittest.TestCase):
    """slugify: doc title → filesystem-safe slug."""

    def test_basic(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_punctuation_stripped(self):
        self.assertEqual(slugify("Quarterly review: numbers!"), "quarterly-review-numbers")

    def test_collapse_dashes(self):
        self.assertEqual(slugify("a -- b ---- c"), "a-b-c")

    def test_empty_string(self):
        self.assertEqual(slugify(""), "untitled")

    def test_none(self):
        self.assertEqual(slugify(None), "untitled")

    def test_only_punctuation(self):
        # If everything strips out, fall back to "untitled"
        self.assertEqual(slugify("!!!"), "untitled")

    def test_max_length(self):
        long = "a" * 200
        self.assertEqual(len(slugify(long)), 80)
        self.assertEqual(len(slugify(long, maxlen=10)), 10)

    def test_unicode_word_chars_preserved(self):
        # \w in Python's re includes unicode word chars by default
        result = slugify("café meeting")
        self.assertIn("café", result.lower())

    def test_leading_trailing_whitespace(self):
        self.assertEqual(slugify("  hello  "), "hello")

    def test_newline_in_title(self):
        # Granola's AI title-generator occasionally produces multi-line titles.
        # Newlines must NOT survive into filenames (breaks shell tools, archives, etc.)
        result = slugify("line one\nline two")
        self.assertNotIn("\n", result)
        self.assertEqual(result, "line-one-line-two")

    def test_tab_in_title(self):
        self.assertNotIn("\t", slugify("col1\tcol2"))

    def test_mixed_whitespace_collapses(self):
        # Multiple whitespace chars (spaces, newlines, tabs) → single hyphen
        result = slugify("foo \n\t bar")
        self.assertEqual(result, "foo-bar")


class TestFormatAttendees(unittest.TestCase):
    """fmt_attendees: doc.people → markdown attendee list."""

    def test_none(self):
        self.assertEqual(fmt_attendees(None), "")

    def test_empty_dict(self):
        self.assertEqual(fmt_attendees({}), "")

    def test_organizer_only(self):
        people = {"organizer": {"email": "a@x.com", "displayName": "Alice"}}
        self.assertIn("Alice", fmt_attendees(people))
        self.assertIn("a@x.com", fmt_attendees(people))

    def test_attendees_list(self):
        people = {"attendees": [
            {"email": "a@x.com", "displayName": "Alice"},
            {"email": "b@x.com", "displayName": "Bob"},
        ]}
        result = fmt_attendees(people)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)

    def test_dedup(self):
        # Same email in organizer + attendees → only one line
        people = {
            "organizer": {"email": "a@x.com", "displayName": "Alice"},
            "attendees": [{"email": "a@x.com", "displayName": "Alice"}],
        }
        result = fmt_attendees(people)
        self.assertEqual(result.count("Alice"), 1)

    def test_email_only_no_name(self):
        people = {"attendees": [{"email": "a@x.com"}]}
        self.assertIn("a@x.com", fmt_attendees(people))


class TestFormatTranscript(unittest.TestCase):
    """fmt_transcript: transcript array → readable markdown."""

    def test_empty(self):
        self.assertEqual(fmt_transcript([]), "(no transcript)")

    def test_none(self):
        self.assertEqual(fmt_transcript(None), "(no transcript)")

    def test_basic_segment(self):
        segments = [{
            "start_timestamp": "2025-06-17T19:02:29.419Z",
            "text": "hello world",
            "source": "microphone",
        }]
        result = fmt_transcript(segments)
        self.assertIn("19:02:29", result)
        self.assertIn("[MIC]", result)
        self.assertIn("hello world", result)

    def test_system_audio_label(self):
        segments = [{
            "start_timestamp": "2025-06-17T19:02:29.419Z",
            "text": "from the other person",
            "source": "system",
        }]
        self.assertIn("[SYS]", fmt_transcript(segments))

    def test_unknown_source(self):
        segments = [{"start_timestamp": "2025-06-17T19:02:29Z", "text": "x", "source": "weird"}]
        self.assertIn("[WEIRD]", fmt_transcript(segments))

    def test_empty_text_skipped(self):
        segments = [
            {"start_timestamp": "2025-06-17T19:02:29Z", "text": "  ", "source": "microphone"},
            {"start_timestamp": "2025-06-17T19:02:30Z", "text": "real", "source": "microphone"},
        ]
        result = fmt_transcript(segments)
        self.assertIn("real", result)
        # The whitespace-only segment shouldn't add a line
        self.assertEqual(result.count("\n"), 0)

    def test_malformed_segment_skipped(self):
        segments = [
            "not a dict",
            {"start_timestamp": "2025-06-17T19:02:29Z", "text": "real", "source": "microphone"},
        ]
        result = fmt_transcript(segments)
        self.assertIn("real", result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
