"""Shared test fixtures."""

import pytest


@pytest.fixture
def sample_markdown():
    return """\
# Chapter 1

This is the first chapter with some content.

## Section 1.1

More detailed content here.

---

# Chapter 2

Second chapter starts here.

## Section 2.1

Final section content.
"""


@pytest.fixture
def markdown_with_images():
    return """\
# Document

Some text before.

![Figure 1](some/path/image1.png)

More text.

![Figure 2](another/path/image2.jpg)
"""
