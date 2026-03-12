import { isValidEmail, isValidPassword } from '../../domain/services/authPolicy';

export const loginUser = async (authRepository, payload) => {
  const { email, password } = payload;

  if (!isValidEmail(email)) {
    throw new Error('Введите корректный email');
  }

  if (!isValidPassword(password)) {
    throw new Error('Пароль должен содержать не менее 6 символов');
  }

  return authRepository.login({ email, password });
};

