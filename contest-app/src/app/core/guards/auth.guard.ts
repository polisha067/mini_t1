import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../../shared/services/auth.service';

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
