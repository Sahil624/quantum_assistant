import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { availableLOUrl, cellDataUrl, myCoursesUrl, updateLOStatusUrl } from '../../urls';
import { AvailableLOResponse, CellDataResponse, CourseI, CreateCourseRequest, MyCourseResponse, UpdateLOStatusRequest } from './course.interface';

@Injectable({
  providedIn: 'root'
})
export class CourseService {

  constructor(
    private http: HttpClient
  ) { }

  getAvailableLO() {
    return this.http.get<AvailableLOResponse>(availableLOUrl);
  }

  getMyCourses() {
    return this.http.get<MyCourseResponse>(myCoursesUrl);
  }

  getCourseDetail(courseID :string) {
    return this.http.get<CourseI>(myCoursesUrl + courseID + '/')
  }

  fetchCellData(cellID: string) {
    return this.http.get<CellDataResponse>(cellDataUrl + cellID + '/')
  }

  updateLOStatus(request: UpdateLOStatusRequest[]) {
    return this.http.put(updateLOStatusUrl, request);
  }

  createCourse(request: CreateCourseRequest) {
    return this.http.post(myCoursesUrl, request);
  }
}
