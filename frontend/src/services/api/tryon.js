import { getTryOnSession as getTryOnSessionUseCase } from '../../core/application/usecases/getTryOnSession';
import { startTryOnSession } from '../../core/application/usecases/startTryOnSession';
import { subscribeToTryOnSession as subscribeToTryOnSessionUseCase } from '../../core/application/usecases/subscribeToTryOnSession';
import { createApiTryOnRepository } from '../../core/infrastructure/repositories/apiTryOnRepository';

const tryOnRepository = createApiTryOnRepository();

export const runTryOn = async (payload) => startTryOnSession(tryOnRepository, payload);
export const getTryOnSession = async (sessionId) => getTryOnSessionUseCase(tryOnRepository, sessionId);
export const subscribeToTryOnSession = (sessionId, handlers) =>
  subscribeToTryOnSessionUseCase(tryOnRepository, sessionId, handlers);
