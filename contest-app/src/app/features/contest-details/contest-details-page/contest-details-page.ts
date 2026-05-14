import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ContestService } from '../../../core/contest.service';
import { TeamService } from '../../../core/team.service';
import { RankingService } from '../../../core/ranking.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Contest, Team, RankingEntry } from '../../../shared/models/contest.model';
import { finalize } from 'rxjs/operators';

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
    console.log('--- МЕТОД loadData ЗАПУЩЕН ---');
    this.isLoading = true;
    this.error = null;

    this.contestService.getById(this.contestId)
      .pipe(finalize(() => {
        if (this.error) this.isLoading = false;
      }))
      .subscribe({
        next: (response: any) => {
          this.contest = response?.contest || response?.data || (response?.id ? response : null);
          this.loadTeamsAndRanking();
        },
        error: (err: any) => {
          console.error('API Error:', err);
          this.error = 'Ошибка при получении данных конкурса';
          this.isLoading = false;
        },
      });
  }

  loadTeamsAndRanking(): void {
    this.rankingService.getRanking(this.contestId, 1, 100)
      .pipe(finalize(() => this.isLoading = false))
      .subscribe({
        next: (response: any) => {
          const data = response?.ranking || response?.data || response;
          this.ranking = Array.isArray(data) ? data : [];
        },
        error: (err: any) => {
          console.warn('Ranking failed, loading teams instead');
          this.teamService.getList(this.contestId, 1, 100).subscribe({
            next: (resp: any) => {
              const data = resp?.teams || resp?.data || resp;
              this.teams = Array.isArray(data) ? data : [];
            }
          });
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