import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ContestService } from '../../core/contest.service';
import { TeamService } from '../../core/team.service';
import { CriterionService } from '../../core/criterion.service';
import { Contest, Team, Criterion } from '../../shared/models/contest.model';

@Component({
  selector: 'app-edit-contest-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './edit-contest-page.html',
  styleUrl: './edit-contest-page.scss',
})
export class EditContestPage implements OnInit {
  originalTeams: Team[] = [];
  originalCriteria: Criterion[] = [];

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
    private criterionService: CriterionService,
    private cdr: ChangeDetectorRef
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

  formatDateForInput(dateStr: string | null | undefined): string {
    if (!dateStr) return '';
    // Преобразуем ISO формат (2026-05-26T19:38:07Z) в формат YYYY-MM-DDTHH:mm для datetime-local
    return dateStr.slice(0, 16);
  }

  loadContestData(): void {
    this.isLoading = true;
    this.error = null;
    this.cdr.detectChanges();

    this.contestService.getById(this.contestId).subscribe({
      next: (response: any) => {
        this.contest = response?.contest || response?.data || (response?.id ? response : null);

        if (!this.contest) {
          this.error = 'Конкурс не найден';
          this.isLoading = false;
          this.cdr.detectChanges();
          return;
        }

        // Заполняем форму данными конкурса
        this.name = this.contest.name;
        this.description = this.contest.description || '';
        this.startDate = this.formatDateForInput(this.contest.start_date);
        this.endDate = this.formatDateForInput(this.contest.end_date);
        this.logoPath = this.contest.logo_path || '';

        // Загружаем команды и критерии
        this.loadTeamsAndCriteria();
      },
      error: (err: any) => {
        console.error('Ошибка при загрузке конкурса:', err);
        this.error = 'Не удалось загрузить данные конкурса';
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }


  loadTeamsAndCriteria(): void {
    this.teamService.getList(this.contestId, 1, 100).subscribe({
      next: (response: any) => {
        const teams = response?.teams || response?.data || [];
        this.originalTeams = [...teams];
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
        this.originalCriteria = [...criteria];
        this.criteria = criteria.length > 0
          ? criteria.map((c: Criterion) => ({
              id: c.id,
              name: c.name,
              description: c.description || '',
              max_score: c.max_score
            }))
          : [{ name: '', description: '', max_score: 10 }];

        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        console.error('Ошибка при загрузке критериев:', err);
        this.criteria = [{ name: '', description: '', max_score: 10 }];
        this.isLoading = false;
        this.cdr.detectChanges();
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
      this.cdr.detectChanges();
      return;
    }

    this.isSubmitting = true;
    this.error = null;
    this.cdr.detectChanges();

    const formData = new FormData();
    formData.append('name', this.name.trim());
    
    // Безопасное добавление описания
    const desc = (this.description || '').trim();
    if (desc) {
      formData.append('description', desc);
    }
    
    if (this.startDate) formData.append('start_date', this.startDate);
    if (this.endDate) formData.append('end_date', this.endDate);
    if (this.selectedFile) {
      formData.append('logo', this.selectedFile);
    }
    
    // Передаем logo_path, чтобы обойти баг бэкенда и принудительно вызвать db.session.commit()
    formData.append('logo_path', this.contest?.logo_path || '');

    // Обновляем конкурс через FormData (чтобы отправлялся и файл, и данные формы)
    this.contestService.update(this.contestId, formData).subscribe({
      next: (response: any) => {
        // После успешного обновления конкурса обрабатываем команды и критерии
        this.handleTeamsAndCriteriaUpdate();
      },
      error: (err: any) => {
        this.isSubmitting = false;
        this.error = err.error?.error?.message || 'Ошибка при обновлении конкурса';
        this.cdr.detectChanges();
      }
    });
  }

  handleTeamsAndCriteriaUpdate(): void {
    const validTeams = this.teams.filter(t => t.name.trim() !== '');
    const validCriteria = this.criteria.filter(c => c.name.trim() !== '');

    const requests: any[] = [];

    // 1. Удаляем команды, которых больше нет в списке
    this.originalTeams.forEach(orig => {
      const exists = validTeams.some(t => t.id === orig.id);
      if (!exists) {
        requests.push(this.teamService.delete(orig.id));
      }
    });

    // 2. Создаем новые команды или обновляем существующие
    validTeams.forEach(team => {
      if (!team.id) {
        requests.push(this.teamService.create(this.contestId, { name: team.name }));
      } else {
        const orig = this.originalTeams.find(t => t.id === team.id);
        if (orig && orig.name !== team.name) {
          requests.push(this.teamService.update(team.id, { name: team.name }));
        }
      }
    });

    // 3. Удаляем критерии, которых больше нет в списке
    this.originalCriteria.forEach(orig => {
      const exists = validCriteria.some(c => c.id === orig.id);
      if (!exists) {
        requests.push(this.criterionService.delete(orig.id));
      }
    });

    // 4. Создаем новые критерии или обновляем существующие
    validCriteria.forEach(crit => {
      if (!crit.id) {
        requests.push(this.criterionService.create(this.contestId, {
          name: crit.name,
          description: crit.description,
          max_score: crit.max_score
        }));
      } else {
        const orig = this.originalCriteria.find(c => c.id === crit.id);
        if (orig && (orig.name !== crit.name || (orig.description || '') !== crit.description || orig.max_score !== crit.max_score)) {
          requests.push(this.criterionService.update(crit.id, {
            name: crit.name,
            description: crit.description,
            max_score: crit.max_score
          }));
        }
      }
    });

    if (requests.length > 0) {
      import('rxjs').then(({ forkJoin }) => {
        forkJoin(requests).subscribe({
          next: () => this.finishUpdate(),
          error: (err) => {
            this.isSubmitting = false;
            this.error = 'Конкурс обновлен, но произошла ошибка при сохранении команд или критериев.';
            this.cdr.detectChanges();
          }
        });
      });
    } else {
      this.finishUpdate();
    }
  }

  private finishUpdate(): void {
    this.isSubmitting = false;
    this.cdr.detectChanges();
    this.router.navigate(['/contest', this.contestId]);
  }

  getLogoUrl(logoPath: string | null): string {
    if (!logoPath) return 'assets/images/photo.jpg';
    if (logoPath.startsWith('http') || logoPath.startsWith('blob:') || logoPath.startsWith('data:')) return logoPath;
    
    const cleanPath = logoPath.replace(/^\/+/, '');
    if (cleanPath.startsWith('uploads/')) {
      return `/${cleanPath}`;
    }
    return `/uploads/${cleanPath}`;
  }

  handleImageError(event: Event): void {
    const target = event.target as HTMLImageElement;
    target.src = 'assets/images/photo.jpg';
  }
}