import { Component } from '@angular/core';
import { FormGroup, Validators, FormControl} from '@angular/forms';

import {MatDialog, MAT_DIALOG_DATA, MatDialogModule} from '@angular/material/dialog';

import { LightningService } from '../lightning.service';
import { User } from '../user';

import { GenericResponseDialogComponent } from '../generic-response-dialog/generic-response-dialog.component';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent {

  constructor(public lightningService: LightningService, public dialog: MatDialog) { }

  profile_user_json = {};
  public member = false;

  user: User = {
    id: 0,
    title: 'Profile User',
    emailvalidated: false,
    admin: false,
    developer: false
  };


  title = new FormControl('');
  developer = new FormControl('');

  ngOnInit(): void {
    console.log('profile init');
    //this.title.setValue(this.lightningService.user['title']);
    this.getUserData();

  }

  getUserData = async () => {
    if (localStorage.getItem("token") === null) {
      console.log('profile - no access token');
    }
    else
    {
      const response = await fetch(this.lightningService.apiUrl + '/users/data', {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      const result = await response.json();
      console.log(result);
      console.log(result.user); 
      console.log(result.status); 
      if (result.status == "401")
      {
        this.lightningService.requestLogin();
      }
      if (result.user) {
        console.log('found user');
        this.user = result.user;
        this.title.setValue(result.user['title']);
        this.developer.setValue(result.user['developer']);

        //this.admin = result.user['admin'];

      }
    }
  }


  updateProfile = async () => {
    console.log('update profile');
    console.log(localStorage.getItem("token"));

    //const location = window.location.hostname; // this works for live
    const location = '13.56.127.211' // hardcoding for now
    const settings = {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({'title':this.title.value,
                              'developer': this.developer.value

      })
    };
    //try {
        const fetchResponse = await fetch(this.lightningService.apiUrl + '/users/profile/update', settings);
        console.log(fetchResponse);
        const data = await fetchResponse.json();
        // TODO - update localstorage with the new profile data
        //const result = await data.json();
        console.log(data);
        //localStorage.setItem('user', JSON.stringify(result.user));

        this.dialog.open(GenericResponseDialogComponent, {
          data: {
            response_message: data['response_message'],
            response_title: data['response_title']
          },
        });

        localStorage.setItem('usertitle', this.title.value || "Lightning User!");

        // we want to do an update at some point, later.
        // doing this here, results in overwriting the actual form data
        this.lightningService.getUserData();

        //this.profile_user_json = result.user;
        return data;
    //} catch (e) {
    //    return e;
    //} 

  }

}
