import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import {
  Contest,
  UpdateContestData,
  PaginatedResponse,
  ApiResponse,
  VotingStatus,
  ExpertContestsResponse,
} from '../shared/models/contest.model';

@Injectable({
  providedIn: 'root',
})
export class ContestService {
  private readonly apiUrl = '/api/contests';

  constructor(private http: HttpClient) {}

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

  generateAccessKey(contestId: number): Observable<any> {
    return this.http.post(`/api/experts/contests/${contestId}/access-key/generate`, {});
  }

  getById(contestId: number): Observable<ApiResponse<Contest>> {
    return this.http.get<ApiResponse<Contest>>(`${this.apiUrl}/${contestId}`);
  }

  create(data: FormData): Observable<ApiResponse<Contest>> {
    return this.http.post<ApiResponse<Contest>>(this.apiUrl, data);
  }

  update(
    contestId: number,
    data: UpdateContestData
  ): Observable<ApiResponse<Contest>> {
    return this.http.put<ApiResponse<Contest>>(`${this.apiUrl}/${contestId}`, data);
  }

  delete(contestId: number): Observable<ApiResponse<Contest>> {
    return this.http.delete<ApiResponse<Contest>>(`${this.apiUrl}/${contestId}`);
  }

  joinContestByAccessKey(contestId: number, accessKey: string): Observable<any> {
    return this.http.post(`/api/experts/contests/${contestId}/join`, {
      access_key: accessKey.trim()
    });
  }

  finalize(contestId: number): Observable<ApiResponse<Contest>> {
    return this.http.post<ApiResponse<Contest>>(
      `${this.apiUrl}/${contestId}/finalize`,
      {}
    );
  }

  getVotingStatus(contestId: number): Observable<ApiResponse<VotingStatus>> {
    return this.http.get<ApiResponse<VotingStatus>>(
      `${this.apiUrl}/${contestId}/voting-status`
    );
  }

  getMyExpertContests(): Observable<ExpertContestsResponse> {
    return this.http.get<ExpertContestsResponse>('/api/experts/me/contests');
  }
}

