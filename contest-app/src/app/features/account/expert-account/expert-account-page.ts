import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';
import { ContestService } from '../../../core/contest.service';
import { User, Contest } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-expert-account-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './expert-account-page.html',
  styleUrl: './expert-account-page.scss',
})
export class ExpertAccountPage implements OnInit {
  user: User | null = null;
  expertContests: Contest[] = [];
  isLoadingContests = false;
  contestsError = '';

  constructor(
    private router: Router,
    private authService: AuthService,
    private contestService: ContestService
  ) {
    this.user = this.authService.getCurrentUser();
  }

  ngOnInit(): void {
    this.loadExpertContests();
  }

  goHome(): void {
    this.router.navigate(['/']);
  }

  logout(): void {
    this.authService.logout();
  }

  goToContest(contestId: number): void {
    this.router.navigate(['/contest', contestId]);
  }

  private loadExpertContests(): void {
    this.isLoadingContests = true;
    this.contestsError = '';

    this.contestService.getMyExpertContests().subscribe({
      next: (response) => {
        const contests =
          (response['contests'] as Contest[]) ||
          (response['assigned_contests'] as Contest[]) ||
          [];
        this.expertContests = contests;
        this.isLoadingContests = false;
      },
      error: () => {
        this.isLoadingContests = false;
        this.contestsError = 'Не удалось загрузить конкурсы эксперта.';
      }
    });
  }
}
