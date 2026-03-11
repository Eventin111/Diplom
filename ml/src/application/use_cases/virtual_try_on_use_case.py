from domain.entities import TryOnResult
from application.dto import TryOnRequest
from adapters.model.ootd_model_port import AbstractOOTDModel
from adapters.preprocessor.image_preprocessor_port import AbstractImagePreprocessor

class VirtualTryOnUseCase:
    def __init__(self, preprocessor: AbstractImagePreprocessor, model: AbstractOOTDModel):
        self.preprocessor = preprocessor
        self.model = model

    def execute(self, request: TryOnRequest) -> TryOnResult:
        person = self.preprocessor.preprocess_person(request.person_image_path)
        cloth = self.preprocessor.preprocess_cloth(request.cloth_image_path)

        generated_paths = self.model.generate(
            person=person,
            garment=cloth,
            scale=request.scale,
            num_samples=request.num_samples,
            model_type=request.model_type,
            category=request.category,
            steps=request.steps,
            seed=request.seed,
        )
        return TryOnResult(generated_images=generated_paths)