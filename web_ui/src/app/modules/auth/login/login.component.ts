import { Component } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';

import { MatFormFieldModule } from '@angular/material/form-field'
import { MatInputModule } from '@angular/material/input'
import { MatButtonModule } from '@angular/material/button'
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar'

import { AuthService } from '../services/auth.service';
import { LoginError, LoginRequest } from '../services/auth.interface';
import { HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatSnackBarModule
  ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  loginForm = new FormGroup({
    username: new FormControl(),
    password: new FormControl()
  })

  constructor(
    private authService: AuthService,
    private snackbar: MatSnackBar,
    private router: Router
  ) {

  }

  login() {
    if(this.loginForm.invalid) {
      return;
    }
    this.authService.login(this.loginForm.value as LoginRequest).subscribe((resp) => {
      this.snackbar.open("Logged In!!");

      this.router.navigateByUrl('/dashboard');
    }, (err: HttpErrorResponse) => {
      const error = (err.error) as LoginError;

      if (error?.detail) {
        this.snackbar.open(error.detail);
      }
    })
  }
}
