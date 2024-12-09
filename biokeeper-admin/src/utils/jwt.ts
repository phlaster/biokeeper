function decodeAccessToken(accessToken: string) {
  if (accessToken) {
    const base64Url = accessToken.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map((c) => `%${(`00${c.charCodeAt(0).toString(16)}`).slice(-2)}`).join(''));

    return JSON.parse(jsonPayload);
  } else {
    return null;
  }
}

export { decodeAccessToken }