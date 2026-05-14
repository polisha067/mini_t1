import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ContestService } from '../../../core/contest.service';
import { TeamService } from '../../../core/team.service';
import { RankingService } from '../../../core/ranking.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Contest, Team, RankingEntry } from '../../../shared/models/contest.model';
import { catchError, finalize, timeout } from 'rxjs/operators';
import { of } from 'rxjs';

@Component({
  selector: 'app-contest-details-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './contest-details-page.html',
  styleUrl: './contest-details-page.scss',
})
export class ContestDetailsPage implements OnInit {
  contestId!: number;
  contest: Contest | null = null;
  teams: Team[] = [];
  ranking: RankingEntry[] = [];
  isLoading = true;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private contestService: ContestService,
    private teamService: TeamService,
    private rankingService: RankingService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam) {
      this.router.navigate(['/']);
      return;
    }
    this.contestId = +idParam;
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.error = null;

    this.contestService
      .getById(this.contestId)
      .pipe(timeout(30_000))
      .subscribe({
        next: (response: any) => {
          this.contest = response?.contest || response?.data || (response?.id ? response : null);
          if (this.contest) {
            this.loadTeamsAndRanking();
          } else {
            this.error = 'Конкурс не найден';
            this.isLoading = false;
          }
        },
        error: (err: any) => {
          console.error('API Error:', err);
          this.error =
            err?.name === 'TimeoutError'
              ? 'Сервер не ответил вовремя. Проверьте, что API запущен (например http://localhost:5000) и proxy в Angular указывает на него.'
              : 'Ошибка при получении данных конкурса';
          this.isLoading = false;
        },
      });
  }

  loadTeamsAndRanking(): void {
    this.rankingService
      .getRanking(this.contestId, 1, 100)
      .pipe(
        timeout(30_000),
        catchError((err) => {
          console.warn('Ranking failed or timed out, loading teams instead', err);
          return this.teamService.getList(this.contestId, 1, 100).pipe(
            catchError((teamErr) => {
              console.error('Teams also failed:', teamErr);
              this.error = 'Не удалось загрузить таблицу и список команд';
              return of(null);
            })
          );
        }),
        finalize(() => {
          this.isLoading = false;
        })
      )
      .subscribe({
        next: (response: any) => {
          if (response === null) {
            return;
          }
          if (response?.ranking !== undefined) {
            const data = response?.ranking || response?.data || response;
            this.ranking = Array.isArray(data) ? data : [];
            return;
          }
          const teamData = response?.teams || response?.data || response;
          this.teams = Array.isArray(teamData) ? teamData : [];
          this.ranking = this.teams.map((t, i) => ({
            rank: i + 1,
            team_id: t.id,
            team_name: t.name,
            total_score: 0,
            grades_count: 0,
          }));
        },
      });
  }

  goBack(): void {
    this.router.navigate(['/']);
  }

  getLogoUrl(logoPath: string | null): string {
    if (!logoPath) return 'assets/images/photo.jpg';
    if (logoPath.startsWith('http')) return logoPath;
    return `/${logoPath.replace(/^\/+/, '')}`;
  }

  formatDate(dateStr: string | null): string {
    if (!dateStr) return 'Дата не указана';
    return new Date(dateStr).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  }

  isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }

  isOrganizer(): boolean {
    return this.authService.isOrganizer();
  }

  isExpert(): boolean {
    return this.authService.isExpert();
  }

  goToEvaluation(): void {
    this.router.navigate(['/evaluation'], { queryParams: { contestId: this.contestId } });
  }

  goToParticipants(): void {
    this.router.navigate(['/contests', this.contestId, 'participants']);
  }

  generateAccessKey(): void {
    if (!this.contestId) return;
    this.contestService.generateAccessKey(this.contestId).subscribe({
      next: (response: any) => {
        if (this.contest) {
          this.contest.access_key = response.access_key;
        }
        alert('Ключ доступа успешно создан: ' + response.access_key);
      },
      error: (err: any) => {
        alert('Ошибка при генерации ключа: ' + (err.error?.error?.message || err.message));
      }
    });
  }
}