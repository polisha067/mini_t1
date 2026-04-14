import { Component, OnInit } from '@angular/core';
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
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadContests();
  }

  loadContests(): void {
    this.isLoading = true;
    this.contestService.getList(1, 100).subscribe({
      next: (response) => {
        this.contests = response['contests'] as Contest[];
        this.filteredContests = [...this.contests];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load contests:', err);
        // Если API недоступен — показываем пустой список
        this.contests = [];
        this.filteredContests = [];
        this.isLoading = false;
      }
    });
  }

  onSearch(): void {
    const query = this.searchQuery.toLowerCase().trim();
    if (!query) {
      this.filteredContests = [...this.contests];
      return;
    }
    this.filteredContests = this.contests.filter(c =>
      c.name.toLowerCase().includes(query)
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
  }

  goToLogin() {
    this.router.navigate(['/login']);
  }

  goToRegister() {
    this.router.navigate(['/register']);
  }

  goToContest(contestId: number) {
    this.router.navigate(['/contest', contestId]);
  }

  getYear(dateStr: string | null): string {
    if (!dateStr) return '';
    return new Date(dateStr).getFullYear().toString();
  }

  getLogoUrl(logoPath: string | null): string {
    if (!logoPath) return 'assets/images/photo.jpg';
    // Если logo_path — это URL
    if (logoPath.startsWith('http')) return logoPath;
    // Для локалки и Docker идем через фронт-прокси
    return `/${logoPath.replace(/^\/+/, '')}`;
  }
}

