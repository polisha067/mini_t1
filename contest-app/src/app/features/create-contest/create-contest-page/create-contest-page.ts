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

  addCriterion(): void {
    this.criteria.push({ name: '', description: '', max_score: 10 });
  }

  removeCriterion(index: number): void {
    if (this.criteria.length > 1) {
      this.criteria.splice(index, 1);
    }
  }

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

  copyKey(): void {
    if (this.generatedAccessKey) {
      navigator.clipboard.writeText(this.generatedAccessKey);
    }
  }

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

    this.contestService.create(formData).subscribe({
      next: (response: any) => {
        const contestId = response['contest'].id;

        const criteriaToCreate = this.criteria.filter(c => c.name.trim());
        const teamsToCreate = this.teams.filter(t => t.name.trim());

        if (criteriaToCreate.length === 0 && teamsToCreate.length === 0) {
          // Если нет критериев и команд — генерируем ключ и завершаем
          this.generateKeyAndFinish(contestId);
          return;
        }

        let criteriaCompleted = 0;
        let teamsCompleted = 0;
        const totalTasks = criteriaToCreate.length + teamsToCreate.length;

        const checkAllDone = () => {
          if (criteriaCompleted + teamsCompleted === totalTasks) {
            this.generateKeyAndFinish(contestId);
          }
        };

        // Создаем критерии
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
            error: (err: any) => {
              console.error('Criterion error:', err);
              criteriaCompleted++;
              checkAllDone();
            },
          });
        });

        // Создаем команды
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


  private generateKeyAndFinish(contestId: number): void {
    this.contestService.generateAccessKey(contestId).subscribe({
      next: (res: any) => {
        this.generatedAccessKey = res.access_key;
        this.isSubmitting = false;
      },
      error: (err: any) => {
        console.error('Generate key error:', err);
        this.isSubmitting = false;
        this.router.navigate(['/']); 
      }
    });
  }
}