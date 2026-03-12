import { appConfig } from '../../config/appConfig';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const getWardrobeItems = async () => {
  await sleep(appConfig.mockDelayMs);
  return [];
};
