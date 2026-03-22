import { Routes } from '@angular/router';
import { ContestListComponent } from './features/contests/contest-list/contest-list.component';
import { NotFound } from './features/not-found/not-found';

export const routes: Routes = [
  { path: '', component: ContestListComponent },
  { path: '404', component: NotFound },
  { path: '**', redirectTo: '/404' }
];