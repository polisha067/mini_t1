import { Routes } from '@angular/router';
import { ContestListComponent } from './features/contests/contest-list/contest-list.component';
import { NotFound } from './features/not-found/not-found';
import { Login } from './features/auth/login/login';
import { Register } from './features/auth/register/register';
import { ForgotPassword } from './features/auth/forgot-password/forgot-password';
import { PasswordResetSent } from './features/auth/password-reset-sent/password-reset-sent';
import { ParticipantsPage } from './features/participants/participants-page/participants-page';
import { EvaluationPage } from './features/evaluation/evaluation-page/evaluation-page';
import { CreateContestPage } from './features/create-contest/create-contest-page/create-contest-page';
import { ContestDetailsPage } from './features/contest-details/contest-details-page/contest-details-page';
import { ExpertAccountPage } from './features/account/expert-account/expert-account-page';
import { OrganizerAccountPage } from './features/account/organizer-account/organizer-account-page';
import {
  accountRedirectGuard,
  organizerGuard,
  expertGuard,
  expertEvaluationGuard,
} from './core/guards/auth.guard';
import { ContestCreatedPage } from './features/contest-created/contest-created-page/contest-created-page';

export const routes: Routes = [
  { path: '', component: ContestListComponent },
  { path: 'contest-created', component: ContestCreatedPage },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'forgot-password', component: ForgotPassword },
  { path: 'password-reset-sent', component: PasswordResetSent },
  { path: 'contests/:contestId/participants', component: ParticipantsPage },
  { path: 'contests/:id', component: ContestDetailsPage },
  { path: 'contest/:id', component: ContestDetailsPage },
  { path: 'participants', component: ParticipantsPage },
  {
    path: 'evaluation',
    component: EvaluationPage,
    canActivate: [expertGuard, expertEvaluationGuard],
  },
  { path: 'create-contest', component: CreateContestPage, canActivate: [organizerGuard] },
  { path: 'account', canActivate: [accountRedirectGuard], component: ContestListComponent },
  { path: 'account/expert', component: ExpertAccountPage, canActivate: [expertGuard] },
  { path: 'account/organizer', component: OrganizerAccountPage, canActivate: [organizerGuard] },
  { path: '404', component: NotFound },
  { path: '**', redirectTo: '/404' }
];
