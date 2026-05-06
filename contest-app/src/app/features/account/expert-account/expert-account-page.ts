import { Component, OnInit, OnDestroy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../../shared/services/auth.service';
import { ContestService } from '../../../core/contest.service';
import { finalize, Subscription } from 'rxjs';

@Component({
  selector: 'app-expert-account-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './expert-account-page.html',
  styleUrls: ['./expert-account-page.scss']
})
export class ExpertAccountPage implements OnInit, OnDestroy {
  user: any = null;
  expertContests: any[] = [];
  isLoadingContests = false;
  contestsError = '';
  
  isJoining = false;
  joinError = '';
  joinSuccess = '';
  joinContestId: number | null = null;
  joinAccessKey = '';

  private userSub?: Subscription;

  constructor(
    private authService: AuthService,
    private contestService: ContestService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    const currentUser = this.authService.getCurrentUser();
    if (currentUser) {
      this.user = currentUser;
      this.loadExpertContests();
    } else {
      this.userSub = this.authService.currentUser$.subscribe(u => {
        if (u && !this.user) {
          this.user = u;
          this.loadExpertContests();
          this.cdr.detectChanges();
        }
      });
    }
  }

  ngOnDestroy(): void {
    this.userSub?.unsubscribe();
  }

  loadExpertContests(): void {
    if (this.isLoadingContests) return;
    this.isLoadingContests = true;
    this.cdr.detectChanges();
    
    this.contestService.getMyExpertContests()
      .pipe(finalize(() => {
        this.isLoadingContests = false;
        this.cdr.detectChanges();
      }))
      .subscribe({
        next: (res: any) => {
          this.expertContests = res.contests || [];
          this.cdr.detectChanges();
        },
        error: () => {
          this.contestsError = 'Ошибка загрузки списка';
          this.cdr.detectChanges();
        }
      });
  }

  joinContest(): void {
    if (!this.joinContestId || !this.joinAccessKey || this.isJoining) return;
    
    this.isJoining = true;
    this.joinError = '';
    this.joinSuccess = '';
    this.cdr.detectChanges();

    this.contestService.joinContestByAccessKey(this.joinContestId, this.joinAccessKey)
      .pipe(finalize(() => {
        this.isJoining = false;
        this.cdr.detectChanges();
      }))
      .subscribe({
        next: (res: any) => {
          this.joinSuccess = res.message || 'Успешно!';
          this.joinContestId = null;
          this.joinAccessKey = '';
          this.loadExpertContests();
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.joinError = err.error?.message || 'Ошибка подключения';
          this.cdr.detectChanges();
        }
      });
  }

  goHome(): void { this.router.navigate(['/']); }
  logout(): void { this.authService.logout(); this.router.navigate(['/login']); }
  goToContest(id: number): void { this.router.navigate(['/contests', id]); }
}