import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';
import { User } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-expert-account-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './expert-account-page.html',
  styleUrl: './expert-account-page.scss',
})
export class ExpertAccountPage {
  user: User | null = null;

  constructor(
    private router: Router,
    private authService: AuthService
  ) {
    this.user = this.authService.getCurrentUser();
  }

  goHome(): void {
    this.router.navigate(['/']);
  }

  logout(): void {
    this.authService.logout();
  }
}
