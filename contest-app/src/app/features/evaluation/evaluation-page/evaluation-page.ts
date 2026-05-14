import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError, finalize } from 'rxjs/operators';
import { TeamService } from '../../../core/team.service';
import { CriterionService } from '../../../core/criterion.service';
import { GradeService } from '../../../core/grade.service';
import { ContestService } from '../../../core/contest.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Team, Criterion, Grade } from '../../../shared/models/contest.model';

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
  contestTitle: string | null = null;
  teams: Team[] = [];
  criteria: Criterion[] = [];
  isLoading = true;
  error: string | null = null;

  selectedTeam: Team | null = null;

  grades: Record<number, { value: number | null; comment: string }> = {};

  existingGrades: Record<number, Grade> = {};

  isSubmitting = false;
  successMessage: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private teamService: TeamService,
    private criterionService: CriterionService,
    private gradeService: GradeService,
    private contestService: ContestService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.queryParamMap.get('contestId');
    this.contestId = idParam ? +idParam : null;
    if (!this.contestId || !Number.isFinite(this.contestId)) {
      this.isLoading = false;
      this.error =
        'Не указан конкурс. Откройте оценивание из личного кабинета эксперта (список конкурсов).';
      return;
    }
    this.loadData();
  }

  loadData(): void {
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
      .pipe(finalize(() => (this.isLoading = false)))
      .subscribe({
        next: (bundle) => {
          const meta = bundle.meta as {
            contest?: { name?: string };
            data?: { name?: string };
          } | null;
          const c = meta?.contest || meta?.data;
          this.contestTitle = c?.name ?? null;

          const tr = bundle.teams as { teams?: Team[] };
          const cr = bundle.criteria as { criteria?: Criterion[] };
          this.teams = Array.isArray(tr?.teams) ? tr.teams : [];
          this.criteria = Array.isArray(cr?.criteria) ? cr.criteria : [];

          this.initGrades();

          if (!this.error && this.teams.length === 0 && this.criteria.length === 0) {
            this.error =
              'Нет команд или критериев для оценивания. Если вы только что присоединились — обновите страницу.';
          }
        },
        error: (err) => {
          if (!this.error) {
            this.error = flaskErrorMessage(err);
          }
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
    this.successMessage = null;
    this.error = null;
    this.initGrades();

    this.gradeService.getTeamGrades(team.id, 1, 100).subscribe({
      next: (response) => {
        const grades = (response as { grades?: Grade[] }).grades ?? [];
        this.existingGrades = {};
        grades.forEach((g) => {
          this.existingGrades[g.criterion_id] = g;
          this.grades[g.criterion_id] = {
            value: g.value,
            comment: g.comment || '',
          };
        });
      },
      error: () => {
        this.existingGrades = {};
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

    this.isSubmitting = true;
    this.error = null;
    this.successMessage = null;

    const entries = Object.entries(this.grades).filter(
      ([_, g]) => g.value !== null && g.value !== undefined
    );

    if (entries.length === 0) {
      this.isSubmitting = false;
      this.error = 'Выставьте хотя бы одну оценку';
      return;
    }

    let completed = 0;
    let hasError = false;

    const saveDone = () => {
      completed++;
      if (completed === entries.length && !hasError) {
        this.isSubmitting = false;
        this.successMessage = 'Оценки успешно сохранены';
        this.initGrades();
      }
    };

    const saveErr = (err: unknown) => {
      hasError = true;
      completed++;
      this.error = flaskErrorMessage(err) || 'Ошибка при сохранении';
      this.isSubmitting = false;
    };

    entries.forEach(([criterionIdStr, gradeData]) => {
      const criterionId = +criterionIdStr;
      const existingGrade = this.existingGrades[criterionId];

      if (existingGrade) {
        this.gradeService
          .update(existingGrade.id, {
            value: gradeData.value!,
            comment: gradeData.comment || undefined,
          })
          .subscribe({ next: saveDone, error: saveErr });
      } else {
        this.gradeService
          .create({
            team_id: this.selectedTeam!.id,
            criterion_id: criterionId,
            value: gradeData.value!,
            comment: gradeData.comment || undefined,
          })
          .subscribe({ next: saveDone, error: saveErr });
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/account/expert']);
  }

  canSubmit(): boolean {
    return Object.values(this.grades).some(
      (g) => g.value !== null && g.value !== undefined
    );
  }

  getMaxScore(criterionId: number): number {
    const criterion = this.criteria.find((c) => c.id === criterionId);
    return criterion?.max_score ?? 10;
  }
}
