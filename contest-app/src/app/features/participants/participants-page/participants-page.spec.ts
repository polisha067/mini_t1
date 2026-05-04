import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { TeamService } from '../../../core/team.service';
import { Team } from '../../../shared/models/contest.model';

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
    const idParam = this.route.snapshot.paramMap.get('contestId');
    if (idParam) {
      this.contestId = +idParam;
      this.loadTeams();
    } else {
      this.error = 'Не указан конкурс';
      this.isLoading = false;
    }
  }

  loadTeams(): void {
    if (!this.contestId) return;

    this.isLoading = true;
    this.teamService.getList(this.contestId, 1, 100).subscribe({
      next: (response: any) => {
        this.teams = response['teams'] as Team[];
        this.isLoading = false;
      },
      error: (err: any) => {
        console.error('Failed to load teams:', err);
        this.error = 'Не удалось загрузить команды';
        this.teams = [];
        this.isLoading = false;
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
    } else {
      this.router.navigate(['/']);
    }
  }

  goToTeam(teamId: number): void {
    console.log('Team clicked:', teamId);
  }
}