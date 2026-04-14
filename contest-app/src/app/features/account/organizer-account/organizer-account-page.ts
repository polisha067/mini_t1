import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';
import { ContestService } from '../../../core/contest.service';
import { User, Contest } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-organizer-account-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './organizer-account-page.html',
  styleUrl: './organizer-account-page.scss',
})
export class OrganizerAccountPage implements OnInit {
  user: User | null = null;
  createdContests: Contest[] = [];
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
    this.loadCreatedContests();
  }

  goHome(): void {
    this.router.navigate(['/']);
  }

  logout(): void {
    this.authService.logout();
  }

  goToCreateContest(): void {
    this.router.navigate(['/create-contest']);
  }

  goToContest(contestId: number): void {
    this.router.navigate(['/contest', contestId]);
  }

  private loadCreatedContests(): void {
    if (!this.user) {
      return;
    }

    this.isLoadingContests = true;
    this.contestsError = '';

    this.contestService.getList(1, 100, this.user.id).subscribe({
      next: (response) => {
        this.createdContests = (response['contests'] as Contest[]) || [];
        this.isLoadingContests = false;
      },
      error: () => {
        this.isLoadingContests = false;
        this.contestsError = 'Не удалось загрузить конкурсы организатора.';
      }
    });
  }
}
