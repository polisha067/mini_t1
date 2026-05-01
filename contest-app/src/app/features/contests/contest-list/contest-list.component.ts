import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ContestService } from '../../../core/contest.service';
import { AuthService } from '../../../shared/services/auth.service';
import { Contest } from '../../../shared/models/contest.model';

@Component({
  selector: 'app-contest-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './contest-list.component.html',
  styleUrls: ['./contest-list.component.scss']
})
export class ContestListComponent implements OnInit {
  contests: Contest[] = [];
  filteredContests: Contest[] = [];
  searchQuery = '';
  isLoading = true;
  error: string | null = null;

  constructor(
    private router: Router,
    private contestService: ContestService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadContests();
  }

  loadContests(): void {
    this.isLoading = true;
    this.error = null;

    this.contestService.getList(1, 100).subscribe({
      next: (response) => {
        const contests = (response['contests'] || []) as Contest[];
        console.log('КОНКУРСЫ:', contests);

        this.contests = [...contests];
        this.filteredContests = [...contests];
        this.isLoading = false;

        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to load contests:', err);

        this.contests = [];
        this.filteredContests = [];
        this.isLoading = false;
        this.error = 'Не удалось загрузить конкурсы';

        this.cdr.detectChanges();
      }
    });
  }

  onSearch(): void {
    const query = this.searchQuery.toLowerCase().trim();

    if (!query) {
      this.filteredContests = [...this.contests];
      return;
    }

    this.filteredContests = this.contests.filter((contest) =>
      contest.name.toLowerCase().includes(query)
    );
  }

  isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }

  getAccountLabel(): string {
    const user = this.authService.getCurrentUser();
    return user?.username || user?.email || 'аккаунт';
  }

  goToAccount(): void {
    const user = this.authService.getCurrentUser();

    if (user?.role === 'organizer') {
      this.router.navigate(['/account/organizer']);
      return;
    }

    this.router.navigate(['/account/expert']);
  }

  logout(): void {
    this.authService.logout();
    this.cdr.detectChanges();
  }

  goToLogin(): void {
    this.router.navigate(['/login']);
  }

  goToRegister(): void {
    this.router.navigate(['/register']);
  }

  goToContest(contestId: number): void {
    this.router.navigate(['/contest', contestId]);
  }

  getYear(dateStr: string | null): string {
    if (!dateStr) return '';
    return new Date(dateStr).getFullYear().toString();
  }

  getLogoUrl(logoPath: string | null): string {
    if (!logoPath) {
      return 'https://placehold.co/520x360/png?text=Preview';
    }

    if (logoPath.startsWith('http')) {
      return logoPath;
    }

    return `http://localhost:5000/${logoPath}`;
  }
}