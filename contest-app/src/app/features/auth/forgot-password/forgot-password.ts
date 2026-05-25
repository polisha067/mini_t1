import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './forgot-password.html',
  styleUrl: './forgot-password.scss',
})
export class ForgotPassword {
  email: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (!this.email) {
      this.errorMessage = 'Пожалуйста, введите почту';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.forgotPassword({ email: this.email }).subscribe({
      next: (response) => {
        this.isLoading = false;
        // Переходим на страницу ожидания с email для отображения
        this.router.navigate(['/password-reset-sent'], {
          queryParams: { email: this.email }
        });
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = this.getErrorMessage(err);
        console.error('Forgot password error:', err);
      }
    });
  }

  goHome(): void {
    this.router.navigate(['/']);
  }

  private getErrorMessage(err: HttpErrorResponse): string {
    if (err.status === 0) {
      return 'Нет соединения с сервером. Проверьте, что backend запущен.';
    }

    const backendMessage = err.error?.error?.message || err.error?.message;
    if (backendMessage) {
      return backendMessage;
    }

    if (err.status >= 500) {
      return 'Ошибка сервера. Попробуйте снова через минуту.';
    }

    return 'Ошибка. Попробуйте снова.';
  }
}