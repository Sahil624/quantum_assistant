export function setAccessToken(token: string) {
    localStorage.setItem('token', token);
}

export function getAccessToken(): string | null {
    let token = localStorage.getItem('token');
    return token;
}

export function setRefreshToken(token: string) {
    localStorage.setItem('refresh', token);
}

export function getRefreshToken(): string | null {
    let token = localStorage.getItem('refresh');
    return token;
}

export function clearStorage() {
    localStorage.clear();
}