import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
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

  constructor(
    private router: Router,
    private teamService: TeamService
  ) {}

  ngOnInit(): void {
    this.loadTeams();
  }

  loadTeams(): void {
    // Загружаем команды первого конкурса (в реальном приложении contestId берётся из route params)
    // Для participants страницы предполагаем, что пользователь пришёл с детали конкурса
    // и contestId сохранён. Пока берём из queryParams или используем 1.
    const contestId = 1; // TODO: получать из route state / queryParams
    this.teamService.getList(contestId, 1, 100).subscribe({
      next: (response) => {
        this.teams = response['teams'] as Team[];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load teams:', err);
        this.teams = [];
        this.isLoading = false;
      },
    });
  }

  goBack(): void {
    this.router.navigate(['/']);
  }

  goToRating(): void {
    this.router.navigate(['/contest', 1]); // TODO: использовать правильный contestId
  }
}
