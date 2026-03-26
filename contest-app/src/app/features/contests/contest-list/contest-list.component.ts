import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-contest-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './contest-list.component.html',
  styleUrls: ['./contest-list.component.scss']
})


export class ContestListComponent {

  constructor(private router: Router) {}

  activeContests = [
    { id: 1, title: 'хакатон 1', year: '2025', image: 'assets/images/photo.jpg' },
    { id: 2, title: 'хакатон 2', year: '2025', image: 'assets/images/photo.jpg' },
    { id: 3, title: 'хакатон 3', year: '2025', image: 'assets/images/photo.jpg' }
  ];

  goToLogin() {  
    this.router.navigate(['/login']);
  }

  goToContest(contestId: number) {
    this.router.navigate(['/contest', contestId]);
}

  goToRegister() {  
    this.router.navigate(['/register']);
  }

}

