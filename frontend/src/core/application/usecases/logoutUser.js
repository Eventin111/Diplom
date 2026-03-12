export const logoutUser = async (authRepository) => {
  authRepository.logout();
  return true;
};

