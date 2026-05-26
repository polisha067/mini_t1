import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { catchError, finalize, timeout } from 'rxjs/operators';
import { of, TimeoutError } from 'rxjs';
import { RankingService } from '../../../core/ranking.service';
import { ContestService } from '../../../core/contest.service';
import { GradeService } from '../../../core/grade.service';
import { AuthService } from '../../../shared/services/auth.service';
import { TeamCriterionScore, Contest, Grade } from '../../../shared/models/contest.model';

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
  contest: Contest | null = null;
  contestName: string | null = null;
  teamName: string | null = null;
  totalScore = 0;
  criteriaScores: TeamCriterionScore[] = [];
  gradesByCriterion: Record<number, Grade[]> = {};
  expertsMap: Record<number, string> = {};
  isLoading = true;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private rankingService: RankingService,
    private contestService: ContestService,
    private gradeService: GradeService,
    private authService: AuthService,
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
        this.contest =
          (contestRes as { contest?: Contest })?.contest ||
          (contestRes as { data?: Contest })?.data ||
          null;
        this.contestName = this.contest?.name ?? null;
        this.cdr.detectChanges();
      });

    this.contestService
      .getContestExperts(this.contestId)
      .pipe(
        timeout(20_000),
        catchError(() => of({ experts: [] }))
      )
      .subscribe((res: any) => {
        const expertsList = res?.experts || res?.data || [];
        this.expertsMap = {};
        expertsList.forEach((e: any) => {
          this.expertsMap[e.id] = e.username;
        });
        this.cdr.detectChanges();
      });

    this.gradeService
      .getTeamGrades(this.teamId, 1, 100)
      .pipe(
        timeout(20_000),
        catchError(() => of({ grades: [] as Grade[] }))
      )
      .subscribe((res: any) => {
        const gradesList = res?.grades || res?.data || [];
        this.gradesByCriterion = {};
        gradesList.forEach((g: Grade) => {
          if (!this.gradesByCriterion[g.criterion_id]) {
            this.gradesByCriterion[g.criterion_id] = [];
          }
          this.gradesByCriterion[g.criterion_id].push(g);
        });
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

  isExpert(): boolean {
    return this.authService.isExpert();
  }

  goToEvaluation(): void {
    this.router.navigate(['/evaluation'], { queryParams: { contestId: this.contestId, teamId: this.teamId } });
  }

  getExpertUsername(grade: Grade): string {
    return grade.expert_username || this.expertsMap[grade.expert_id] || `Эксперт #${grade.expert_id}`;
  }

  formatScore(score: number | null): string {
    if (score === null || score === undefined) {
      return '—';
    }
    return Number.isInteger(score) ? String(score) : score.toFixed(2);
  }
}
