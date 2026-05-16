import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ContestService } from '../../../core/contest.service';
import { TeamService } from '../../../core/team.service';
import { RankingService } from '../../../core/ranking.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Contest, Team, RankingEntry } from '../../../shared/models/contest.model';
import { catchError, finalize, switchMap, timeout } from 'rxjs/operators';
import { of, TimeoutError } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';

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
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      
      if (id) {
        this.contestId = +id;
        console.log('ID конкурса успешно получен после перезагрузки:', this.contestId);
        this.loadData();
      } else {
        console.warn('ID конкурса не найден в URL');
        this.router.navigate(['/']);
      }
    });
  }

  loadData(): void {
    this.isLoading = true;
    this.error = null;

    this.contestService
      .getById(this.contestId)
      .pipe(
        timeout(20_000),
        switchMap((response: any) => {
          this.contest =
            response?.contest || response?.data || (response?.id ? response : null);
          if (!this.contest) {
            this.error = 'Конкурс не найден';
            return of(null);
          }
          return this.rankingService.getRanking(this.contestId, 1, 100).pipe(
            timeout(20_000),
            catchError(() => {
              return this.teamService.getList(this.contestId, 1, 100).pipe(
                timeout(20_000),
                catchError(() => {
                  this.error = 'Не удалось загрузить таблицу и список команд';
                  return of(null);
                })
              );
            })
          );
        }),
        finalize(() => {
          this.isLoading = false;
          this.cdr.detectChanges(); // Твой ручной запуск проверки изменений, чтобы верстка точно обновилась
        })
      )
      .subscribe({
        next: (response: any) => {
          if (response === null) {
            this.cdr.detectChanges();
            return;
          }
          if (response?.ranking !== undefined) {
            const data = response?.ranking || response?.data || response;
            this.ranking = Array.isArray(data) ? data : [];
            this.cdr.detectChanges();
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
          this.cdr.detectChanges();
        },
        error: (err: unknown) => {
          console.error('API Error:', err);
          const isTimeout =
            err instanceof TimeoutError ||
            (typeof err === 'object' &&
              err !== null &&
              (err as { name?: string }).name === 'TimeoutError');
          if (isTimeout) {
            this.error =
              'Сервер не ответил вовремя. Убедитесь, что API запущен (часто http://localhost:5000) и что вы открываете приложение с того же хоста, куда настроен proxy в ng serve.';
          } else if (!this.error) {
            this.error = 'Ошибка при получении данных конкурса';
          }
          this.cdr.detectChanges();
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
      },
    });
  }
}