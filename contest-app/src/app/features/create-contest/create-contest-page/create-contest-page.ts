import {
  Component,
  AfterViewInit,
  ElementRef,
  ViewChild
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import flatpickr from 'flatpickr';
import { Russian } from 'flatpickr/dist/l10n/ru';

import { ContestService } from '../../../core/contest.service';
import { CriterionService } from '../../../core/criterion.service';
import { TeamService } from '../../../core/team.service';

@Component({
  selector: 'app-create-contest-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './create-contest-page.html',
  styleUrl: './create-contest-page.scss',
})
export class CreateContestPage implements AfterViewInit {
  @ViewChild('startDateInput') startDateInput!: ElementRef<HTMLInputElement>;
  @ViewChild('endDateInput') endDateInput!: ElementRef<HTMLInputElement>;

  name = '';
  description = '';
  startDate = '';
  endDate = '';
  logoPath = '';
  selectedFile: File | null = null;

  criteria: { name: string; description: string; max_score: number }[] = [
    { name: '', description: '', max_score: 10 },
  ];

  teams: { name: string }[] = [
    { name: '' },
  ];

  isSubmitting = false;
  error: string | null = null;
  generatedAccessKey: string | null = null;

  constructor(
    private router: Router,
    private contestService: ContestService,
    private criterionService: CriterionService,
    private teamService: TeamService
  ) {}

  ngAfterViewInit(): void {
    flatpickr(this.startDateInput.nativeElement, {
      enableTime: true,
      dateFormat: 'Y-m-d\\TH:i:S',
      time_24hr: true,
      locale: Russian,
      onChange: (_, dateStr) => { this.startDate = dateStr; },
    });
    flatpickr(this.endDateInput.nativeElement, {
      enableTime: true,
      dateFormat: 'Y-m-d\\TH:i:S',
      time_24hr: true,
      locale: Russian,
      onChange: (_, dateStr) => { this.endDate = dateStr; },
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) {
      this.selectedFile = null;
      this.logoPath = '';
      return;
    }
    this.selectedFile = input.files[0];
    this.logoPath = URL.createObjectURL(this.selectedFile);
  }

  addCriterion(): void { this.criteria.push({ name: '', description: '', max_score: 10 }); }
  removeCriterion(i: number): void { if (this.criteria.length > 1) this.criteria.splice(i, 1); }
  addTeam(): void { this.teams.push({ name: '' }); }
  removeTeam(i: number): void { if (this.teams.length > 1) this.teams.splice(i, 1); }
  goBack(): void {
    this.router.navigate(['/account/organizer']);
  }
  copyKey(): void { if (this.generatedAccessKey) navigator.clipboard.writeText(this.generatedAccessKey); }

  onSubmit(): void {
    if (!this.name.trim()) {
      this.error = 'Введите название конкурса';
      return;
    }

    this.isSubmitting = true;
    this.error = null;
    this.generatedAccessKey = null;

    const formData = new FormData();
    formData.append('name', this.name.trim());
    if (this.description.trim()) formData.append('description', this.description.trim());
    if (this.startDate) formData.append('start_date', this.startDate);
    if (this.endDate) formData.append('end_date', this.endDate);
    if (this.selectedFile) formData.append('logo', this.selectedFile);

    console.log('Начинаем создание конкурса...');

    this.contestService.create(formData).subscribe({
      next: (res: any) => {
        const contestId = res['contest'].id;
        console.log('Конкурс создан, ID:', contestId);

        const criteriaToCreate = this.criteria.filter(c => c.name.trim());
        const teamsToCreate = this.teams.filter(t => t.name.trim());
        let completed = 0;
        const total = criteriaToCreate.length + teamsToCreate.length;

        const checkFinish = () => {
          completed++;
          if (completed === total) {
            console.log('Все вложенные объекты созданы');
            this.generateKeyAndFinish(contestId);
          }
        };

        if (total === 0) {
          checkFinish();
          return;
        }

        // Критерии
        criteriaToCreate.forEach(c => {
          this.criterionService.create(contestId, {
            name: c.name.trim(),
            description: c.description.trim() || undefined,
            max_score: c.max_score
          }).subscribe({
            next: checkFinish,
            error: (err) => { console.error('Ошибка критерия:', err); this.unlockAndShowError(err); checkFinish(); }
          });
        });

        // Команды
        teamsToCreate.forEach(t => {
          this.teamService.create(contestId, { name: t.name.trim() }).subscribe({
            next: checkFinish,
            error: (err) => { console.error('Ошибка команды:', err); this.unlockAndShowError(err); checkFinish(); }
          });
        });
      },
      error: (err) => this.unlockAndShowError(err)
    });
  }

  private generateKeyAndFinish(contestId: number): void {
    console.log('Генерируем ключ...');
    this.contestService.generateAccessKey(contestId).subscribe({
      next: (res: any) => {
        this.generatedAccessKey = res.access_key;
        this.isSubmitting = false;
        console.log('Ключ сгенерирован:', res.access_key);
      },
      error: (err) => {
        console.error('Ошибка генерации ключа:', err);
        this.unlockAndShowError(err);
      }
    });
  }

  private unlockAndShowError(err: any): void {
    this.isSubmitting = false;
    this.error = err.error?.error?.message || err.error?.message || 'Ошибка сохранения данных';
    console.error(' Финальная ошибка:', err);
  }
}