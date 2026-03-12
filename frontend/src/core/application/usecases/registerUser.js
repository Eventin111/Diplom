import { isValidEmail, isValidPassword, isValidUsername } from '../../domain/services/authPolicy';

export const registerUser = async (authRepository, payload) => {
  const { email, password, username } = payload;

  if (!isValidUsername(username)) {
    throw new Error('Имя пользователя должно содержать не менее 3 символов');
  }

  if (!isValidEmail(email)) {
    throw new Error('Введите корректный email');
  }

  if (!isValidPassword(password)) {
    throw new Error('Пароль должен содержать не менее 6 символов');
  }

  return authRepository.register({ email, password, username });
};

