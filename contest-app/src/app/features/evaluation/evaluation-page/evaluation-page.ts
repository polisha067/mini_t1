import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { HttpErrorResponse } from '@angular/common/http';
import { forkJoin, of, throwError, timeout } from 'rxjs';
import { catchError, finalize, switchMap } from 'rxjs/operators';
import { TeamService } from '../../../core/team.service';
import { CriterionService } from '../../../core/criterion.service';
import { GradeService } from '../../../core/grade.service';
import { ContestService } from '../../../core/contest.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Team, Criterion, Grade, Contest } from '../../../shared/models/contest.model';

function flaskErrorMessage(err: unknown): string | null {
  const e = err as { error?: { error?: { message?: string }; message?: string } };
  return e?.error?.error?.message || e?.error?.message || null;
}

@Component({
  selector: 'app-evaluation-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './evaluation-page.html',
  styleUrl: './evaluation-page.scss',
})
export class EvaluationPage implements OnInit {
  contestId: number | null = null;
  contest: Contest | null = null;
  contestTitle: string | null = null;
  teams: Team[] = [];
  criteria: Criterion[] = [];
  isLoading = true;
  error: string | null = null;

  selectedTeam: Team | null = null;

  grades: Record<number, { value: number | null; comment: string }> = {};

  existingGrades: Record<number, Grade> = {};

  isSubmitting = false;
  showSuccessToast = false;
  private toastHideTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private teamService: TeamService,
    private criterionService: CriterionService,
    private gradeService: GradeService,
    private contestService: ContestService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((params) => {
      const idParam = params.get('contestId');
      this.contestId = idParam ? +idParam : null;

      const teamIdParam = params.get('teamId');
      const autoTeamId = teamIdParam ? +teamIdParam : null;

      if (!this.contestId || !Number.isFinite(this.contestId)) {
        this.isLoading = false;
        this.error =
          'Не указан конкурс. Откройте оценивание из личного кабинета эксперта (список конкурсов).';
        return;
      }
      this.loadDataAndSelectTeam(autoTeamId);
    });
  }

  loadDataAndSelectTeam(autoTeamId: number | null): void {
    if (!this.contestId) {
      return;
    }
    this.isLoading = true;
    this.error = null;

    forkJoin({
      meta: this.contestService.getById(this.contestId).pipe(catchError(() => of(null))),
      teams: this.teamService.getList(this.contestId, 1, 100).pipe(
        catchError((err) => {
          if (!this.error) {
            this.error = flaskErrorMessage(err);
          }
          return of({ teams: [] as Team[] });
        })
      ),
      criteria: this.criterionService.getList(this.contestId, 1, 100).pipe(
        catchError((err) => {
          if (!this.error) {
            this.error = flaskErrorMessage(err);
          }
          return of({ criteria: [] as Criterion[] });
        })
      ),
    })
      .pipe(
        finalize(() => {
          this.isLoading = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: (bundle) => {
          const meta = bundle.meta as {
            contest?: Contest;
            data?: Contest;
          } | null;
          this.contest = meta?.contest || meta?.data || null;
          this.contestTitle = this.contest?.name ?? null;

          const tr = bundle.teams as { teams?: Team[] };
          const cr = bundle.criteria as { criteria?: Criterion[] };
          this.teams = Array.isArray(tr?.teams) ? tr.teams : [];
          this.criteria = Array.isArray(cr?.criteria) ? cr.criteria : [];

          this.initGrades();

          if (autoTeamId) {
            const teamToSelect = this.teams.find((t) => t.id === autoTeamId);
            if (teamToSelect) {
              this.selectTeam(teamToSelect);
            }
          }

          if (!this.error && this.teams.length === 0 && this.criteria.length === 0) {
            this.error =
              'Нет команд или критериев для оценивания. Если вы только что присоединились — обновите страницу.';
          }
          this.cdr.detectChanges();
        },
        error: (err) => {
          if (!this.error) {
            this.error = flaskErrorMessage(err);
          }
          this.cdr.detectChanges();
        },
      });
  }

  initGrades(): void {
    this.grades = {};
    this.criteria.forEach((c) => {
      this.grades[c.id] = { value: null, comment: '' };
    });
  }

  selectTeam(team: Team): void {
    this.selectedTeam = team;
    this.showSuccessToast = false;
    this.error = null;
    this.initGrades();

    this.gradeService.getTeamGrades(team.id, 1, 100).subscribe({
      next: (response) => {
        const currentUser = this.authService.getCurrentUser();
        const expertId = currentUser?.id;
        const grades = ((response as { grades?: Grade[] }).grades ?? []).filter(
          (g) => expertId != null && g.expert_id == expertId
        );
        this.existingGrades = {};
        grades.forEach((g) => {
          this.existingGrades[g.criterion_id] = g;
          this.grades[g.criterion_id] = {
            value: g.value,
            comment: g.comment || '',
          };
        });
        this.cdr.detectChanges();
      },
      error: () => {
        this.existingGrades = {};
        this.cdr.detectChanges();
      },
    });
  }

  submitGrades(): void {
    if (!this.selectedTeam) {
      this.error = 'Выберите команду';
      return;
    }

    if (!this.authService.getCurrentUser()) {
      this.error = 'Необходимо авторизоваться';
      return;
    }

    const entries = Object.entries(this.grades).filter(([_, g]) =>
      this.hasGradeValue(g.value)
    );

    if (entries.length === 0) {
      this.error = 'Выставьте хотя бы одну оценку';
      return;
    }

    this.isSubmitting = true;
    this.error = null;
    this.showSuccessToast = false;

    const teamId = this.selectedTeam.id;
    const requests = entries.map(([criterionIdStr, gradeData]) => {
      const criterionId = +criterionIdStr;
      const payload = {
        value: Number(gradeData.value),
        comment: gradeData.comment?.trim() || undefined,
      };
      return this.saveGradeForCriterion(teamId, criterionId, payload);
    });

    forkJoin(requests)
      .pipe(
        timeout(30_000),
        finalize(() => {
          this.isSubmitting = false;
          this.cdr.detectChanges();
        })
      )
      .subscribe({
        next: () => {
          this.error = null;
          this.reloadTeamGrades();
          this.showGradesSavedToast();
        },
        error: (err) => {
          this.error =
            flaskErrorMessage(err) ||
            (err?.name === 'TimeoutError' ? 'Превышено время ожидания. Попробуйте снова.' : null) ||
            'Ошибка при сохранении';
          this.cdr.detectChanges();
        },
      });
  }

  private saveGradeForCriterion(
    teamId: number,
    criterionId: number,
    payload: { value: number; comment?: string }
  ) {
    const existing = this.existingGrades[criterionId];
    if (existing?.id) {
      return this.gradeService.update(existing.id, payload).pipe(timeout(20_000));
    }

    return this.gradeService
      .create({
        team_id: teamId,
        criterion_id: criterionId,
        value: payload.value,
        comment: payload.comment,
      })
      .pipe(
        timeout(20_000),
        catchError((err: HttpErrorResponse) => {
          if (err.status === 409) {
            return this.gradeService.getTeamGrades(teamId, 1, 100).pipe(
              switchMap((response) => {
                const grades = (response as { grades?: Grade[] }).grades ?? [];
                const found = grades.find((g) => g.criterion_id === criterionId);
                if (!found) {
                  return throwError(() => err);
                }
                this.existingGrades[criterionId] = found;
                return this.gradeService.update(found.id, payload);
              })
            );
          }
          return throwError(() => err);
        })
      );
  }

  private reloadTeamGrades(): void {
    if (!this.selectedTeam) {
      return;
    }
    this.gradeService.getTeamGrades(this.selectedTeam.id, 1, 100).subscribe({
      next: (response) => {
        const currentUser = this.authService.getCurrentUser();
        const expertId = currentUser?.id;
        const grades = ((response as { grades?: Grade[] }).grades ?? []).filter(
          (g) => expertId != null && g.expert_id == expertId
        );
        this.existingGrades = {};
        grades.forEach((g) => {
          this.existingGrades[g.criterion_id] = g;
          if (this.grades[g.criterion_id]) {
            this.grades[g.criterion_id] = {
              value: g.value,
              comment: g.comment || '',
            };
          }
        });
        this.cdr.detectChanges();
      },
    });
  }

  private showGradesSavedToast(): void {
    if (this.toastHideTimer) {
      clearTimeout(this.toastHideTimer);
    }
    this.showSuccessToast = true;
    this.cdr.detectChanges();
    this.toastHideTimer = setTimeout(() => {
      this.showSuccessToast = false;
      this.toastHideTimer = null;
      this.cdr.detectChanges();
    }, 2500);
  }

  goBack(): void {
    this.router.navigate(['/account/expert']);
  }

  canSubmit(): boolean {
    return Object.values(this.grades).some((g) => this.hasGradeValue(g.value));
  }

  private hasGradeValue(value: number | null | undefined): boolean {
    if (value === null || value === undefined || value === ('' as unknown as number)) {
      return false;
    }
    return !Number.isNaN(Number(value));
  }

  getMaxScore(criterionId: number): number {
    const criterion = this.criteria.find((c) => c.id === criterionId);
    return criterion?.max_score ?? 10;
  }
}
