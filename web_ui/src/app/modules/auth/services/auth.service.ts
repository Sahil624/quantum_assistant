import { HttpClient, HttpErrorResponse, HttpRequest } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { LoginRequest, LoginResponse, RefreshRequest, RefreshResponse } from './auth.interface';
import { loginUrl, refreshUrl } from '../../../helpers/urls';
import { BehaviorSubject, Observable, Subject, tap } from 'rxjs';
import { clearStorage, getAccessToken, getRefreshToken, setAccessToken, setRefreshToken } from '../../../helpers/storage';
import { UnAuthenticatedError } from '../../../helpers/errors';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(
    private http: HttpClient,
    private router:Router
  ) { }

  login(request: LoginRequest) {
    return this.http.post<LoginResponse>(loginUrl, request).pipe(tap(resp => {
      setAccessToken(resp.access);
      setRefreshToken(resp.refresh);
    }));
  }

  getValidAccessToken(req?: HttpRequest<unknown>): Observable<string | null> {
    const obs = new BehaviorSubject<string | null>(null);
    const token = getAccessToken();

    if (!token || req?.url.endsWith(refreshUrl)) {
      obs.next(null);
    } else {
      const claims = JSON.parse(atob(token.split('.')[1]));
      const expiry = claims['exp'];

      if (((Date.now() / 1e3) - 60) >= expiry) {
        const refreshToken = getRefreshToken();
        if (refreshToken == null) {
          obs.next(null)
          return obs.asObservable()
        }
        const req: RefreshRequest = {
          refresh: refreshToken
        };

        this.http.post<RefreshResponse>(refreshUrl, req).subscribe((res) => {
          const accessToken = res.access;

          setAccessToken(accessToken);
          obs.next(accessToken);
        }, (err: HttpErrorResponse) => {
          if (err.status == 401) {
            obs.error(new UnAuthenticatedError());
          }
        })
      } else {
        obs.next(token);
      }
    }

    return obs.asObservable();
  }

  logout() {
    clearStorage();

    this.router.navigateByUrl('/');
  }
}
