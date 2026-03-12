import { appConfig } from '../../config/appConfig';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const toggleLike = async ({ postId, isLiked }) => {
  await sleep(appConfig.mockDelayMs);
  return { postId, isLiked: !isLiked };
};
