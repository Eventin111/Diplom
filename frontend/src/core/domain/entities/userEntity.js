import { buildAvatarUrl } from '../services/authPolicy';

export const createUserEntity = ({ id, email, username, avatar, isGuest = false }) => ({
  id,
  email,
  username,
  avatar: avatar || buildAvatarUrl(username, isGuest ? '666666' : 'ff0000'),
  isGuest
});

export const sanitizeUserEntity = (user) => {
  if (!user || !user.email || !user.username) {
    return null;
  }

  return createUserEntity(user);
};

