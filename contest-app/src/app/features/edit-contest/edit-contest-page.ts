import { Component, OnInit, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import flatpickr from 'flatpickr';
import { Russian } from 'flatpickr/dist/l10n/ru';
import { ContestService } from '../../../core/contest.service';
import { TeamService } from '../../../core/team.service';
import { CriterionService } from '../../../core/criterion.service';
import { Contest, Team, Criterion } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-edit-contest-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-contest-page.html',
  styleUrl: './edit-contest-page.scss',
})
export class EditContestPage implements OnInit, AfterViewInit {
  @ViewChild('startDateInput') startDateInput!: ElementRef<HTMLInputElement>;
  @ViewChild('endDateInput') endDateInput!: ElementRef<HTMLInputElement>;

  contestId!: number;
  contest: Contest | null = null;

  name = '';
  description = '';
  startDate = '';
  endDate = '';
  logoPath = '';
  selectedFile: File | null = null;

  teams: { id?: number; name: string }[] = [
    { name: '' },
  ];

  criteria: { id?: number; name: string; description: string; max_score: number }[] = [
    { name: '', description: '', max_score: 10 },
  ];

  isLoading = true;
  isSubmitting = false;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private contestService: ContestService,
    private teamService: TeamService,
    private criterionService: CriterionService
  ) {}

  ngOnInit(): void {
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');

      if (id) {
        this.contestId = +id;
        this.loadContestData();
      } else {
        console.warn('ID конкурса не найден в URL');
        this.router.navigate(['/']);
      }
    });
  }

  ngAfterViewInit(): void {
    flatpickr(this.startDateInput.nativeElement, {
      enableTime: true,
      dateFormat: 'Y-m-d\\\\TH:i:S',
      time_24hr: true,
      locale: Russian,
      onChange: (selectedDates) => {
        this.startDate = selectedDates.length ? selectedDates[0].toISOString() : '';
      },
    });

    flatpickr(this.endDateInput.nativeElement, {
      enableTime: true,
      dateFormat: 'Y-m-d\\\\TH:i:S',
      time_24hr: true,
      locale: Russian,
      onChange: (selectedDates) => {
        this.endDate = selectedDates.length ? selectedDates[0].toISOString() : '';
      },
    });
  }

  loadContestData(): void {
    this.isLoading = true;
    this.error = null;

    this.contestService.getById(this.contestId).subscribe({
      next: (response: any) => {
        this.contest = response?.contest || response?.data || (response?.id ? response : null);

        if (!this.contest) {
          this.error = 'Конкурс не найден';
          this.isLoading = false;
          return;
        }

        // Заполняем форму данными конкурса
        this.name = this.contest.name;
        this.description = this.contest.description || '';
        this.startDate = this.contest.start_date || '';
        this.endDate = this.contest.end_date || '';
        this.logoPath = this.contest.logo_path || '';

        // Загружаем команды и критерии
        this.loadTeamsAndCriteria();
      },
      error: (err: any) => {
        console.error('Ошибка при загрузке конкурса:', err);
        this.error = 'Не удалось загрузить данные конкурса';
        this.isLoading = false;
      }
    });
  }

  loadTeamsAndCriteria(): void {
    this.teamService.getList(this.contestId, 1, 100).subscribe({
      next: (response: any) => {
        const teams = response?.teams || response?.data || [];
        this.teams = teams.length > 0
          ? teams.map((t: Team) => ({ id: t.id, name: t.name }))
          : [{ name: '' }];

        this.loadCriteria();
      },
      error: (err: any) => {
        console.error('Ошибка при загрузке команд:', err);
        this.teams = [{ name: '' }];
        this.loadCriteria();
      }
    });
  }

  loadCriteria(): void {
    this.criterionService.getList(this.contestId).subscribe({
      next: (response: any) => {
        const criteria = response?.criteria || response?.data || [];
        this.criteria = criteria.length > 0
          ? criteria.map((c: Criterion) => ({
              id: c.id,
              name: c.name,
              description: c.description || '',
              max_score: c.max_score
            }))
          : [{ name: '', description: '', max_score: 10 }];

        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Ошибка при загрузке критериев:', err);
        this.criteria = [{ name: '', description: '', max_score: 10 }];
        this.isLoading = false;
      }
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      this.selectedFile = null;
      return;
    }
    this.selectedFile = input.files[0];
    this.logoPath = URL.createObjectURL(this.selectedFile);
  }

  addCriterion(event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    this.criteria.push({ name: '', description: '', max_score: 10 });
  }

  removeCriterion(index: number, event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    if (this.criteria.length > 1) {
      this.criteria.splice(index, 1);
    }
  }

  addTeam(event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    this.teams.push({ name: '' });
  }

  removeTeam(index: number, event?: Event): void {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    if (this.teams.length > 1) {
      this.teams.splice(index, 1);
    }
  }

  trackByIndex(index: number, item: any): number {
    return index;
  }

  goBack(): void {
    this.router.navigate(['/contest', this.contestId]);
  }

  onSubmit(): void {
    if (!this.name.trim()) {
      this.error = 'Введите название конкурса';
      return;
    }

    this.isSubmitting = true;
    this.error = null;

    const formData = new FormData();
    formData.append('name', this.name.trim());
    if (this.description.trim()) formData.append('description', this.description.trim());
    if (this.startDate) formData.append('start_date', this.startDate);
    if (this.endDate) formData.append('end_date', this.endDate);
    if (this.selectedFile) formData.append('logo', this.selectedFile);

    // Обновляем конкурс
    this.contestService.update(this.contestId, {
      name: this.name.trim(),
      description: this.description.trim(),
      start_date: this.startDate,
      end_date: this.endDate,
    }).subscribe({
      next: (response: any) => {
        // После успешного обновления конкурса обрабатываем команды и критерии
        this.handleTeamsAndCriteriaUpdate();
      },
      error: (err: any) => {
        this.isSubmitting = false;
        this.error = err.error?.error?.message || 'Ошибка при обновлении конкурса';
      }
    });
  }

  handleTeamsAndCriteriaUpdate(): void {
    const validTeams = this.teams.filter(t => t.name.trim() !== '');
    const validCriteria = this.criteria.filter(c => c.name.trim() !== '');

    const requests: any[] = [];

    // Создаем новые команды (без id)
    validTeams.filter(t => !t.id).forEach(team => {
      requests.push(this.teamService.create(this.contestId, { name: team.name }));
    });

    // Создаем новые критерии (без id)
    validCriteria.filter(c => !c.id).forEach(crit => {
      requests.push(this.criterionService.create(this.contestId, {
        name: crit.name,
        description: crit.description,
        max_score: crit.max_score
      }));
    });

    if (requests.length > 0) {
      import('rxjs').then(({ forkJoin }) => {
        forkJoin(requests).subscribe({
          next: () => this.finishUpdate(),
          error: (err) => {
            this.isSubmitting = false;
            this.error = 'Конкурс обновлен, но произошла ошибка при сохранении команд или критериев.';
          }
        });
      });
    } else {
      this.finishUpdate();
    }
  }

  private finishUpdate(): void {
    this.isSubmitting = false;
    this.router.navigate(['/contest', this.contestId]);
  }

  getLogoUrl(logoPath: string | null): string {
    if (!logoPath) return 'https://placehold.co/520x360/png?text=Preview';
    if (logoPath.startsWith('http')) return logoPath;
    return `/${logoPath.replace(/^\/+/, '')}`;
  }
}