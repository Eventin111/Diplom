import { getFeedPosts } from '../../core/application/usecases/getFeedPosts';
import { createMockPostRepository } from '../../core/infrastructure/repositories/mockPostRepository';

const postRepository = createMockPostRepository();

export const getPosts = async () => getFeedPosts(postRepository);
