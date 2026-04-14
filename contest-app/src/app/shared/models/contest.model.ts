// Пользователь
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'organizer' | 'expert';
  created_at?: string;
}

// Конкурс (хакатон)
export interface Contest {
  id: number;
  name: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  logo_path: string | null;
  is_finished: boolean;
  created_at: string;
  organizer_id: number;
  organizer?: User;
}

// Команда участника
export interface Team {
  id: number;
  name: string;
  description: string | null;
  contest_id: number;
  created_at: string;
}

// Критерий оценивания
export interface Criterion {
  id: number;
  name: string;
  description: string | null;
  max_score: number;
  contest_id: number;
}

// Оценка эксперта
export interface Grade {
  id: number;
  value: number;
  comment: string | null;
  created_at: string;
  updated_at: string;
  expert_id: number;
  team_id: number;
  criterion_id: number;
}

// Элемент рейтинга (результат ранжирования команд)
export interface RankingEntry {
  rank: number;
  team_id: number;
  team_name: string;
  total_score: number;
  grades_count: number;
}

// Назначение эксперта на конкурс
export interface ContestExpert {
  id: number;
  contest_id: number;
  user_id: number;
  assigned_at: string;
  user?: User;
}

// Пагинация
export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Ответы API
export interface ApiResponse<T> {
  status: string;
  message?: string;
  [key: string]: any; // Позволяет динамические поля (teams, criteria, grades и т.д.)
}

export interface PaginatedResponse<T> extends ApiResponse<T> {
  pagination: PaginationMeta;
  [key: string]: any; // Позволяет динамические поля (teams, criteria, grades и т.д.)
}

export interface AuthResponse {
  status: string;
  access_token?: string;
  user: User;
  message?: string;
  redirect_url?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  role: 'organizer' | 'expert';
}

// Данные для создания конкурса
export interface CreateContestData {
  name: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  logo_path?: string;
}

// Данные для обновления конкурса
export interface UpdateContestData {
  name?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  logo_path?: string;
}

// Данные для создания команды
export interface CreateTeamData {
  name: string;
  description?: string;
}

// Данные для создания критерия
export interface CreateCriterionData {
  name: string;
  description?: string;
  max_score?: number;
}

// Данные для создания оценки
export interface CreateGradeData {
  team_id: number;
  criterion_id: number;
  value: number;
  comment?: string;
}

// Данные для обновления оценки
export interface UpdateGradeData {
  value?: number;
  comment?: string;
}

// Статус голосования
export interface VotingStatus {
  total_experts: number;
  graded_experts: number;
  total_teams: number;
  total_criteria: number;
  total_grades: number;
  expected_grades: number;
  completion_percentage: number;
}

// Статус голосования для конкретной команды
export interface TeamVotingStatus {
  team_id: number;
  team_name: string;
  total_experts: number;
  graded_experts: number;
  graded_count: number;
  expected_count: number;
  completion_percentage: number;
}
