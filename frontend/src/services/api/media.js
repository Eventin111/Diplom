import { uploadMedia as uploadMediaUseCase } from '../../core/application/usecases/uploadMedia';
import { createApiMediaRepository } from '../../core/infrastructure/repositories/apiMediaRepository';

const mediaRepository = createApiMediaRepository();

export const uploadMedia = async (file) => uploadMediaUseCase(mediaRepository, file);
