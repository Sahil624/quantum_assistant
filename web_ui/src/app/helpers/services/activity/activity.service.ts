import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { RecordActivityRequest } from './activity.interface';
import { activityUrl } from '../../urls';

@Injectable({
  providedIn: 'root'
})
export class ActivityService {

  constructor(
    private http: HttpClient
  ) { }

  saveActivity(request: RecordActivityRequest) {
    return this.http.post(activityUrl, request);
  }
}
