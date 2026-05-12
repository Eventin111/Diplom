import { buildAvatarUrl } from '../services/authPolicy';

export const createUserEntity = ({ id, email, username, avatar, avatar_url, status = '', isGuest = false }) => ({
  id,
  email,
  username,
  status: String(status || ''),
  avatar: avatar || avatar_url || buildAvatarUrl(username, isGuest ? '666666' : 'ff0000'),
  isGuest
});

export const sanitizeUserEntity = (user) => {
  if (!user || !user.email || !user.username) {
    return null;
  }

  return createUserEntity(user);
};
