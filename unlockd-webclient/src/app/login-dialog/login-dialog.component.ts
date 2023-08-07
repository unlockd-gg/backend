import {Component, Inject, Input, NgModule} from '@angular/core';
//import { BrowserModule } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { LightningService } from '../lightning.service';
import {MatDialog, MAT_DIALOG_DATA, MatDialogModule} from '@angular/material/dialog';
//import { FormControl } from '@angular/forms';
import { FormsModule, ReactiveFormsModule  } from '@angular/forms';
import {NgIf} from '@angular/common';
import {MatButtonModule} from '@angular/material/button';

import { LoginDialogData } from '../login-dialog-data';

@Component({
  selector: 'app-login-dialog',
  templateUrl: './login-dialog.component.html',
  standalone: true,
  imports: [ CommonModule, MatDialogModule, NgIf, MatButtonModule, FormsModule, ReactiveFormsModule],
})
export class LoginDialogComponent {
  
  constructor(@Inject(MAT_DIALOG_DATA) public data: LoginDialogData, private lightningService: LightningService) {
    
  }

  ngOnInit(): void {
    // subscribe to the user in lightning service for changes 
    this.lightningService.showEmailPopUp.subscribe( (value) => {
      console.log('show email popup');
      this.signinEmailValidationStart = true;
      this.signinLightning = false;
    });
    // subscribe to the user in lightning service for changes
    this.lightningService.showEmailValidationPopUp.subscribe( (value) => {
      console.log('show Email Validation popup');
      this.signinEmailValidationCodeStart = true;
      this.signinEmailValidationStart = false;
    });



    
 }
  //qrcodesrc = this.lightningService.getLnUrl();
  qrcodesrc = 'https://unlockd.gg/api/generate_qr/' + this.lightningService.getLnUrl();
  weblnurl = 'lightning:' + this.lightningService.getLnUrl();

  // Multi-stage dialog
  // Stage1 = lightninglogin
  signinLightning = true;

  loginmodebrowser = true;
  loginmodeQR = false;
  loginmodeEmail = false;


  // Stage 2 - email address entry
  signinEmailValidationStart = false;
  signinEmailValidation = false;
  emailaddress = '';
  // Stage 3 - Email validation
  signinEmailValidationCodeStart = false;
  emailaddressverificationcode = '';

  changeLoginMode(loginMode: string) {
    if (loginMode == "browser") {
      this.loginmodebrowser = true;
      this.loginmodeQR = false;
      this.loginmodeEmail = false;
    } else if (loginMode == "qrcode")  {
      this.loginmodebrowser = false;
      this.loginmodeQR = true;
      this.loginmodeEmail = false;
    } else {
      this.loginmodebrowser = false;
      this.loginmodeQR = false;
      this.loginmodeEmail = true;
    }
  }

  submitEmail() {
    console.log(this.emailaddress);
    this.lightningService.startEmailValidation(this.emailaddress);
  }

  validateEmail() {
    console.log(this.emailaddress);
    console.log(this.emailaddressverificationcode)
    this.lightningService.validateEmail(this.emailaddress, this.emailaddressverificationcode);
  }

  submitEmailNoLightning() {
    console.log(this.emailaddress);
    this.lightningService.startEmailValidationNoLightning(this.emailaddress);

    // Turn off the mode selection buttons
    this.signinLightning = false;
  }
  validateEmailNoLightning() {
    console.log(this.emailaddress);
    console.log(this.emailaddressverificationcode)
    this.lightningService.validateEmailNoLightning(this.emailaddress, this.emailaddressverificationcode);
  }

}
