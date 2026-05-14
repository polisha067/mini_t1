import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../../shared/services/auth.service';
import { ContestService } from '../contest.service';
import { catchError, map, take } from 'rxjs/operators';
import { of } from 'rxjs';

/**
 * Guard: доступ только для авторизованных пользователей
 */
export const authGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  router.navigate(['/login']);
  return false;
};

/**
 * Guard: доступ только для организаторов
 */
export const organizerGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated() && authService.isOrganizer()) {
    return true;
  }

  if (authService.isAuthenticated()) {
    // Авторизован, но не организатор
    router.navigate(['/']);
    return false;
  }

  router.navigate(['/login']);
  return false;
};

/**
 * Guard: доступ только для экспертов
 */
export const expertGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated() && authService.isExpert()) {
    return true;
  }

  if (authService.isAuthenticated()) {
    // Авторизован, но не эксперт
    router.navigate(['/']);
    return false;
  }

  router.navigate(['/login']);
  return false;
};

/** Оценивание: эксперт и contestId из списка «мои конкурсы» (после ввода ключа). */
export const expertEvaluationGuard: CanActivateFn = (route) => {
  const router = inject(Router);
  const contestService = inject(ContestService);

  const raw = route.queryParamMap.get('contestId');
  const contestId = raw ? Number(raw) : NaN;
  if (!Number.isFinite(contestId) || contestId < 1) {
    router.navigate(['/account/expert'], {
      queryParams: { evaluation: 'missing-contest' },
    });
    return false;
  }

  return contestService.getMyExpertContests().pipe(
    take(1),
    map((res) => {
      const contests = res.contests ?? [];
      const ids = contests.map((c) => c.id);
      if (ids.includes(contestId)) {
        return true;
      }
      router.navigate(['/account/expert'], {
        queryParams: {
          evaluation: 'not-assigned',
          contestId: String(contestId),
        },
      });
      return false;
    }),
    catchError(() => {
      router.navigate(['/account/expert'], {
        queryParams: { evaluation: 'load-failed' },
      });
      return of(false);
    })
  );
};

/**
 * Guard: редирект из /account на страницу аккаунта по роли
 */
export const accountRedirectGuard: CanActivateFn = () => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (!authService.isAuthenticated()) {
    router.navigate(['/login']);
    return false;
  }

  if (authService.isOrganizer()) {
    router.navigate(['/account/organizer']);
    return false;
  }

  if (authService.isExpert()) {
    router.navigate(['/account/expert']);
    return false;
  }

  router.navigate(['/']);
  return false;
};
