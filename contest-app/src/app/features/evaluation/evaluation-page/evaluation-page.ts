import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TeamService } from '../../../core/team.service';
import { CriterionService } from '../../../core/criterion.service';
import { GradeService } from '../../../core/grade.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Team, Criterion, Grade } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-evaluation-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './evaluation-page.html',
  styleUrl: './evaluation-page.scss',
})
export class EvaluationPage implements OnInit {
  teams: Team[] = [];
  criteria: Criterion[] = [];
  isLoading = true;
  error: string | null = null;

  // Выбранная команда
  selectedTeam: Team | null = null;

  // Оценки: criterionId -> { value, comment }
  grades: Record<number, { value: number | null; comment: string }> = {};

  // Уже выставленные оценки (для редактирования)
  existingGrades: Record<number, Grade> = {};

  isSubmitting = false;
  successMessage: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private teamService: TeamService,
    private criterionService: CriterionService,
    private gradeService: GradeService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    const idParam = this.route.snapshot.queryParamMap.get('contestId');
    const contestId = idParam ? +idParam : 1; 

    // Загружаем команды и критерии параллельно
    this.teamService.getList(contestId, 1, 100).subscribe({
      next: (response) => {
        this.teams = response['teams'] as Team[];
        this.loadCriteria(contestId);
      },
      error: () => {
        this.teams = [];
        this.loadCriteria(contestId);
      },
    });
  }

  loadCriteria(contestId: number): void {
    this.criterionService.getList(contestId, 1, 100).subscribe({
      next: (response) => {
        this.criteria = response['criteria'] as Criterion[];
        this.initGrades();
        this.isLoading = false;
      },
      error: () => {
        this.criteria = [];
        this.isLoading = false;
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

    // Загружаем уже выставленные оценки для этой команды
    this.gradeService.getTeamGrades(team.id, 1, 100).subscribe({
      next: (response) => {
        const grades = response['grades'] as Grade[];
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

    const currentUser = this.authService.getCurrentUser();
    if (!currentUser) {
      this.error = 'Необходимо авторизоваться';
      return;
    }

    this.isSubmitting = true;
    this.error = null;
    this.successMessage = null;

    // Собираем критерии, у которых есть оценка
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

    entries.forEach(([criterionIdStr, gradeData]) => {
      const criterionId = +criterionIdStr;
      const existingGrade = this.existingGrades[criterionId];

      if (existingGrade) {
        // Обновляем существующую оценку
        this.gradeService.update(existingGrade.id, {
          value: gradeData.value!,
          comment: gradeData.comment || undefined,
        }).subscribe({
          next: () => {
            completed++;
            if (completed === entries.length && !hasError) {
              this.isSubmitting = false;
              this.successMessage = 'Оценки успешно сохранены';
              this.initGrades();
            }
          },
          error: (err) => {
            hasError = true;
            completed++;
            this.error = err.error?.error?.message || 'Ошибка при сохранении';
            this.isSubmitting = false;
          },
        });
      } else {
        // Создаём новую оценку
        this.gradeService.create({
          team_id: this.selectedTeam!.id,
          criterion_id: criterionId,
          value: gradeData.value!,
          comment: gradeData.comment || undefined,
        }).subscribe({
          next: () => {
            completed++;
            if (completed === entries.length && !hasError) {
              this.isSubmitting = false;
              this.successMessage = 'Оценки успешно сохранены';
              this.initGrades();
            }
          },
          error: (err) => {
            hasError = true;
            completed++;
            this.error = err.error?.error?.message || 'Ошибка при сохранении';
            this.isSubmitting = false;
          },
        });
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/']);
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
