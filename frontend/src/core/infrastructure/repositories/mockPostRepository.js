import { appConfig } from '../../../config/appConfig';
import { MOCK_POSTS } from '../mocks/posts';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const createMockPostRepository = (deps = {}) => {
  const config = deps.config || appConfig;

  return {
    async getFeedPosts() {
      await sleep(config.mockDelayMs);
      return [...MOCK_POSTS];
    }
  };
};

