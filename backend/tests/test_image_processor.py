from io import BytesIO

from PIL import Image

from app.core.image_processor import ImageProcessor


def image_bytes(size=(12, 34), fmt="PNG"):
    image = Image.new("RGB", size, "red")
    buffer = BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def test_get_image_dimensions_returns_size():
    assert ImageProcessor.get_image_dimensions(image_bytes()) == (12, 34)


def test_get_image_dimensions_returns_none_for_invalid_data():
    assert ImageProcessor.get_image_dimensions(b"not-an-image") is None


def test_is_image_vertical_uses_threshold():
    assert ImageProcessor.is_image_vertical(width=100, height=121) is True
    assert ImageProcessor.is_image_vertical(width=100, height=120) is False


def test_get_image_format_detects_format():
    assert ImageProcessor.get_image_format(image_bytes(fmt="JPEG")) == "JPEG"


def test_get_image_format_returns_none_for_invalid_data():
    assert ImageProcessor.get_image_format(b"bad") is None
