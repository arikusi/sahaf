"""Tests for backend.utils."""

from backend.utils import rewrite_image_paths, rewrite_image_paths_for_zip


class TestRewriteImagePaths:
    def test_rewrites_simple_path(self):
        md = "![alt](some/path/img.png)"
        result = rewrite_image_paths(md, "task123")
        assert result == "![alt](/api/images/task123/img.png)"

    def test_rewrites_multiple_images(self, markdown_with_images):
        result = rewrite_image_paths(markdown_with_images, "task123")
        assert "/api/images/task123/image1.png" in result
        assert "/api/images/task123/image2.jpg" in result

    def test_preserves_alt_text(self):
        md = "![My Figure](path/to/fig.png)"
        result = rewrite_image_paths(md, "t1")
        assert "![My Figure]" in result

    def test_no_images_unchanged(self):
        md = "Just plain text, no images."
        result = rewrite_image_paths(md, "t1")
        assert result == md

    def test_empty_string(self):
        assert rewrite_image_paths("", "t1") == ""


class TestRewriteImagePathsForZip:
    def test_rewrites_to_relative(self):
        md = "![alt](some/deep/path/img.png)"
        result = rewrite_image_paths_for_zip(md)
        assert result == "![alt](images/img.png)"

    def test_rewrites_api_paths(self):
        md = "![fig](/api/images/task123/img.png)"
        result = rewrite_image_paths_for_zip(md)
        assert result == "![fig](images/img.png)"

    def test_no_images_unchanged(self):
        md = "No images here."
        result = rewrite_image_paths_for_zip(md)
        assert result == md
