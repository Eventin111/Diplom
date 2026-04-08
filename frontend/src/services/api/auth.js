import { loginUser } from '../../core/application/usecases/loginUser';
import { logoutUser } from '../../core/application/usecases/logoutUser';
import { registerUser } from '../../core/application/usecases/registerUser';
import { createBackendAuthRepository } from '../../core/infrastructure/repositories/backendAuthRepository';

const authRepository = createBackendAuthRepository();

export const loginRequest = async (payload) => loginUser(authRepository, payload);
export const registerRequest = async (payload) => registerUser(authRepository, payload);
export const logoutRequest = async () => logoutUser(authRepository);
export const initSessionRequest = async () => authRepository.initializeSession();
