import { Routes } from '@angular/router';
import { ContestListComponent } from './features/contests/contest-list/contest-list.component';
import { NotFound } from './features/not-found/not-found';
import { Login } from './features/auth/login/login';
import { Register } from './features/auth/register/register';

export const routes: Routes = [
  { path: '', component: ContestListComponent },
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'contest/:id', component: NotFound },
  { path: '404', component: NotFound },
  { path: '**', redirectTo: '/404' }
];