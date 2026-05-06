import { HttpInterceptorFn, HttpRequest, HttpHandlerFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../../shared/services/auth.service';
import { catchError, switchMap, throwError } from 'rxjs';

/**
 * Надежный интерцептор с поддержкой Refresh Token
 */
export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
) => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  let authReq = req;
  if (token && !req.url.includes('/api/auth/')) {
    authReq = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    });
  }

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      // Если получили 401 и это не попытка входа/обновления
      if (error.status === 401 && !req.url.includes('/api/auth/')) {
        return authService.refreshToken().pipe(
          switchMap((response) => {
            const newToken = response.access_token;
            const retryReq = req.clone({
              setHeaders: { Authorization: `Bearer ${newToken}` },
            });
            return next(retryReq);
          }),
          catchError((refreshError) => {
            authService.logout();
            return throwError(() => refreshError);
          })
        );
      }
      return throwError(() => error);
    })
  );
};
