import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';
import { User } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-organizer-account-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './organizer-account-page.html',
  styleUrl: './organizer-account-page.scss',
})
export class OrganizerAccountPage {
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
