import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { availableLOUrl, cellDataUrl, downloadNotebookUrl, metaDataUrl, myCoursesUrl, optimizeLOsUrl, updateLOStatusUrl } from '../../urls';
import { AvailableLOResponse, CellDataResponse, CourseI, CreateCourseRequest, MetaDataI, MyCourseResponse, UpdateLOStatusRequest } from './course.interface';
import { catchError, map, Observable, throwError } from 'rxjs';
import { MetaManager } from './meta.model';

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

  optimizeCourse(cellIDs: string[], time: number){
    return this.http.get<string[]>(optimizeLOsUrl, {
      params: {
        learning_object_ids: cellIDs,
        total_time: time || 100000
      }
    })
  }

  getMetaData() {
    return this.http.get<MetaDataI>(metaDataUrl).pipe(
      map((r) => {
        return new MetaManager(r);
      })
    )
  }

  downloadFile(filename: string): Observable<Blob> {
    const headers = new HttpHeaders({
      'Accept': '*/*'
    });

    return this.http.get(downloadNotebookUrl + filename + "/", {
      headers: headers,
      responseType: 'blob',
      observe: 'response'
    }).pipe(
      map(response => {
        const contentType = response.headers.get('Content-Type') || 'application/octet-stream';
        const blob = new Blob([response.body!], { type: contentType });
        return blob;
      }),
      catchError(this.handleError)
    );
  }
  
  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred during download';
    
    if (error.status === 404) {
      errorMessage = 'File not found';
    } else if (error.status === 403) {
      errorMessage = 'Access denied';
    } else if (error.status === 406) {
      errorMessage = 'Content type negotiation failed';
    }
    
    console.error('Download error:', error);
    return throwError(() => new Error(errorMessage));
  }
}
