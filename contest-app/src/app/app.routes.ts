import { Routes } from '@angular/router';
import { ContestListComponent } from './features/contests/contest-list/contest-list.component';
import { NotFound } from './features/not-found/not-found';
import { Login } from './features/auth/login/login';
import { Register } from './features/auth/register/register';
import { ParticipantsPage } from './features/participants/participants-page/participants-page';
import { EvaluationPage } from './features/evaluation/evaluation-page/evaluation-page';
import { CreateContestPage } from './features/create-contest/create-contest-page/create-contest-page';
import { ContestDetailsPage } from './features/contest-details/contest-details-page/contest-details-page';

export const routes: Routes = [
  { path: '', component: ContestListComponent },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'participants', component: ParticipantsPage },
  { path: 'evaluation', component: EvaluationPage },
  { path: 'create-contest', component: CreateContestPage },
  { path: 'contest-details', component: ContestDetailsPage },
  { path: 'contest/:id', component: NotFound },
  { path: '404', component: NotFound },
  { path: '**', redirectTo: '/404' }
];