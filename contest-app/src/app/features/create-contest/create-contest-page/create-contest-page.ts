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
  CreateContestData,
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
      dateFormat: 'd.m.Y, H:i',
      time_24hr: true,
      locale: Russian,
      onChange: (_, dateStr) => {
        this.startDate = dateStr;
      },
    });

    flatpickr(this.endDateInput.nativeElement, {
      enableTime: true,
      dateFormat: 'd.m.Y, H:i',
      time_24hr: true,
      locale: Russian,
      onChange: (_, dateStr) => {
        this.endDate = dateStr;
      },
    });
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

    const contestData: CreateContestData = {
      name: this.name.trim(),
      description: this.description.trim() || undefined,
      start_date: this.startDate || undefined,
      end_date: this.endDate || undefined,
      logo_path: this.logoPath.trim() || undefined,
    };

    this.contestService.create(contestData).subscribe({
      next: (response) => {
        const contestId = response['contest'].id;

        const criteriaToCreate = this.criteria.filter(c => c.name.trim());

        if (criteriaToCreate.length === 0) {
          this.isSubmitting = false;
          this.router.navigate(['/contest', contestId]);
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
                this.router.navigate(['/contest', contestId]);
              }
            },
            error: () => {
              completed++;
              if (completed === criteriaToCreate.length) {
                this.isSubmitting = false;
                this.router.navigate(['/contest', contestId]);
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