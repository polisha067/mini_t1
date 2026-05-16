import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-contest-created-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './contest-created-page.html',
  styleUrl: './contest-created-page.scss',
})
export class ContestCreatedPage implements OnInit, OnDestroy {
  contestId: number | null = null;
  accessKey: string | null = null;
  contestName: string | null = null;

  copyToastMessage: string | null = null;
  private copyToastTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.contestId = Number(this.route.snapshot.queryParamMap.get('id'));
    this.accessKey = this.route.snapshot.queryParamMap.get('key');
    this.contestName = this.route.snapshot.queryParamMap.get('name');

    if (!this.contestId || !this.accessKey) {
      this.router.navigate(['/']);
    }
  }

  ngOnDestroy(): void {
    if (this.copyToastTimer !== null) {
      clearTimeout(this.copyToastTimer);
    }
  }

  copyKey(): void {
    if (!this.accessKey) {
      return;
    }
    navigator.clipboard.writeText(this.accessKey).then(
      () => this.showCopyToast('Ключ доступа для эксперта скопирован'),
      () => this.showCopyToast('Не удалось скопировать — выделите ключ вручную')
    );
  }

  copyId(): void {
    if (this.contestId) {
      navigator.clipboard.writeText(this.contestId.toString());
    }
  }

  goToAccount(): void {
    this.router.navigate(['/account/organizer']);
  }

  goToContest(): void {
    if (this.contestId) {
      this.router.navigate(['/contest', this.contestId]);
    }
  }

  private showCopyToast(message: string): void {
    if (this.copyToastTimer !== null) {
      clearTimeout(this.copyToastTimer);
    }
    this.copyToastMessage = message;
    this.copyToastTimer = setTimeout(() => {
      this.copyToastMessage = null;
      this.copyToastTimer = null;
    }, 2600);
  }
}