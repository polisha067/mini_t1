import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  RankingEntry,
  PaginatedResponse,
  ApiResponse,
} from '../shared/models/contest.model';

@Injectable({
  providedIn: 'root',
})
export class RankingService {
  private readonly baseUrl = '/api/contests';

  constructor(private http: HttpClient) {}

  /**
   * Получить рейтинг команд конкурса
   * @param contestId ID конкурса
   * @param page страница пагинации
   * @param perPage количество на странице
   * @param sort направление сортировки: 'desc' (по убыванию) или 'asc'
   */
  getRanking(
    contestId: number,
    page: number = 1,
    perPage: number = 100,
    sort: 'asc' | 'desc' = 'desc'
  ): Observable<PaginatedResponse<RankingEntry>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString())
      .set('sort', sort);

    return this.http.get<PaginatedResponse<RankingEntry>>(
      `${this.baseUrl}/${contestId}/ranking`,
      { params }
    );
  }
}
