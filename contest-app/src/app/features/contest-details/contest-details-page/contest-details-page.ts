import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ContestService } from '../../../core/contest.service';
import { TeamService } from '../../../core/team.service';
import { RankingService } from '../../../core/ranking.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Contest, Team, RankingEntry } from '../../../shared/models/contest.model';
import { forkJoin, of } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';
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
    this.isLoading = true;

    forkJoin({
      rankingData: this.rankingService.getRanking(this.contestId, 1, 100).pipe(
        catchError(() => of({ ranking: [] }))
      ),
      teamsData: this.teamService.getList(this.contestId, 1, 100).pipe(
        catchError(() => of({ teams: [] }))
      )
    })
    .pipe(finalize(() => {
      this.isLoading = false;
      this.cdr.detectChanges(); 
    }))
    .subscribe({
      next: (result) => {
        this.ranking = result.rankingData?.ranking || [];
        this.teams = result.teamsData?.teams || [];
        
        this.cdr.detectChanges(); 
        console.log('Данные отрисованы на странице');
      }
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