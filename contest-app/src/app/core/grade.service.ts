import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Grade,
  CreateGradeData,
  UpdateGradeData,
  PaginatedResponse,
  ApiResponse,
} from '../shared/models/contest.model';

@Injectable({
  providedIn: 'root',
})
export class GradeService {
  constructor(private http: HttpClient) {}

  /**
   * Создать оценку (только expert)
   */
  create(data: CreateGradeData): Observable<ApiResponse<Grade>> {
    return this.http.post<ApiResponse<Grade>>('/api/grades', data);
  }

  /**
   * Получить оценки команды
   */
  getTeamGrades(
    teamId: number,
    page: number = 1,
    perPage: number = 100
  ): Observable<PaginatedResponse<Grade>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());

    return this.http.get<PaginatedResponse<Grade>>(
      `/api/teams/${teamId}/grades`,
      { params }
    );
  }

  /**
   * Получить свои оценки (только expert)
   */
  getMyGrades(
    expertId: number,
    page: number = 1,
    perPage: number = 100
  ): Observable<PaginatedResponse<Grade>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());

    return this.http.get<PaginatedResponse<Grade>>(
      `/api/experts/${expertId}/grades`,
      { params }
    );
  }

  /**
   * Обновить оценку (только владелец-эксперт)
   */
  update(
    gradeId: number,
    data: UpdateGradeData
  ): Observable<ApiResponse<Grade>> {
    return this.http.put<ApiResponse<Grade>>(`/api/grades/${gradeId}`, data);
  }

  /**
   * Удалить оценку (только владелец-эксперт)
   */
  delete(gradeId: number): Observable<ApiResponse<Grade>> {
    return this.http.delete<ApiResponse<Grade>>(`/api/grades/${gradeId}`);
  }
}
