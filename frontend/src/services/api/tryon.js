import { appConfig } from '../../config/appConfig';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const buildTryOnUrl = () => `${appConfig.apiBaseUrl}/api/v1/tryon/try-on`;

const blobToJpegFile = async (blob, fallbackName) => {
  const contentType = String(blob?.type || '').toLowerCase();
  if (contentType === 'image/jpeg' || contentType === 'image/jpg') {
    return new File([blob], fallbackName, { type: 'image/jpeg' });
  }

  if (typeof document === 'undefined') {
    return new File([blob], fallbackName, { type: blob.type || 'image/jpeg' });
  }

  const objectUrl = URL.createObjectURL(blob);

  try {
    const img = await new Promise((resolve, reject) => {
      const el = new Image();
      el.onload = () => resolve(el);
      el.onerror = () => reject(new Error('Failed to decode image'));
      el.src = objectUrl;
    });

    const canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth || img.width;
    canvas.height = img.naturalHeight || img.height;
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      throw new Error('Canvas context is not available');
    }
    ctx.drawImage(img, 0, 0);

    const jpegBlob = await new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/jpeg', 0.92);
    });

    if (!jpegBlob) {
      throw new Error('Failed to encode jpg');
    }

    return new File([jpegBlob], fallbackName, { type: 'image/jpeg' });
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
};

const imageInputToFile = async (input, fallbackName, options = {}) => {
  const { preferJpeg = false } = options;

  if (!input) {
    throw new Error('Image input is required');
  }

  if (input instanceof File) {
    return preferJpeg ? blobToJpegFile(input, fallbackName) : input;
  }

  if (input instanceof Blob) {
    if (preferJpeg) {
      return blobToJpegFile(input, fallbackName);
    }
    return new File([input], fallbackName, { type: input.type || 'image/jpeg' });
  }

  if (typeof input === 'string') {
    const response = await fetch(input);
    if (!response.ok) {
      throw new Error(`Failed to fetch image source: ${response.status}`);
    }

    const blob = await response.blob();
    if (preferJpeg) {
      return blobToJpegFile(blob, fallbackName);
    }
    return new File([blob], fallbackName, { type: blob.type || 'image/jpeg' });
  }

  throw new Error('Unsupported image input type');
};

const runTryOnMock = async ({ modelImage, clothImage }) => {
  await sleep(appConfig.mockDelayMs);
  return {
    id: Date.now(),
    resultUrl: typeof modelImage === 'string' ? modelImage : (typeof clothImage === 'string' ? clothImage : ''),
    status: 'completed',
    raw: { success: true, results: [], count: 0, mock: true }
  };
};

export const runTryOn = async ({
  modelImage,
  clothImage,
  modelType = 'hd',
  category = 0,
  scale = 2.0,
  numSteps = 4,
  numSamples = 1,
  seed = -1
}) => {
  const modelImageFile = await imageInputToFile(modelImage, 'model-image.jpg');
  const clothImageFile = await imageInputToFile(clothImage, 'cloth-image.jpg', { preferJpeg: true });

  const formData = new FormData();
  formData.append('model_image', modelImageFile);
  formData.append('cloth_image', clothImageFile);
  formData.append('model_type', modelType);
  formData.append('category', String(category));
  formData.append('scale', String(scale));
  formData.append('num_steps', String(numSteps));
  formData.append('num_samples', String(numSamples));
  formData.append('seed', String(seed));

  try {
    const response = await fetch(buildTryOnUrl(), {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      let detail = '';
      try {
        const payload = await response.json();
        detail = payload?.detail || JSON.stringify(payload);
      } catch (error) {
        detail = await response.text();
      }
      throw new Error(`Try-on request failed: ${response.status} ${detail}`);
    }

    const payload = await response.json();
    return {
      id: Date.now(),
      resultUrl: payload?.results?.[0] || '',
      status: payload?.success ? 'completed' : 'failed',
      raw: payload
    };
  } catch (error) {
    if (appConfig.useMockData) {
      return runTryOnMock({ modelImage, clothImage });
    }
    if (error instanceof TypeError) {
      throw new Error(
        'Сетевой доступ к API недоступен (возможен CORS или неверный API URL). Проверь, что backend запущен и разрешает текущий origin.'
      );
    }

    throw error;
  }
};
