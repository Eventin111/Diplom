import { appConfig } from '../../config/appConfig';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const getComments = async () => {
  await sleep(appConfig.mockDelayMs);
  return [];
};

export const createComment = async (payload) => {
  await sleep(appConfig.mockDelayMs);
  return { id: Date.now(), ...payload };
};
