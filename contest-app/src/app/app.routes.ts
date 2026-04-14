import { Routes } from '@angular/router';
import { ContestListComponent } from './features/contests/contest-list/contest-list.component';
import { NotFound } from './features/not-found/not-found';
import { Login } from './features/auth/login/login';
import { Register } from './features/auth/register/register';
import { ParticipantsPage } from './features/participants/participants-page/participants-page';
import { EvaluationPage } from './features/evaluation/evaluation-page/evaluation-page';
import { CreateContestPage } from './features/create-contest/create-contest-page/create-contest-page';
import { ContestDetailsPage } from './features/contest-details/contest-details-page/contest-details-page';
import { ExpertAccountPage } from './features/account/expert-account/expert-account-page';
import { OrganizerAccountPage } from './features/account/organizer-account/organizer-account-page';
import { accountRedirectGuard, organizerGuard, expertGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', component: ContestListComponent },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'contest/:id', component: ContestDetailsPage },
  { path: 'participants', component: ParticipantsPage },
  { path: 'evaluation', component: EvaluationPage, canActivate: [expertGuard] },
  { path: 'create-contest', component: CreateContestPage, canActivate: [organizerGuard] },
  { path: 'account', canActivate: [accountRedirectGuard], component: ContestListComponent },
  { path: 'account/expert', component: ExpertAccountPage, canActivate: [expertGuard] },
  { path: 'account/organizer', component: OrganizerAccountPage, canActivate: [organizerGuard] },
  { path: '404', component: NotFound },
  { path: '**', redirectTo: '/404' }
];
