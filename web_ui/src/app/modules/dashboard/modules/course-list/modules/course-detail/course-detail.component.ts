import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CourseService } from '../../../../../../helpers/services/course/course.service';
import { CourseI, LearningObject, UpdateLOStatusRequest } from '../../../../../../helpers/services/course/course.interface';
import { MatSidenavModule } from '@angular/material/sidenav';
import { ProgressBarComponent } from './components/progress-bar/progress-bar.component';
import { CellContentComponent } from './components/cell-content/cell-content.component';
import { MatButtonModule } from '@angular/material/button';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { AiAssistantComponent } from '../../../../../../helpers/shared/ai-assistant/ai-assistant.component';
import { DialogPosition, MatDialog } from '@angular/material/dialog';
import { RecordActivityRequest, ViewContentDetails } from '../../../../../../helpers/services/activity/activity.interface';
import { ActivityType } from '../../../../../../helpers/services/activity/activity.enums';
import { ActivityService } from '../../../../../../helpers/services/activity/activity.service';

@Component({
  selector: 'app-course-detail',
  standalone: true,
  imports: [
    MatSidenavModule,
    ProgressBarComponent,
    CellContentComponent,
    MatButtonModule,
    MatToolbarModule,
    MatIconModule,
    MatSnackBarModule,
    AiAssistantComponent
  ],
  templateUrl: './course-detail.component.html',
  styleUrl: './course-detail.component.scss'
})
export class CourseDetailComponent {
  courseDetail!: CourseI;
  cellID: string | null = null;
  activeLo!: LearningObject;

  constructor(
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private courseService: CourseService,
    private snackbar: MatSnackBar,
    private dialog: MatDialog,
    private activityService: ActivityService
  ) {
    this.activatedRoute.params.subscribe((params) => {
      const courseID = params['courseID'];
      if (!courseID) {
        this.router.navigateByUrl('/dashboard');
        return;
      }

      this.cellID = params['cellID'] || null;

      if ((this.courseDetail == null) || (+courseID != this.courseDetail.id)) {
        this.fetchCourse(courseID);
      } else {
        this.updateTitle();
      }

    })
  }

  fetchCourse(courseID: string) {
    this.courseService.getCourseDetail(courseID).subscribe((res) => {
      this.courseDetail = res;

      this.courseDetail.learning_objects.forEach((lo, idx) => {
        if (lo.completed_on != null) {
          if (idx < this.courseDetail.learning_objects.length - 1) {
            this.cellID = this.courseDetail.learning_objects[idx + 1].object_id;
            return
          }
        }
      })

      if (this.cellID == null) {
        this.navigateToCellID(this.courseDetail.learning_objects[0].object_id);
      } else {
        this.navigateToCellID(this.cellID);
      }

      this.updateTitle();
    })
  }

  updateTitle() {
    const lo = this.courseDetail.learning_objects.find(lo => lo.object_id == this.cellID);
    if (lo) {
      this.activeLo = lo;
    }
  }

  next() {
    if (!this.cellID) { return }
    const currentLOIdx = this.courseDetail.learning_objects.findIndex(x => x.object_id === this.cellID);

    const nextIndex = currentLOIdx + 1;
    let lastLO = false;

    if (currentLOIdx == this.courseDetail.learning_objects.length - 1) {
      lastLO = true;
    } else if (nextIndex > this.courseDetail.learning_objects.length - 1) {
      return
    }

    if (!lastLO) {
      this.saveViewContentActivity(this.courseDetail.learning_objects[nextIndex].object_id, 1);

      if (this.courseDetail.learning_objects[currentLOIdx].completed_on != null) {
        this.navigateToCellID(this.courseDetail.learning_objects[nextIndex].object_id);
        return;
      }
    }

    const now = new Date().toISOString().split('.')[0] + "Z";

    const updateRequest: UpdateLOStatusRequest[] = [
      {
        id: this.courseDetail.learning_objects[currentLOIdx].id,
        completed_on: now
      }
    ];

    if (!lastLO) {
      updateRequest.push(
        {
          id: this.courseDetail.learning_objects[nextIndex].id,
          started_on: now
        }
      );
    }

    this.courseService.updateLOStatus(updateRequest).subscribe((_) => {
      this.snackbar.open(`Congratulations! ${this.courseDetail.learning_objects[currentLOIdx].object_id} completed.`)

      this.courseDetail.learning_objects[currentLOIdx].completed_on = now;

      if (!lastLO) {
        this.navigateToCellID(this.courseDetail.learning_objects[nextIndex].object_id);
        this.courseDetail.learning_objects[nextIndex].started_on = now;
      }
    })
  }

  previous() {
    if (!this.cellID) { return }
    const currentLOIdx = this.courseDetail.learning_objects.findIndex(x => x.object_id === this.cellID);

    const previousIndex = currentLOIdx - 1;

    if (previousIndex < 0) {
      return
    }


    this.saveViewContentActivity(this.courseDetail.learning_objects[previousIndex].object_id, 1);
    this.navigateToCellID(this.courseDetail.learning_objects[previousIndex].object_id);
  }

  navigateToCellID(cellID: string) {
    this.router.navigateByUrl(`/dashboard/courses/learn/${this.courseDetail.id}/${cellID}`, {
      replaceUrl: true
    });
  }

  openAssistantDialog(): void {
    const position: DialogPosition = {
      bottom: '0',
      right: '64px'
    };
    const dialogRef = this.dialog.open(AiAssistantComponent, {
      data: {
        courseId: this.courseDetail.id,
        lo: this.activeLo.object_id
      },
      position,
      height: '600px',
      width: '400px'
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed');
    });
  }

  saveViewContentActivity(cellID: string, delta = -1) {
    const detail: ViewContentDetails = {
      viewed_cell: cellID
    }

    if (delta != -1) {
      detail.movement = delta === 1 ? 'next' : 'previous';
    }

    const request: RecordActivityRequest = {
      activity_type: ActivityType.ViewContent,
      course: this.courseDetail.id,
      details: detail
    };

    this.activityService.saveActivity(request).subscribe();
  }
}
