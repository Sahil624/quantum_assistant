import { Component } from '@angular/core';
import { CourseService } from '../../../../helpers/services/course/course.service';
import { CourseI, MyCourseResponse } from '../../../../helpers/services/course/course.interface';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-course-list',
  standalone: true,
  imports: [
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    RouterModule
  ],
  templateUrl: './course-list.component.html',
  styleUrl: './course-list.component.scss'
})
export class CourseListComponent {
  myCourses!: MyCourseResponse

  constructor(
    private courseService: CourseService
  ) {
    this.getMyCourses();
  }

  getMyCourses() {
    this.courseService.getMyCourses().subscribe((res) => {
      this.myCourses = res;
    })
  }

  getTimeDetails(course: CourseI) {
    let totalTime = 0;
    let isStarted = false;
    course.learning_objects.forEach((lo) => {
      totalTime += +(lo.metadata?.cell_estimated_time || 0);
      if (!isStarted) {
        isStarted = lo.started_on != null;
      }
    })

    return {
      totalTime, isStarted
    }
  }
}
