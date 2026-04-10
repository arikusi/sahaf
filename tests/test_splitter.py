"""Tests for backend.splitter."""

from backend.splitter import split_markdown


class TestSplitMarkdown:
    def test_empty_string(self):
        result = split_markdown("", 3)
        assert result == [""]

    def test_single_part_returns_original(self, sample_markdown):
        result = split_markdown(sample_markdown, 1)
        assert result == [sample_markdown]

    def test_split_into_two(self, sample_markdown):
        result = split_markdown(sample_markdown, 2)
        assert len(result) == 2
        combined = "\n\n".join(result)
        for heading in ["# Chapter 1", "# Chapter 2"]:
            assert heading in combined

    def test_split_respects_headings(self, sample_markdown):
        result = split_markdown(sample_markdown, 2)
        assert result[0].startswith("# Chapter 1")
        assert result[1].lstrip().startswith("#") or result[1].lstrip().startswith("---")

    def test_no_headings_splits_at_paragraphs(self):
        text = "Para one.\n\nPara two.\n\nPara three.\n\nPara four."
        result = split_markdown(text, 2)
        assert len(result) == 2

    def test_large_num_parts(self):
        text = "Short text."
        result = split_markdown(text, 100)
        assert len(result) >= 1
        assert all(len(part) > 0 for part in result)

    def test_all_content_preserved(self, sample_markdown):
        parts = split_markdown(sample_markdown, 3)
        combined = " ".join(parts)
        assert "Chapter 1" in combined
        assert "Chapter 2" in combined
        assert "Section 1.1" in combined
        assert "Section 2.1" in combined
