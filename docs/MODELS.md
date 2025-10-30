# Open-Source Model Options

The default configuration loads the [OpenCLIP](https://github.com/mlfoundations/open_clip) ViT-B/32 encoder with a lightweight logistic regression head (`backend/checkpoints/clip_logreg.json`). This head can be retrained using the evaluation tooling.

Alternative detectors to experiment with:

1. [`orviproject/vidgen-detector`](https://huggingface.co/orviproject/vidgen-detector)
2. [`facebook/convnextv2-base-22k-224`](https://huggingface.co/facebook/convnextv2-base-22k-224) fine-tuned for synthetic media detection.
3. [`seferbekov/deepfake-detection`](https://huggingface.co/seferbekov/deepfake-detection) (Xception-based deepfake detector).
4. [`laion/clippier-synthetic-detector`](https://huggingface.co/laion/clippier-synthetic-detector).
5. [`facebookresearch/dfdc`](https://ai.facebook.com/datasets/dfdc/) EfficientNet baseline models.

Update `backend/app/config.py` to point to a new model and extend `backend/app/inference.py` to add appropriate preprocessing if switching architectures.
