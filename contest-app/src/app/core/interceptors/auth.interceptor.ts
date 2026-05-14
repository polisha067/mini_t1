import {
  HttpInterceptorFn,
  HttpRequest,
  HttpHandlerFn,
  HttpErrorResponse,
  HttpEvent,
} from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../../shared/services/auth.service';
import {
  Observable,
  catchError,
  finalize,
  of,
  share,
  switchMap,
  take,
  throwError,
} from 'rxjs';

/**
 * Интерцептор с защитой от Race Condition при обновлении токена.
 * Несколько параллельных 401 делят один запрос refresh через share(),
 * чтобы не зависнуть в ожидании BehaviorSubject при ошибке refresh.
 */

let refreshInFlight$: Observable<string> | null = null;

export const authInterceptor: HttpInterceptorFn = (
  req: HttpRequest<unknown>,
  next: HttpHandlerFn
): Observable<HttpEvent<unknown>> => {
  const authService = inject(AuthService);
  const token = authService.getToken();

  let authReq = req;
  if (token && !req.url.includes('/api/auth/')) {
    authReq = addToken(req, token);
  }

  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !req.url.includes('/api/auth/')) {
        return handle401(req, next, authService);
      }
      return throwError(() => error);
    })
  );
};

function addToken(req: HttpRequest<unknown>, token: string): HttpRequest<unknown> {
  return req.clone({ setHeaders: { Authorization: `Bearer ${token}` } });
}

function handle401(
  req: HttpRequest<unknown>,
  next: HttpHandlerFn,
  authService: AuthService
): Observable<HttpEvent<unknown>> {
  if (!refreshInFlight$) {
    refreshInFlight$ = authService.refreshToken().pipe(
      switchMap((response) => {
        const newToken = response.access_token;
        if (!newToken) {
          authService.logout();
          return throwError(() => new Error('No access token in refresh response'));
        }
        return of(newToken);
      }),
      catchError((err) => {
        authService.logout();
        return throwError(() => err);
      }),
      finalize(() => {
        refreshInFlight$ = null;
      }),
      share()
    );
  }

  return refreshInFlight$.pipe(
    take(1),
    switchMap((newToken) => next(addToken(req, newToken)))
  );
}
