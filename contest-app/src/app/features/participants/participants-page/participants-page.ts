import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { TeamService } from '../../../core/team.service';
import { Team } from '../../../shared/models/contest.model';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-participants-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './participants-page.html',
  styleUrls: ['./participants-page.scss'],
})
export class ParticipantsPage implements OnInit {
  teams: Team[] = [];
  isLoading = true;
  error: string | null = null;
  contestId: number | null = null;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private teamService: TeamService
  ) {}

ngOnInit(): void {
  this.contestId = Number(this.route.snapshot.paramMap.get('contestId'));

  if (this.contestId) {
    this.loadTeams();
  } else {
    this.error = 'Конкурс не найден';
    this.isLoading = false;
  }
}

  loadTeams(): void {
    if (!this.contestId) return;

    this.isLoading = true;
    this.teamService.getList(this.contestId, 1, 100)
      .pipe(finalize(() => this.isLoading = false))
      .subscribe({
        next: (response: any) => {
          const rawData = response?.teams || response?.data || response;
          this.teams = Array.isArray(rawData) ? rawData : [];
        },
        error: (err) => {
          console.error('Teams load error:', err);
          this.error = 'Ошибка загрузки команд';
        },
      });
  }

goBack(): void {
  if (this.contestId) {
    this.router.navigate(['/contest', this.contestId]);
  } else {
    this.router.navigate(['/']);
  }
}

  goToRating(): void {
    if (this.contestId) {
      this.router.navigate(['/contest', this.contestId]);
    }
  }
}