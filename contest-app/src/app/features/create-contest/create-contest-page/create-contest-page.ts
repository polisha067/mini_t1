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
import { HttpErrorResponse } from '@angular/common/http'; 

import { ContestService } from '../../../core/contest.service';
import { CriterionService } from '../../../core/criterion.service';
import { TeamService } from '../../../core/team.service'; 
import { CreateCriterionData } from '../../../shared/models/contest.model';

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
      onChange: (_, dateStr) => {
        this.startDate = dateStr;
      },
    });

    flatpickr(this.endDateInput.nativeElement, {
      enableTime: true,
      dateFormat: 'Y-m-d\\TH:i:S',
      time_24hr: true,
      locale: Russian,
      onChange: (_, dateStr) => {
        this.endDate = dateStr;
      },
    });
  } 

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files || input.files.length === 0) {
      this.selectedFile = null;
      this.logoPath = '';
      return;
    }
    this.selectedFile = input.files[0];
    this.logoPath = URL.createObjectURL(this.selectedFile);
  }

  // --- Критерии ---
  addCriterion(): void {
    this.criteria.push({ name: '', description: '', max_score: 10 });
  }

  removeCriterion(index: number): void {
    if (this.criteria.length > 1) {
      this.criteria.splice(index, 1);
    }
  }

  // --- Команды ---
  addTeam(): void {
    this.teams.push({ name: '' });
  }

  removeTeam(index: number): void {
    if (this.teams.length > 1) {
      this.teams.splice(index, 1);
    }
  }

  goBack(): void {
    this.router.navigate(['/']);
  }

  // --- Отправка формы ---
  onSubmit(): void {
    if (!this.name.trim()) {
      this.error = 'Введите название конкурса';
      return;
    }

    this.isSubmitting = true;
    this.error = null;

    const formData = new FormData();
    formData.append('name', this.name.trim());

    if (this.description.trim()) {
      formData.append('description', this.description.trim());
    }
    if (this.startDate) {
      formData.append('start_date', this.startDate);
    }
    if (this.endDate) {
      formData.append('end_date', this.endDate);
    }
    if (this.selectedFile) {
      formData.append('logo', this.selectedFile);
    }

    // 1. Создаем конкурс
    this.contestService.create(formData).subscribe({
      next: (response: any) => {
        const contestId = response['contest'].id;

        // Фильтруем заполненные данные
        const criteriaToCreate = this.criteria.filter(c => c.name.trim());
        const teamsToCreate = this.teams.filter(t => t.name.trim());

        // Если ничего не нужно создавать — сразу редирект
        if (criteriaToCreate.length === 0 && teamsToCreate.length === 0) {
          this.isSubmitting = false;
          this.router.navigate(['/']);
          return;
        }

        let criteriaCompleted = 0;
        let teamsCompleted = 0;
        const totalTasks = criteriaToCreate.length + teamsToCreate.length;

        const checkAllDone = () => {
          if (criteriaCompleted + teamsCompleted === totalTasks) {
            this.isSubmitting = false;
            this.router.navigate(['/']);
          }
        };

        // 2. Создаем критерии
        criteriaToCreate.forEach((criterion) => {
          this.criterionService.create(contestId, {
            name: criterion.name.trim(),
            description: criterion.description.trim() || undefined,
            max_score: criterion.max_score,
          }).subscribe({
            next: () => {
              criteriaCompleted++;
              checkAllDone();
            },
            error: (err) => {
              console.error('Criterion error:', err);
              criteriaCompleted++;
              checkAllDone();
            },
          });
        });

        // 3. Создаем команды
        teamsToCreate.forEach((team) => {
          this.teamService.create(contestId, {
            name: team.name.trim(),
          }).subscribe({
            next: () => {
              teamsCompleted++;
              checkAllDone();
            },
            error: (err: any) => { 
              console.error('Team error:', err);
              teamsCompleted++;
              checkAllDone();
            },
          });
        });
      },
      error: (err: any) => { 
        this.isSubmitting = false;
        this.error = err.error?.error?.message || 'Ошибка при создании конкурса';
        console.error('Create contest error:', err);
      },
    });
  } 
} 