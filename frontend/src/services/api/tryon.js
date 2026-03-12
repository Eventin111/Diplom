import { appConfig } from '../../config/appConfig';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const runTryOn = async ({ userPhoto, outfitPhoto }) => {
  await sleep(appConfig.mockDelayMs);
  return {
    id: Date.now(),
    resultUrl: userPhoto || outfitPhoto || '',
    status: 'completed'
  };
};
