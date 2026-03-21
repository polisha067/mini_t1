import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-contest-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './contest-list.component.html',
  styleUrls: ['./contest-list.component.scss']
})
export class ContestListComponent {
  activeContests = [
    { id: 1, title: 'хакатон 1', year: '2025', image: 'assets/images/photo.jpg' },
    { id: 2, title: 'хакатон 2', year: '2025', image: 'assets/images/photo.jpg' },
    { id: 3, title: 'хакатон 3', year: '2025', image: 'assets/images/photo.jpg' }
  ];
}

