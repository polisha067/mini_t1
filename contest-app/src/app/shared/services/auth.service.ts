import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { Router } from '@angular/router';
import {
  User,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
} from '../../shared/models/contest.model';

// Re-export типов для использования в других модулях
export type { LoginRequest, RegisterRequest, AuthResponse } from '../../shared/models/contest.model';


@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private readonly apiUrl = '/api/auth';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadUserFromStorage();
  }

  private loadUserFromStorage(): void {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('current_user');
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        this.currentUserSubject.next(user);
      } catch {
        this.clearAuth();
      }
    }
  }

  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.http
      .post<AuthResponse>(`${this.apiUrl}/login`, credentials)
      .pipe(
        tap((response) => {
          this.saveAuthData(response);
        })
      );
  }

  refreshToken(): Observable<AuthResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http
      .post<AuthResponse>(`${this.apiUrl}/refresh`, {}, {
        headers: { Authorization: `Bearer ${refreshToken}` }
      })
      .pipe(
        tap((response) => {
          if (response.access_token) {
            localStorage.setItem('access_token', response.access_token);
          }
        })
      );
  }

  private saveAuthData(response: AuthResponse): void {
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token);
    }
    if (response.refresh_token) {
      localStorage.setItem('refresh_token', response.refresh_token);
    }
    if (response.user) {
      localStorage.setItem('current_user', JSON.stringify(response.user));
      this.currentUserSubject.next(response.user);
    }
  }

  register(userData: RegisterRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/register`, userData);
  }

  logout(): void {
    this.clearAuthState();
    this.router.navigate(['/']);

    this.http.post(`${this.apiUrl}/logout`, {}).subscribe({
      error: (err) => {
        console.warn('Logout request failed:', err);
      },
    });
  }

  getCurrentUser(): User | null {
    return this.currentUserSubject.value;
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRole(): string | null {
    const user = this.getCurrentUser();
    return user?.role ?? null;
  }

  isOrganizer(): boolean {
    return this.getRole() === 'organizer';
  }

  isExpert(): boolean {
    return this.getRole() === 'expert';
  }

  clearAuthState(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    this.currentUserSubject.next(null);
  }

  private clearAuth(): void {
    this.clearAuthState();
  }
}
