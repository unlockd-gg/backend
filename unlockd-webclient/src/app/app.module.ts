import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatFormFieldModule} from '@angular/material/form-field';


import {MatDialogModule} from '@angular/material/dialog';
import {MatButtonModule} from '@angular/material/button';
import {MatIconModule} from '@angular/material/icon';
import {MatMenuModule} from '@angular/material/menu';
import {MatDatepickerModule} from '@angular/material/datepicker';
import {MatNativeDateModule} from '@angular/material/core';
import { MatCheckboxModule } from '@angular/material/checkbox';
import {MatListModule} from '@angular/material/list';
import {MatGridListModule} from '@angular/material/grid-list';
import { LoginDialogComponent } from './login-dialog/login-dialog.component';
import { ProfileComponent } from './profile/profile.component';
import { GenericResponseDialogComponent } from './generic-response-dialog/generic-response-dialog.component';
import { HomepageComponent } from './homepage/homepage.component';
import { TransactionsComponent } from './transactions/transactions.component';
import { UsersComponent } from './admin/users/users.component';
import { UserDetailComponent } from './admin/user-detail/user-detail.component';
import { GamesComponent } from './developer/games/games.component';
import { CostsComponent } from './costs/costs.component';
import { FaqComponent } from './faq/faq.component';

@NgModule({
  declarations: [
    AppComponent,
    ProfileComponent,
    GenericResponseDialogComponent,
    HomepageComponent,
    TransactionsComponent,
    UsersComponent,
    UserDetailComponent,
    GamesComponent,
    CostsComponent,
    FaqComponent,
    //LoginDialogComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatNativeDateModule,
    MatDatepickerModule,
    MatCheckboxModule,
    MatListModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule, MatSelectModule, MatInputModule, MatGridListModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
