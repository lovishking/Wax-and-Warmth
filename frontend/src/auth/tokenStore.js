let accessToken = null;

export const tokenStore = {
  getAccess: () => accessToken,
  set: ({ access }) => { accessToken = access || null; },
  clear: () => { accessToken = null; },
};
