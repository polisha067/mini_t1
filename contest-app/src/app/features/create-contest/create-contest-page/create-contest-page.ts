import { Component, AfterViewInit, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import flatpickr from 'flatpickr';
import { Russian } from 'flatpickr/dist/l10n/ru';
import { ContestService } from '../../../core/contest.service';

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

  generatedAccessKey: string | null = null;
  isSubmitting = false;
  error: string | null = null;

  constructor(
    private router: Router,
    private contestService: ContestService
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

  generateAccessKey(): void {
    const array = new Uint8Array(24);
    window.crypto.getRandomValues(array);
    this.generatedAccessKey = Array.from(array, byte => 
      byte.toString(36).padStart(2, '0')
    ).join('');
  }

  copyKey(): void {
    if (this.generatedAccessKey) {
      navigator.clipboard.writeText(this.generatedAccessKey);
    }
  }

  goBack(): void {
    this.router.navigate(['/account/organizer']);
  }
  onSubmit(): void {
  if (!this.name.trim()) {
    this.error = 'Введите название конкурса';
    return;
  }

  this.isSubmitting = true;
  this.error = null;

  this.generateAccessKey();

  const formData = new FormData();
  formData.append('name', this.name.trim());
  if (this.description.trim()) formData.append('description', this.description.trim());
  if (this.startDate) formData.append('start_date', this.startDate);
  if (this.endDate) formData.append('end_date', this.endDate);
  if (this.selectedFile) formData.append('logo', this.selectedFile);

  if (this.generatedAccessKey) {
    formData.append('access_key', this.generatedAccessKey);
  }

  this.contestService.create(formData).subscribe({
    next: (response: any) => {
      const contestId = response.contest?.id || response.id;
      const key = this.generatedAccessKey;
      
      this.router.navigate(['/contest-created'], {
        queryParams: {
          id: contestId,
          key: key,
          name: this.name.trim()
        }
      });
    },
    error: (err: any) => {
      this.isSubmitting = false;
      this.error = err.error?.error?.message || 'Ошибка при создании конкурса';
    }
  });
}}