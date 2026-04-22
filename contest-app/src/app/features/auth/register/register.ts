import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService, RegisterRequest } from '../../../shared/services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  imports: [CommonModule, FormsModule],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  userData: RegisterRequest = {
    username: '',
    email: '',
    password: '',
    role: ''
  };
  confirmPassword: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;
  showPassword: boolean = false;
  showConfirmPassword: boolean = false;
  isRoleDropdownOpen: boolean = false;
  roles = [
    { value: 'expert', label: 'Эксперт' },
    { value: 'organizer', label: 'Организатор' }
  ];

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  selectRole(role: 'expert' | 'organizer'): void {
  this.userData.role = role;
  this.isRoleDropdownOpen = false;
  }

  onSubmit(): void {
    if (!this.userData.username || !this.userData.email || !this.userData.password || !this.userData.role) {
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

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.register(this.userData).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = this.getRegisterErrorMessage(err);
        console.error('Registration error:', err);
      }
    });
  }

  goHome(): void {
    this.router.navigate(['/']);
  }

  private getRegisterErrorMessage(err: HttpErrorResponse): string {
    if (err.status === 0) {
      return 'Нет соединения с сервером. Проверьте, что backend запущен.';
    }

    if (err.status === 409) {
      return 'Пользователь с таким email уже существует.';
    }

    if (err.status === 422) {
      return 'Проверьте корректность заполненных данных.';
    }

    const backendMessage = err.error?.error?.message || err.error?.message;
    if (backendMessage) {
      return backendMessage;
    }

    if (err.status >= 500) {
      return 'Ошибка сервера. Попробуйте снова через минуту.';
    }

    return 'Ошибка регистрации. Попробуйте снова.';
  }
}
