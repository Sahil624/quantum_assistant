import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../../modules/auth/services/auth.service';
import { switchMap } from 'rxjs';

export const bearerInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);

  return authService.getValidAccessToken(req).pipe(switchMap((token) => {
    if (token != null) {
      // req.headers.set("Authorization", token);
      req = req.clone({
        headers: req.headers.set("Authorization", "Bearer " + token)
      })
    }

    return next(req);
  }))
};
