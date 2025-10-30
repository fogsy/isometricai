from PIL import Image

from backend.app.inference import ModelRunner


def test_predict_image_returns_probability() -> None:
    runner = ModelRunner()
    image = Image.new("RGB", (32, 32), color=(255, 0, 0))
    probability = runner.predict_image(image)
    assert 0.0 <= probability <= 1.0
