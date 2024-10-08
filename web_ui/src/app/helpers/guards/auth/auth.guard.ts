import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../../../modules/auth/services/auth.service';
import { map } from 'rxjs';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  return authService.getValidAccessToken().pipe(map((token) => {
    if (token == null) {
      return true;
    } else {
      router.navigateByUrl('/dashboard');
      return false;
    }
  }));
};
