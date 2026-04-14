import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Contest,
  CreateContestData,
  UpdateContestData,
  PaginatedResponse,
  ApiResponse,
  VotingStatus,
} from '../shared/models/contest.model';

@Injectable({
  providedIn: 'root',
})
export class ContestService {
  private readonly apiUrl = '/api/contests';

  constructor(private http: HttpClient) {}

  /**
   * Получить список конкурсов с пагинацией
   */
  getList(
    page: number = 1,
    perPage: number = 10,
    organizerId?: number
  ): Observable<PaginatedResponse<Contest>> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());

    if (organizerId) {
      params = params.set('organizer_id', organizerId.toString());
    }

    return this.http.get<PaginatedResponse<Contest>>(this.apiUrl, { params });
  }

  /**
   * Получить детали конкурса по ID
   */
  getById(contestId: number): Observable<ApiResponse<Contest>> {
    return this.http.get<ApiResponse<Contest>>(`${this.apiUrl}/${contestId}`);
  }

  /**
   * Создать конкурс (только organizer)
   */
  create(data: CreateContestData): Observable<ApiResponse<Contest>> {
    return this.http.post<ApiResponse<Contest>>(this.apiUrl, data);
  }

  /**
   * Обновить конкурс (только владелец-organizer)
   */
  update(
    contestId: number,
    data: UpdateContestData
  ): Observable<ApiResponse<Contest>> {
    return this.http.put<ApiResponse<Contest>>(`${this.apiUrl}/${contestId}`, data);
  }

  /**
   * Удалить конкурс (только владелец-organizer)
   */
  delete(contestId: number): Observable<ApiResponse<Contest>> {
    return this.http.delete<ApiResponse<Contest>>(`${this.apiUrl}/${contestId}`);
  }

  /**
   * Завершить конкурс (финализировать)
   */
  finalize(contestId: number): Observable<ApiResponse<Contest>> {
    return this.http.post<ApiResponse<Contest>>(
      `${this.apiUrl}/${contestId}/finalize`,
      {}
    );
  }

  /**
   * Получить статус голосования
   */
  getVotingStatus(contestId: number): Observable<ApiResponse<VotingStatus>> {
    return this.http.get<ApiResponse<VotingStatus>>(
      `${this.apiUrl}/${contestId}/voting-status`
    );
  }
}
