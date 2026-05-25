import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router'; // Импортируем роутер для кнопки назад

@Component({
  selector: 'app-reset-password',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.scss']
})
export class ResetPassword {
  newPassword = '';
  confirmPassword = '';

  showPassword = false;
  showConfirmPassword = false;

  isLoading = false;
  errorMessage = '';

  constructor(private router: Router) {}

  onSubmit() {
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

    console.log('Отправка на бэкенд нового пароля:', this.newPassword);
    
    setTimeout(() => {
      this.isLoading = false;
    }, 2000);
  }

  goHome() {
    this.router.navigate(['/login']);
  }
}