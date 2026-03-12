import { isValidEmail, isValidPassword, isValidUsername } from '../core/domain/services/authPolicy';
import { VALIDATION } from './constants';

export const validateLoginForm = ({ email, password }) => {
  if (!isValidEmail(email)) {
    return 'Введите корректный email';
  }

  if (!isValidPassword(password, VALIDATION.MIN_PASSWORD_LENGTH)) {
    return `Пароль должен содержать не менее ${VALIDATION.MIN_PASSWORD_LENGTH} символов`;
  }

  return '';
};

export const validateRegisterForm = ({ email, password, username }) => {
  if (!isValidUsername(username, VALIDATION.MIN_USERNAME_LENGTH)) {
    return `Имя пользователя должно содержать не менее ${VALIDATION.MIN_USERNAME_LENGTH} символов`;
  }

  return validateLoginForm({ email, password });
};
