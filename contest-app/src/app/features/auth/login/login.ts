import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService, LoginRequest } from '../../../shared/services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  credentials: LoginRequest = {
    email: '',
    password: ''
  };

  errorMessage: string = '';
  isLoading: boolean = false;

  showPassword: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (!this.credentials.email || !this.credentials.password) {
      this.errorMessage = 'Пожалуйста, заполните все поля';
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.login(this.credentials).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = this.getLoginErrorMessage(err);
        console.error('Login error:', err);
      }
    });
  }

  goHome(): void {
    this.router.navigate(['/']);
  }

  private getLoginErrorMessage(err: HttpErrorResponse): string {
    if (err.status === 0) {
      return 'Нет соединения с сервером. Проверьте, что backend запущен.';
    }

    if (err.status === 401) {
      return 'Неверный email или пароль.';
    }

    const backendMessage = err.error?.error?.message || err.error?.message;
    if (backendMessage) {
      return backendMessage;
    }

    if (err.status >= 500) {
      return 'Ошибка сервера. Попробуйте снова через минуту.';
    }

    return 'Ошибка входа. Проверьте данные и попробуйте снова.';
  }
}