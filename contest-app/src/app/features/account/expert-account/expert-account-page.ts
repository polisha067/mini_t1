import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';
import { ContestService } from '../../../core/contest.service';
import { User, Contest } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-expert-account-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './expert-account-page.html',
  styleUrl: './expert-account-page.scss',
})
export class ExpertAccountPage implements OnInit {
  user: User | null = null;
  expertContests: Contest[] = [];
  isLoadingContests = false;
  contestsError = '';

  joinContestId: number | null = null;
  joinAccessKey = '';
  joinError = '';
  joinSuccess = '';
  isJoining = false;

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

  goHome(): void { this.router.navigate(['/']); }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  goToContest(contestId: number): void {
    this.router.navigate(['/contest', contestId]);
  }

  joinContest(): void {
    if (!this.joinContestId || !this.joinAccessKey.trim()) {
      this.joinError = 'Заполните ID конкурса и ключ доступа';
      return;
    }

    this.isJoining = true;
    this.joinError = '';
    this.joinSuccess = '';

    this.contestService.joinContestByAccessKey(this.joinContestId, this.joinAccessKey).subscribe({
      next: (response: any) => {
        this.joinSuccess = response.message || 'Вы успешно присоединились к конкурсу!';
        this.joinContestId = null;
        this.joinAccessKey = '';
        this.isJoining = false;
        this.loadExpertContests();
      },
      error: (err: any) => {
        this.joinError = err.error?.error?.message || 'Ошибка: неверный ключ или ID конкурса';
        this.isJoining = false;
      }
    });
  }

  private loadExpertContests(): void {
    this.isLoadingContests = true;
    this.contestsError = '';

    this.contestService.getMyExpertContests().subscribe({
      next: (response: any) => {
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