export const publishTryOnSession = async (
  tryOnRepository,
  sessionId,
  { caption = '', sourceType = null, sourcePostId = null, hashtags = [] } = {}
) => {
  return tryOnRepository.publishTryOnSession(sessionId, {
    caption,
    sourceType,
    sourcePostId,
    hashtags
  });
};
