import { apiFetch } from './http';

const DEMO_FEED_LIMIT = 200;

export const getPosts = async ({ skip = 0, limit = 20 } = {}) => {
  const query = new URLSearchParams({
    skip: String(skip),
    limit: String(limit)
  });
  const payload = await apiFetch(`/api/v1/feed?${query.toString()}`, { method: 'GET' });
  return payload?.items || [];
};

const createGarment = async (post) =>
  apiFetch('/api/v1/garments/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      title: post?.outfit?.type || `Outfit ${post?.id || ''}`,
      brand: post?.outfit?.brand || null,
      media_id: null,
      garment_metadata: {
        source: 'frontend_demo_feed',
        local_post_id: post?.id || null,
        tags: post?.tags || [],
        price: post?.outfit?.price || null
      }
    })
  });

const createFeedItem = async (post, garmentId) =>
  apiFetch('/api/v1/feed/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      caption: post?.description || '',
      garment_id: garmentId || null,
      media_ids: []
    })
  });

export const ensureDemoFeedPosts = async (samplePosts = []) => {
  if (!Array.isArray(samplePosts) || samplePosts.length === 0) {
    return [];
  }

  const existingItems = await getPosts({ skip: 0, limit: DEMO_FEED_LIMIT });
  const existingCaptions = new Set(existingItems.map((item) => String(item?.caption || '').trim()));

  for (const post of samplePosts) {
    const caption = String(post?.description || '').trim();
    if (!caption || existingCaptions.has(caption)) {
      continue;
    }

    const garment = await createGarment(post);
    await createFeedItem(post, garment?.id);
    existingCaptions.add(caption);
  }

  return getPosts({ skip: 0, limit: DEMO_FEED_LIMIT });
};
