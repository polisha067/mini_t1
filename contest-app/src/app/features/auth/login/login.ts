import { ChangeDetectorRef, Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { finalize, timeout } from 'rxjs/operators';
import { TimeoutError } from 'rxjs';
import { AuthService, LoginRequest } from '../../../shared/services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  credentials: LoginRequest = {
    email: '',
    password: '',
  };

  errorMessage = '';
  isLoading = false;
  showPassword = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  onSubmit(): void {
    if (!this.credentials.email || !this.credentials.password) {
      this.errorMessage = 'Пожалуйста, заполните все поля';
      return;
    }

    if (this.isLoading) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService
      .login(this.credentials)
      .pipe(
        timeout(16_000),
        finalize(() => {
          this.isLoading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (response) => {
          const user = response?.user;
          if (!user?.role) {
            this.errorMessage = 'Сервер вернул некорректный ответ. Попробуйте снова.';
            this.cdr.detectChanges();
            return;
          }
          this.navigateByRole(user.role);
        },
        error: (err) => {
          this.errorMessage = this.getLoginErrorMessage(err);
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

  private getLoginErrorMessage(err: unknown): string {
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

    if (httpErr.status === 401) {
      return 'Неверный email или пароль.';
    }

    const backendMessage = httpErr.error?.error?.message || httpErr.error?.message;
    if (backendMessage) {
      return backendMessage;
    }

    if (httpErr.status >= 500) {
      return 'Ошибка сервера. Попробуйте снова через минуту.';
    }

    return 'Ошибка входа. Проверьте данные и попробуйте снова.';
  }
}
