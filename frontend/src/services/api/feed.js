import { fetchLikedFeedIds as fetchLikedFeedIdsUseCase } from '../../core/application/usecases/fetchLikedFeedIds';
import { likeFeedItem as likeFeedItemUseCase } from '../../core/application/usecases/likeFeedItem';
import { unlikeFeedItem as unlikeFeedItemUseCase } from '../../core/application/usecases/unlikeFeedItem';
import { createApiFeedRepository } from '../../core/infrastructure/repositories/apiFeedRepository';

const feedRepository = createApiFeedRepository();

export const fetchLikedFeedIds = async () => fetchLikedFeedIdsUseCase(feedRepository);
export const likeFeedItem = async (feedItemId) => likeFeedItemUseCase(feedRepository, feedItemId);
export const unlikeFeedItem = async (feedItemId) => unlikeFeedItemUseCase(feedRepository, feedItemId);
