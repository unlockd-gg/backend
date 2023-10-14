import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, of, Subject } from 'rxjs';
import { catchError, map, tap, delay } from 'rxjs/operators';

//import { requestProvider } from "webln";

import { User } from './user';
//import { Role } from './role';
import { AuthChallenge } from './authchallenge';

@Injectable({
  providedIn: 'root'
})
export class LightningService {

  // TODO:  Fix this so it's not hardcoded to our local dev environment
  public apiUrl = 'https://unlockd.gg/api';  // URL to web api - in quotes - no trailing slash:  'http://54.176.48.9'
  public lappUrl = 'http://localhost/lapp';  // URL to lightning  api - in quotes - no trailing slash:  'http://54.176.48.9'
  public authChallengeResponse = '';
  public weblnButtonUrl = '';
  public emailaddress = '';
  public auth_token = '';
  public signinActive = false;
  signinEmailValidation = false;
  showEmailPopUp: Subject<boolean> = new Subject<boolean>();
  showEmailValidationPopUp: Subject<boolean> = new Subject<boolean>();
  signInComplete = false;
  showCloseDialog: Subject<boolean> = new Subject<boolean>();

  // keep track of fake pubkey in the case of a non-lighting login
  fake_pub_key = "";

  user: User = {
    id: 0,
    title: 'Service Test User',
    emailvalidated: false,
    admin: false,
    developer: false
  };



  sub_user: Subject<boolean> = new Subject<boolean>();
  login_user: Subject<boolean> = new Subject<boolean>();

  constructor(
    private http: HttpClient
  ) { }

  /** GET login challenge from the server */
  // this is just a lnurl string
  loginChallenge():  Observable<AuthChallenge> {
    console.log('Lightning Service Login Challenge');
    const auth_url = `${this.lappUrl}/do-login`;
    return this.http.get<AuthChallenge>(auth_url)
    .pipe(
      tap( // Log the result or error
      {
        //next: (data) => this.log(data['lnurl']), // this works
        //next: (data) => this.authChallengeResponse = data['lnurl'], // this too
        next: (data) => this.registerACR( data['lnurl'] ),
        error: (error) => this.log('error')
      }
      )
    );
  }

  registerACR(aCR: string) {
    console.log('register ACR');
    console.log(aCR);
    this.authChallengeResponse = aCR;
    this.signinActive = true;
    this.startPolling();
  }

  getLnUrl() {
    console.log('Lightning Service Get lnUrl');
    return this.authChallengeResponse;
  }

  pollSignedIn = async () => {
    const response = await fetch(this.apiUrl + '/me?bech_32_url=' + this.authChallengeResponse);
    const result = await response.json();
    console.log(result);
    console.log(result.user); 
    if (result.auth_token)
    {
      console.log('found auth_token');

      // User can still be none here.  Check first.
      if (result.user) {
        console.log('found user');
        this.user = result.user;
        this.update_user(result.user['title'], result.user['address'], result.user['admin']);
      }
      
      this.auth_token = result.auth_token;
      localStorage.setItem('token', result.auth_token);
      
      //localStorage.setItem('user', JSON.stringify(result.user));

      this.signinActive = false;

      if (result.do_email_validation) {
        console.log('do email validation');
        this.showEmailPopUp.next(true);
      } 
      else 
      {
        console.log('no email validation - close dialog');
        this.showCloseDialog.next(true);
        this.getUserData();
      }
    }
    return result.user != null;
  }

  checkSignedIn = async () => {
    const result = await this.pollSignedIn();
    console.log(result);

    if (!result) {
        this.startPolling();
    } else {
        console.log('login success');
        // window.location.reload();
        this.signInComplete = true;
    }
  }

  startPolling() {
      if(!this.signinActive)
      {
        return;
      }
      window.setTimeout( this.checkSignedIn, 1000);
  }

  async startEmailValidation(emailaddress: string)
  {
    console.log('lightning.service startEmailValidation')
    this.emailaddress = emailaddress;
    const response = await fetch(this.apiUrl + '/user/email/' + emailaddress + '/start', {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.auth_token}`
      }
    });
    this.showEmailValidationPopUp.next(true);
    const result = await response.json();
  }

  async validateEmail(emailaddress: string, verificationcode: string)
  {
    console.log('lightning.service startEmailValidation')
    this.emailaddress = emailaddress;
    const response = await fetch(this.apiUrl + '/user/email/' + emailaddress + '/validate/' + verificationcode, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.auth_token}`
      }
    });
    this.showEmailValidationPopUp.next(true);
    const result = await response.json();

    if (result['success'] == true) {
      console.log('success true');

      // get user data again.
      this.getUserData();
      this.signinActive = false;
      this.showCloseDialog.next(true);

    }
  }

  async startEmailValidationNoLightning(emailaddress: string)
  {
    console.log('lightning.service startEmailValidation without lightning')
    this.emailaddress = emailaddress;
    const response = await fetch(this.apiUrl + '/user/email/' + emailaddress + '/start-no-lightning' );
    this.showEmailValidationPopUp.next(true);
    const result = await response.json();
    this.fake_pub_key = result['publickey'];
  }

  async validateEmailNoLightning(emailaddress: string, verificationcode: string)
  {
    console.log('lightning.service startEmailValidation without lightning')
    this.emailaddress = emailaddress;
    const response = await fetch(this.apiUrl + '/user/email/' + emailaddress + '/validate-no-lightning/' + verificationcode + "/" + this.fake_pub_key );

    this.showEmailValidationPopUp.next(true);
    const result = await response.json();

    if (result['success'] == true) {
      console.log('success true');
      // save the JWT token here.
      this.auth_token = result.auth_token;
      localStorage.setItem('token', result.auth_token);

      this.signinActive = false;
      this.showCloseDialog.next(true);

    }
  }

  update_user(title: string, address: string, admin: boolean )
  {
    console.log('lightning service update user');
    this.user['title'] = title;
    this.user['admin'] = admin;
    this.sub_user.next(true);
  }

  getUserData = async () => {
    const response = await fetch(this.apiUrl + '/users/data', {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem("token")}`
      }
    });
    const result = await response.json();
    console.log(result);
    console.log(result.user); 
    if (result.user) {
      console.log('found user');
      this.user = result.user;
      this.sub_user.next(true);
    }
    else
    {
      this.login_user.next(true);
    }
    if (result.role) {
      console.log('found role');
      console.log(result.role);
      //this.role = result.role;

      // add the role to localstorage
      //localStorage.setItem('role', JSON.stringify(result.role));
    }
    return {User: this.user};
  }

  doLogout() {
  }

  public requestLogin( ) {
    this.login_user.next(true);
    this.user = {
      id: 0,
      title: 'Service Test User',
      emailvalidated: false,
      admin: false,
      developer: false
    };
  }




  /** Log */
  private log(message: string) {
    console.log(message);
    //this.messageService.add(`HeroService: ${message}`);
  }
}
