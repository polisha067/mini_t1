import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Team,
  CreateTeamData,
  PaginatedResponse,
  ApiResponse,
} from '../shared/models/contest.model';

@Injectable({
  providedIn: 'root',
})
export class TeamService {
  private readonly baseUrl = '/api/contests';

  constructor(private http: HttpClient) {}

  /**
   * Получить список команд конкурса с пагинацией
   */
  getList(
    contestId: number,
    page: number = 1,
    perPage: number = 10
  ): Observable<PaginatedResponse<Team>> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('per_page', perPage.toString());

    return this.http.get<PaginatedResponse<Team>>(
      `${this.baseUrl}/${contestId}/teams`,
      { params }
    );
  }

  /**
   * Получить детали команды по ID
   */
  getById(teamId: number): Observable<ApiResponse<Team>> {
    return this.http.get<ApiResponse<Team>>(`/api/teams/${teamId}`);
  }

  /**
   * Создать команду в конкурсе (только organizer)
   */
  create(
    contestId: number,
    data: CreateTeamData
  ): Observable<ApiResponse<Team>> {
    return this.http.post<ApiResponse<Team>>(
      `${this.baseUrl}/${contestId}/teams`,
      data
    );
  }

  /**
   * Обновить команду (только organizer конкурса)
   */
  update(teamId: number, data: CreateTeamData): Observable<ApiResponse<Team>> {
    return this.http.put<ApiResponse<Team>>(`/api/teams/${teamId}`, data);
  }

  /**
   * Удалить команду (только organizer конкурса)
   */
  delete(teamId: number): Observable<ApiResponse<Team>> {
    return this.http.delete<ApiResponse<Team>>(`/api/teams/${teamId}`);
  }
}
