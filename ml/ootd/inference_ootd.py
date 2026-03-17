from pathlib import Path
import os
import sys

# Some OOTD checkpoints refer to custom modules as `pipelines_ootd.*`.
# Ensure that `ml/ootd` is on sys.path so these imports resolve at runtime.
OOTD_ROOT = Path(__file__).resolve().parent
if str(OOTD_ROOT) not in sys.path:
    sys.path.insert(0, str(OOTD_ROOT))

# Allow tests to import this module even if heavy ML dependencies are not installed.
try:
    import torch
    import numpy as np
    from PIL import Image
    import cv2
    import random
    import time

    from ootd.pipelines_ootd.pipeline_ootd import OotdPipeline
    from ootd.pipelines_ootd.unet_garm_2d_condition import UNetGarm2DConditionModel
    from ootd.pipelines_ootd.unet_vton_2d_condition import UNetVton2DConditionModel
    from diffusers import UniPCMultistepScheduler
    from diffusers import AutoencoderKL

    from transformers import AutoProcessor, CLIPVisionModelWithProjection
    from transformers import CLIPTextModel, CLIPTokenizer

    _HAS_TORCH = True
except ImportError:  # pragma: no cover
    torch = np = Image = cv2 = None
    random = time = None
    OotdPipeline = None
    UNetGarm2DConditionModel = None
    UNetVton2DConditionModel = None
    UniPCMultistepScheduler = None
    AutoencoderKL = None
    AutoProcessor = None
    CLIPVisionModelWithProjection = None
    CLIPTextModel = None
    CLIPTokenizer = None
    _HAS_TORCH = False

# NOTE: paths are resolved relative to the repository root (one level above `ootd/`).
REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS_ROOT = REPO_ROOT / "checkpoints"
VIT_PATH = CHECKPOINTS_ROOT / "clip-vit-large-patch14"
VAE_PATH = CHECKPOINTS_ROOT / "ootd"
MODEL_PATH = CHECKPOINTS_ROOT / "ootd"


class OOTDiffusion:

    def __init__(self, gpu_id, unet_checkpoint_path: str = None):
        if not _HAS_TORCH:
            raise ImportError(
                "OOTDiffusion requires torch, diffusers, transformers, and related dependencies. "
                "Install requirements or mock this class for tests."
            )

        self.gpu_id = gpu_id
        self.device = f'cuda:{gpu_id}' if torch.cuda.is_available() else 'cpu'
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(gpu_id)
            print(f"[OOTDiffusion] Using CUDA device {gpu_id}: {gpu_name}")
        else:
            print("[OOTDiffusion] CUDA not available, using CPU")

        if unet_checkpoint_path is None:
            unet_checkpoint_path = CHECKPOINTS_ROOT / "ootd/ootd_hd/checkpoint-36000"
        unet_checkpoint_path = Path(unet_checkpoint_path)

        vae = AutoencoderKL.from_pretrained(
            VAE_PATH,
            subfolder="vae",
            torch_dtype=torch.float16,
        )

        unet_garm = UNetGarm2DConditionModel.from_pretrained(
            unet_checkpoint_path,
            subfolder="unet_garm",
            torch_dtype=torch.float16,
            use_safetensors=True,
        )
        unet_vton = UNetVton2DConditionModel.from_pretrained(
            unet_checkpoint_path,
            subfolder="unet_vton",
            torch_dtype=torch.float16,
            use_safetensors=True,
        )

        self.pipe = OotdPipeline.from_pretrained(
            MODEL_PATH,
            unet_garm=unet_garm,
            unet_vton=unet_vton,
            vae=vae,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True,
            safety_checker=None,
            requires_safety_checker=False,
        ).to(self.device)

        self.pipe.scheduler = UniPCMultistepScheduler.from_config(self.pipe.scheduler.config)
        
        self.auto_processor = AutoProcessor.from_pretrained(VIT_PATH)
        self.image_encoder = CLIPVisionModelWithProjection.from_pretrained(VIT_PATH).to(self.device)

        self.tokenizer = CLIPTokenizer.from_pretrained(
            MODEL_PATH,
            subfolder="tokenizer",
        )
        self.text_encoder = CLIPTextModel.from_pretrained(
            MODEL_PATH,
            subfolder="text_encoder",
        ).to(self.device)


    def tokenize_captions(self, captions, max_length):
        inputs = self.tokenizer(
            captions, max_length=max_length, padding="max_length", truncation=True, return_tensors="pt"
        )
        return inputs.input_ids


    def __call__(
                self,
                model_type='hd',
                category='upperbody',
                image_garm=None,
                image_vton=None,
                mask=None,
                image_ori=None,
                num_samples=1,
                num_steps=20,
                image_scale=1.0,
                seed=-1,
    ):
        if seed == -1:
            random.seed(time.time())
            seed = random.randint(0, 2147483647)
        print('Initial seed: ' + str(seed))
        generator = torch.manual_seed(seed)
        print(f"[OOTDiffusion] device={self.device}, num_steps={num_steps}, image_scale={image_scale}")

        with torch.no_grad():
            prompt_image = self.auto_processor(images=image_garm, return_tensors="pt").to(self.device)
            prompt_image = self.image_encoder(prompt_image.data['pixel_values']).image_embeds
            prompt_image = prompt_image.unsqueeze(1)
            if model_type == 'hd':
                prompt_embeds = self.text_encoder(self.tokenize_captions([""], 2).to(self.device))[0]
                prompt_embeds[:, 1:] = prompt_image[:]
            elif model_type == 'dc':
                prompt_embeds = self.text_encoder(self.tokenize_captions([category], 3).to(self.device))[0]
                prompt_embeds = torch.cat([prompt_embeds, prompt_image], dim=1)
            else:
                raise ValueError("model_type must be \'hd\' or \'dc\'!")

            images = self.pipe(prompt_embeds=prompt_embeds,
                        image_garm=image_garm,
                        image_vton=image_vton, 
                        mask=mask,
                        image_ori=image_ori,
                        num_inference_steps=num_steps,
                        image_guidance_scale=image_scale,
                        num_images_per_prompt=num_samples,
                        generator=generator,
            ).images

        return images
