import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
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
    private teamService: TeamService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Подписываемся на ID, чтобы он не терялся при обновлении страницы
    this.route.paramMap.subscribe(params => {
      const id = params.get('contestId') || params.get('id'); 
      if (id) {
        this.contestId = +id;
        this.loadTeams();
      }
    });
  }

  loadTeams(): void {
      if (!this.contestId) return; // Проверка на null

      this.isLoading = true;
      this.teamService.getList(this.contestId, 1, 100) // Теперь без ошибки типа
        .pipe(
          finalize(() => {
            this.isLoading = false;
            this.cdr.detectChanges(); // Принудительное обновление
          })
        )
        .subscribe({
          next: (response: any) => {
            console.log('Полный ответ от бэкенда по командам:', response); // Посмотрим в консоль
            
            // Проверяем все возможные варианты, где могут лежать данные
            this.teams = response?.teams || response?.data || (Array.isArray(response) ? response : []);
            
            this.cdr.detectChanges();
          },
          error: () => {
            this.error = 'Ошибка загрузки команд';
          }
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