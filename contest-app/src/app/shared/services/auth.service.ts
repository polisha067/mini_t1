import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { Router } from '@angular/router';

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

export interface LoginResponse {
  status: string;
  access_token: string;
  user: User;
  redirect_url: string;
}

export interface RegisterResponse {
  status: string;
  message: string;
  user: User;
  redirect_url: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  role: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = '/api/auth';
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
      } catch (e) {
        this.clearAuth();
      }
    }
  }

  login(credentials: LoginRequest): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap((response: LoginResponse) => {
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('current_user', JSON.stringify(response.user));
        this.currentUserSubject.next(response.user);
      })
    );
  }

  register(userData: RegisterRequest): Observable<RegisterResponse> {
    return this.http.post<RegisterResponse>(`${this.apiUrl}/register`, userData).pipe(
      tap((response: RegisterResponse) => {
        // После регистрации автоматически логиним пользователя
        this.login({
          email: userData.email,
          password: userData.password
        }).subscribe({
          next: () => {
            // Перенаправление будет обработано в компоненте
          },
          error: (err: any) => {
            console.error('Auto-login after registration failed:', err);
          }
        });
      })
    );
  }

  logout(): void {
    this.http.post(`${this.apiUrl}/logout`, {}).subscribe({
      next: () => {
        this.clearAuth();
        this.router.navigate(['/login']);
      },
      error: () => {
        this.clearAuth();
        this.router.navigate(['/login']);
      }
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

  private clearAuth(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    this.currentUserSubject.next(null);
  }
}