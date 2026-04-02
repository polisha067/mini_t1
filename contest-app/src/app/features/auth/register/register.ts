import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService, RegisterRequest } from '../../../shared/services/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  userData: RegisterRequest = {
    username: '',
    email: '',
    password: '',
    role: 'participant'
  };
  confirmPassword: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;
  roles = [
    { value: 'participant', label: 'Участник' },
    { value: 'expert', label: 'Эксперт' },
    { value: 'admin', label: 'Администратор' }
  ];

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    if (!this.userData.username || !this.userData.email || !this.userData.password) {
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
      next: (response) => {
        this.isLoading = false;
        this.router.navigate([response.redirect_url || '/home']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.message || 'Ошибка регистрации. Попробуйте снова.';
        console.error('Registration error:', err);
      }
    });
  }
}
