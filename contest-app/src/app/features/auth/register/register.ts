import { ChangeDetectorRef, Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { finalize, timeout } from 'rxjs/operators';
import { TimeoutError } from 'rxjs';
import { AuthService, RegisterRequest } from '../../../shared/services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  userData: RegisterRequest = {
    username: '',
    email: '',
    password: '',
    role: '',
  };
  confirmPassword = '';
  errorMessage = '';
  isLoading = false;
  showPassword = false;
  showConfirmPassword = false;
  isRoleDropdownOpen = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  selectRole(role: 'expert' | 'organizer'): void {
    this.userData.role = role;
    this.isRoleDropdownOpen = false;
  }

  onSubmit(): void {
    if (
      !this.userData.username ||
      !this.userData.email ||
      !this.userData.password ||
      !this.userData.role
    ) {
      this.errorMessage = 'Пожалуйста, заполните все обязательные поля';
      return;
    }

    if (this.userData.password !== this.confirmPassword) {
      this.errorMessage = 'Пароли не совпадают';
      return;
    }

    if (this.userData.password.length < 6) {
      this.errorMessage = 'Пароль должен содержать не менее 6 символов';
      return;
    }

    if (this.isLoading) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService
      .registerAndLogin(this.userData)
      .pipe(
        timeout(32_000),
        finalize(() => {
          this.isLoading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (response) => {
          const user = response?.user;
          if (!user?.role) {
            this.errorMessage =
              'Регистрация прошла, но вход не завершился. Войдите вручную.';
            this.cdr.detectChanges();
            return;
          }
          this.navigateByRole(user.role);
        },
        error: (err) => {
          this.errorMessage = this.getRegisterErrorMessage(err);
          this.cdr.detectChanges();
        },
      });
  }

  goHome(): void {
    this.router.navigate(['/']);
  }

  private navigateByRole(role: string): void {
    if (role === 'organizer') {
      this.router.navigate(['/account/organizer']);
    } else if (role === 'expert') {
      this.router.navigate(['/account/expert']);
    } else {
      this.router.navigate(['/']);
    }
  }

  private getRegisterErrorMessage(err: unknown): string {
    if (
      err instanceof TimeoutError ||
      (typeof err === 'object' &&
        err !== null &&
        (err as { name?: string }).name === 'TimeoutError')
    ) {
      return 'Сервер не ответил вовремя. Проверьте, что backend запущен (http://localhost:5000).';
    }

    const httpErr = err as HttpErrorResponse;

    if (httpErr.status === 0) {
      return 'Нет соединения с сервером. Проверьте, что backend запущен.';
    }

    if (httpErr.status === 422) {
      return (
        httpErr.error?.error?.message ||
        'Проверьте корректность заполненных данных (имя от 3 символов, пароль от 6).'
      );
    }

    if (httpErr.status === 409) {
      return (
        httpErr.error?.error?.message ||
        httpErr.error?.message ||
        httpErr.error?.detail ||
        'Пользователь с таким email или именем уже существует.'
      );
    }

    if (httpErr.status === 401) {
      return 'Регистрация выполнена, но автоматический вход не удался. Попробуйте войти вручную.';
    }

    const backendMessage = httpErr.error?.error?.message || httpErr.error?.message;
    if (backendMessage) {
      return backendMessage;
    }

    if (httpErr.status >= 500) {
      return 'Ошибка сервера. Попробуйте снова через минуту.';
    }

    return 'Ошибка регистрации. Попробуйте снова.';
  }
}
