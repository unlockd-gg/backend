import { Component } from '@angular/core';

import { LightningService } from '../../lightning.service';

@Component({
  selector: 'app-users',
  templateUrl: './users.component.html',
  styleUrls: ['./users.component.css']
})
export class UsersComponent {
  constructor(private lightningService: LightningService) { }
  public user_list = [];

  ngOnInit(): void {
    console.log('admin users init');
    //this.title.setValue(this.lightningService.user['title']);
    this.getUserData();

  }

  getUserData = async () => {
  const response = await fetch(this.lightningService.apiUrl + '/users/', {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem("token")}`
      }
    });
    const result = await response.json();
    console.log(result);

    this.user_list = result;

  }

}
