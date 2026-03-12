import { appConfig } from '../../config/appConfig';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const getCurrentUser = async () => {
  await sleep(appConfig.mockDelayMs);
  return null;
};
