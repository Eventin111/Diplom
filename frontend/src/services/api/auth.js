import { loginUser } from '../../core/application/usecases/loginUser';
import { logoutUser } from '../../core/application/usecases/logoutUser';
import { registerUser } from '../../core/application/usecases/registerUser';
import { createMockAuthRepository } from '../../core/infrastructure/repositories/mockAuthRepository';

const authRepository = createMockAuthRepository();

export const loginRequest = async (payload) => loginUser(authRepository, payload);
export const registerRequest = async (payload) => registerUser(authRepository, payload);
export const logoutRequest = async () => logoutUser(authRepository);
export const initSessionRequest = async () => authRepository.initializeSession();
