import { Component } from '@angular/core';
import { Router, ActivatedRoute} from '@angular/router';

import { AuthChallenge } from './authchallenge';

import { LightningService } from '../app/lightning.service';
import { LoginDialogComponent } from '../app/login-dialog/login-dialog.component'

import {MatDialog, MAT_DIALOG_DATA, MatDialogModule} from '@angular/material/dialog';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'unlockd-webclient';
  qrcodesrc = '';
  loginComplete = false;
  loginButtonVisible = false;
  logoutButtonVisible = false;
  public userTitle = "Lightning User";
  authchall: AuthChallenge | undefined;
  public user = this.lightningService.user;
  public admin = false;

  constructor(public lightningService: LightningService, private dialog: MatDialog, private router: Router) { }

  ngOnInit(): void {
    if (localStorage.getItem("token") === null) {
      this.loginButtonVisible = true;
      this.logoutButtonVisible = false;
    }
    else
    {
      this.loginButtonVisible = false;
      this.logoutButtonVisible = true;
    }

    if (localStorage.getItem("usertitle") === null) {
      console.log('usertitle not found in localstorage');
    }
    else 
    {
      this.userTitle = localStorage.getItem("usertitle") || "";
    }

    if (localStorage.getItem("admin") === null) {
      console.log('admin not found in localstorage');
    }
    else 
    {
      var admin_str = localStorage.getItem("admin") || "";
      if (admin_str == 'true')
      {
        this.admin = true;
      }
      else
      {
        this.admin = false;
      }
      
    }

    // Subscribe to the login user in lightning service to know if we need to run auth again
    this.lightningService.login_user.subscribe( (value) => {
      console.log('lightning service requesting re-authentication');
      // Only do this if there is an old token in localstorage
      if (localStorage.getItem('token'))
      {
        console.log('found an old token');
        this.loginChallenge();
      }
    });

    // subscribe to the user in lightning service for changes 
    this.lightningService.sub_user.subscribe( (value) => {
      console.log('lightning service user changed');
      console.log(this.lightningService.user);
      //console.log(this.lightningService.role);
      this.user = this.lightningService.user;
      this.userTitle = this.lightningService.user.title;
      //this.role = this.lightningService.role;
      //console.log(this.role.view_admin_interface.valueOf());
    });
    // subscribe to UI changes
    this.lightningService.showCloseDialog.subscribe( (value) => {
      console.log('show close dialog');
      this.closeDialog();
      this.loginButtonVisible = false;
      this.logoutButtonVisible = true;
    });

    this.dialog.afterAllClosed.subscribe(data=>{
      console.log("data returned from mat-dialog-close is ",data);
      this.lightningService.signinActive = false;
  })

  }

  loginChallenge() {
    console.log('App Component Login pressed');

    this.lightningService.loginChallenge()
    .subscribe(authchall => {
      this.authchall = authchall;
      this.qrcodesrc = 'https://unlockd.gg/api/generate_qr/' + authchall.lnurl;

      // open the login dialog
      this.dialog.open(LoginDialogComponent, {
        data: {
          lnurl: this.authchall,
          qrcodesrc: this.qrcodesrc
        },
      });
    });
  }

  

  closeDialog () {
    this.dialog.closeAll();
  }

  logout () {
    this.lightningService.doLogout();
    this.loginButtonVisible = true;
    this.logoutButtonVisible = false;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    //localStorage.removeItem('role');
    this.router.navigate(['']);
  }



}
