export const deleteFeedItem = async (feedRepository, feedItemId) => {
  return feedRepository.deleteFeedItem(feedItemId);
};
