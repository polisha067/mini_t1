import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { catchError, finalize, timeout } from 'rxjs/operators';
import { of, TimeoutError } from 'rxjs';
import { RankingService } from '../../../core/ranking.service';
import { ContestService } from '../../../core/contest.service';
import { TeamCriterionScore } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-team-scores-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './team-scores-page.html',
  styleUrl: './team-scores-page.scss',
})
export class TeamScoresPage implements OnInit {
  contestId!: number;
  teamId!: number;
  contestName: string | null = null;
  teamName: string | null = null;
  totalScore = 0;
  criteriaScores: TeamCriterionScore[] = [];
  isLoading = true;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rankingService: RankingService,
    private contestService: ContestService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe((params) => {
      const contestId = params.get('contestId');
      const teamId = params.get('teamId');
      if (!contestId || !teamId) {
        this.router.navigate(['/']);
        return;
      }
      this.contestId = +contestId;
      this.teamId = +teamId;
      this.loadData();
    });
  }

  loadData(): void {
    this.isLoading = true;
    this.error = null;

    this.contestService
      .getById(this.contestId)
      .pipe(
        timeout(20_000),
        catchError(() => of(null))
      )
      .subscribe((contestRes) => {
        const contest =
          (contestRes as { contest?: { name?: string } })?.contest ||
          (contestRes as { data?: { name?: string } })?.data;
        this.contestName = contest?.name ?? null;
        this.cdr.detectChanges();
      });

    this.rankingService
      .getTeamScores(this.contestId, this.teamId)
      .pipe(
        timeout(20_000),
        finalize(() => {
          this.isLoading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (res) => {
          this.teamName = res.team_name;
          this.totalScore = res.total_score;
          this.criteriaScores = res.criteria_scores ?? [];
          this.cdr.detectChanges();
        },
        error: (err: unknown) => {
          const isTimeout =
            err instanceof TimeoutError ||
            (typeof err === 'object' &&
              err !== null &&
              (err as { name?: string }).name === 'TimeoutError');
          this.error = isTimeout
            ? 'Сервер не ответил вовремя'
            : 'Не удалось загрузить оценки команды';
          this.cdr.detectChanges();
        },
      });
  }

  goBack(): void {
    this.router.navigate(['/contests', this.contestId]);
  }

  formatScore(score: number | null): string {
    if (score === null || score === undefined) {
      return '—';
    }
    return Number.isInteger(score) ? String(score) : score.toFixed(2);
  }
}
