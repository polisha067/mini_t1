import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-password-reset-sent',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './password-reset-sent.html',
  styleUrl: './password-reset-sent.scss',
})
export class PasswordResetSent implements OnInit {
  email: string = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.email = params['email'] || '';
    });
  }

  goHome(): void {
    this.router.navigate(['/']);
  }
}