import { Component } from '@angular/core';
import { FormGroup, Validators, FormControl} from '@angular/forms';
import { Router, ActivatedRoute} from '@angular/router';

import { LightningService } from '../../lightning.service';

@Component({
  selector: 'app-user-detail',
  templateUrl: './user-detail.component.html',
  styleUrls: ['./user-detail.component.css']
})
export class UserDetailComponent {
  constructor(private lightningService: LightningService, private route: ActivatedRoute, private router: Router) { }

  userid ="";
  public user = {};

  // load the role into the form 
  ngOnInit(): void {
    console.log('user detail init');
    
    this.route.paramMap.subscribe((params) => {
      console.log('user data params changed')
      this.userid = params.get('userid') || "";
      //this.role = this.productService.getProduct(this.id);
      this.getUserData();
     

    });
  }

  getUserData = async () => {
    if (localStorage.getItem("token") === null) {
      console.log('user data - no access token');
    }
    else
    {
      const response = await fetch(this.lightningService.apiUrl + '/admin/users/' + this.userid, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      const result = await response.json();
      console.log(result);
      console.log(result.user); 
      if (result.status == "401")
      {
        this.lightningService.requestLogin();
      }
      if (result.user) {
        console.log('found user');
        console.log(result.user['title']);
        console.log(result.user['description']);
        
        this.developer.setValue(result.user['developer']);
        this.user = result.user;
        this.title.setValue(result.user['title']);
        this.emailaddress.setValue(result.user['emailaddress']);


      }
    }
  }

  title = new FormControl('');

  emailaddress = new FormControl('');
  developer = new FormControl('');


  
  updateUser = async () => {
    console.log('update user');
    console.log(localStorage.getItem("token"));

    //const location = window.location.hostname; // this works for live
    //const location = '13.56.127.211' // hardcoding for now
    const settings = {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({'_id':this.userid,
         'title':this.title.value,
         'emailaddress': this.emailaddress.value,
         'developer': this.developer.value,

      
                            })
    };
    //try {
        const fetchResponse = await fetch(this.lightningService.apiUrl + '/admin/users/' + this.userid + '/update', settings);
        console.log(fetchResponse);
        const data = await fetchResponse.json();
        // we dont have to do anything special here.  redirect?
        this.router.navigate(['admin-users']);

        console.log(data);

        return data;
    //} catch (e) {
    //    return e;
    //} 

  }


  deleteUser = async () => {
    console.log('delete user');
    console.log(localStorage.getItem("token"));

    //const location = window.location.hostname; // this works for live
    //const location = '13.56.127.211' // hardcoding for now
    const settings = {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({'_id':this.userid})
    };
    //try {
        const fetchResponse = await fetch(this.lightningService.apiUrl + '/admin/users/' + this.userid + '/delete', settings);
        console.log(fetchResponse);
        const data = await fetchResponse.json();
        // we dont have to do anything special here.  redirect?
        this.router.navigate(['admin-users']);
        
        console.log(data);

        return data;
    //} catch (e) {
    //    return e;
    //} 

  }
}
