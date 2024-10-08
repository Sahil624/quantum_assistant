export interface LoginRequest {
    username: string;
    password: string;
}

export interface LoginResponse {
    refresh: string;
    access: string;
}

export interface LoginError {
    detail: string;
}

export interface RefreshRequest {
    refresh: string;
}

export interface RefreshResponse {
    access: string;
}