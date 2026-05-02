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
import {
  CreateCriterionData
} from '../../../shared/models/contest.model';

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

  isSubmitting = false;
  error: string | null = null;

  constructor(
    private router: Router,
    private contestService: ContestService,
    private criterionService: CriterionService
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

  goBack(): void {
  this.router.navigate(['/']);
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
      next: (response) => {
        const contestId = response['contest'].id;

        const criteriaToCreate = this.criteria.filter(c => c.name.trim());

        if (criteriaToCreate.length === 0) {
          this.isSubmitting = false;
          this.router.navigate(['/']);
          return;
        }

        let completed = 0;

        criteriaToCreate.forEach((criterion) => {
          const data: CreateCriterionData = {
            name: criterion.name.trim(),
            description: criterion.description.trim() || undefined,
            max_score: criterion.max_score,
          };

          this.criterionService.create(contestId, data).subscribe({
            next: () => {
              completed++;
              if (completed === criteriaToCreate.length) {
                this.isSubmitting = false;
                this.router.navigate(['/']);
              }
            },
            error: () => {
              completed++;
              if (completed === criteriaToCreate.length) {
                this.isSubmitting = false;
                this.router.navigate(['/']);
              }
            },
          });
        });
      },
      error: (err) => {
        this.isSubmitting = false;
        this.error =
          err.error?.error?.message || 'Ошибка при создании конкурса';
        console.error('Create contest error:', err);
      },
    });
  }
}