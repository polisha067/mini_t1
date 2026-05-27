import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.scss']
})
export class ResetPassword implements OnInit {
  newPassword = '';
  confirmPassword = '';

  showPassword = false;
  showConfirmPassword = false;

  isLoading = false;
  errorMessage = '';

  token: string | null = null;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.token = this.route.snapshot.queryParamMap.get('token');
    if (!this.token) {
      this.errorMessage = 'Токен не найден. Воспользуйтесь ссылкой из письма.';
    }
  }

  onSubmit() {
    if (!this.token) {
      this.errorMessage = 'Токен не найден. Воспользуйтесь ссылкой из письма.';
      return;
    }

    if (!this.newPassword || !this.confirmPassword) {
      this.errorMessage = 'пожалуйста, заполните все поля';
      return;
    }

    if (this.newPassword !== this.confirmPassword) {
      this.errorMessage = 'пароли не совпадают';
      return;
    }

    this.errorMessage = '';
    this.isLoading = true;

    this.authService.resetPassword({ token: this.token, new_password: this.newPassword }).subscribe({
      next: () => {
        this.isLoading = false;
        alert('Пароль успешно изменён! Вы можете войти с новым паролем.');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.message || 'Произошла ошибка при сбросе пароля';
      }
    });
  }

  goHome() {
    this.router.navigate(['/login']);
  }
}