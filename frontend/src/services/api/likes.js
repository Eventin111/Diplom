import { apiFetch } from './http';

export const toggleLike = async ({ postId, isLiked }) => {
  if (isLiked) {
    await apiFetch(`/api/v1/feed/${postId}/like`, {
      method: 'DELETE'
    });
    return { postId, isLiked: false };
  }

  await apiFetch(`/api/v1/feed/${postId}/like`, {
    method: 'POST'
  });
  return { postId, isLiked: true };
};
