import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Criterion,
  CreateCriterionData,
  PaginatedResponse,
  ApiResponse,
} from '../shared/models/contest.model';

@Injectable({
  providedIn: 'root',
})
export class CriterionService {
  private readonly baseUrl = '/api/contests';

  constructor(private http: HttpClient) {}

  /**
   * Получить список критериев конкурса
   */
  getList(
    contestId: number,
    page: number = 1,
    perPage: number = 100
  ): Observable<PaginatedResponse<Criterion>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());

    return this.http.get<PaginatedResponse<Criterion>>(
      `${this.baseUrl}/${contestId}/criteria`,
      { params }
    );
  }

  /**
   * Получить критерий по ID
   */
  getById(criterionId: number): Observable<ApiResponse<Criterion>> {
    return this.http.get<ApiResponse<Criterion>>(`/api/criteria/${criterionId}`);
  }

  /**
   * Создать критерий (только organizer конкурса)
   */
  create(
    contestId: number,
    data: CreateCriterionData
  ): Observable<ApiResponse<Criterion>> {
    return this.http.post<ApiResponse<Criterion>>(
      `${this.baseUrl}/${contestId}/criteria`,
      data
    );
  }

  /**
   * Обновить критерий (только organizer)
   */
  update(
    criterionId: number,
    data: CreateCriterionData
  ): Observable<ApiResponse<Criterion>> {
    return this.http.put<ApiResponse<Criterion>>(
      `/api/criteria/${criterionId}`,
      data
    );
  }

  /**
   * Удалить критерий (только organizer)
   */
  delete(criterionId: number): Observable<ApiResponse<Criterion>> {
    return this.http.delete<ApiResponse<Criterion>>(
      `/api/criteria/${criterionId}`
    );
  }
}
