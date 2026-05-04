import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { ContestService } from '../../../core/contest.service';
import { TeamService } from '../../../core/team.service';
import { RankingService } from '../../../core/ranking.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Contest, Team, RankingEntry } from '../../../shared/models/contest.model';

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
  accessKey: string | null = null;
  isGeneratingKey = false;

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

    // Загружаем детали конкурса
    this.contestService.getById(this.contestId).subscribe({
      next: (response) => {
        this.contest = response['contest'] as Contest;
        this.loadTeamsAndRanking();
      },
      error: (err) => {
        console.error('Failed to load contest:', err);
        this.error = 'Не удалось загрузить данные конкурса';
        this.isLoading = false;
      },
    });
  }

  loadTeamsAndRanking(): void {
    // Загружаем рейтинг (он уже содержит данные о командах)
    this.rankingService.getRanking(this.contestId, 1, 100).subscribe({
      next: (response) => {
        this.ranking = response['ranking'] as RankingEntry[];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load ranking:', err);
        // Если рейтинг ещё пуст — загружаем просто команды
        this.teamService.getList(this.contestId, 1, 100).subscribe({
          next: (resp) => {
            this.teams = resp['teams'] as Team[];
            this.isLoading = false;
          },
          error: () => {
            this.teams = [];
            this.isLoading = false;
          },
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
    this.router.navigate(['/evaluation']);
  }

  goToParticipants(): void {
    this.router.navigate(['/contests', this.contestId, 'participants']);
  }

  generateKey(): void {
    if (!this.contestId) return;
    this.isGeneratingKey = true;
    
    this.contestService.generateAccessKey(this.contestId).subscribe({
      next: (res) => {
        this.accessKey = res.access_key;
        if (this.contest) {
          this.contest.access_key = res.access_key;
        }
        this.isGeneratingKey = false;
      },
      error: (err) => {
        console.error('Generate key error:', err);
        this.isGeneratingKey = false;
      }
    });
  }

  copyKey(): void {
    if (this.accessKey) {
      navigator.clipboard.writeText(this.accessKey);
    }
  }
}