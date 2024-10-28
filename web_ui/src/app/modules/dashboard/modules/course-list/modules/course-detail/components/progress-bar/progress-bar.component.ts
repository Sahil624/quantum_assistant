import { Component, Input } from '@angular/core';
import { CourseI, LearningObject } from '../../../../../../../../helpers/services/course/course.interface';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute, Router } from '@angular/router';
import { DatePipe } from '@angular/common';
import { MatTooltipModule } from '@angular/material/tooltip';
import { RecordActivityRequest, ViewContentDetails } from '../../../../../../../../helpers/services/activity/activity.interface';
import { ActivityType } from '../../../../../../../../helpers/services/activity/activity.enums';
import { ActivityService } from '../../../../../../../../helpers/services/activity/activity.service';

@Component({
  selector: 'app-progress-bar',
  standalone: true,
  imports: [
    MatSidenavModule,
    MatProgressBarModule,
    MatListModule,
    MatIconModule,
    DatePipe,
    MatTooltipModule
  ],
  templateUrl: './progress-bar.component.html',
  styleUrl: './progress-bar.component.scss'
})
export class ProgressBarComponent {
  @Input() course!: CourseI;
  activeCell!: string;

  constructor(
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private activityService: ActivityService
  ) {
    this.activatedRoute.params.subscribe((param) => {
      this.activeCell = param['cellID']
    })
  }

  navigateToCell(cell: LearningObject) {
    this.saveViewContentActivity(cell.object_id);
    this.router.navigateByUrl(`/dashboard/courses/learn/${this.course.id}/${cell.object_id}`);
  }

  saveViewContentActivity(cellID: string) {
    const detail: ViewContentDetails = {
      viewed_cell: cellID,
      movement: 'skip'
    }

    const request: RecordActivityRequest = {
      activity_type: ActivityType.ViewContent,
      course: this.course.id,
      details: detail
    };

    this.activityService.saveActivity(request).subscribe();
  }

  get completedPercent() {
    const percent = (this.course.learning_objects.filter(x=> x.completed_on!=null).length/this.course.learning_objects.length) * 100;
    return percent.toFixed(1);
  }
}
