import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomepageComponent } from './homepage/homepage.component'
import { CostsComponent } from './costs/costs.component'
import { FaqComponent } from './faq/faq.component'

import { ProfileComponent } from './profile/profile.component'
import { TransactionsComponent } from './transactions/transactions.component'

import { UsersComponent } from './admin/users/users.component'
import { UserDetailComponent } from './admin/user-detail/user-detail.component'

import { GamesComponent } from './developer/games/games.component'

const routes: Routes = [
  { path: '', component: HomepageComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'costs', component: CostsComponent },
  { path: 'faq', component: FaqComponent },
  { path: 'transactions', component: TransactionsComponent },
  { path: 'admin/users', component: UsersComponent },
  { path: 'admin/users/:userid', component: UserDetailComponent },
  { path: 'developer/games', component: GamesComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

