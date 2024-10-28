import { Component, OnDestroy, QueryList, ViewChildren } from '@angular/core';
import { CourseService } from '../../../../helpers/services/course/course.service';
import { AvailableLOResponse, MetaDataI } from '../../../../helpers/services/course/course.interface';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { DialogPosition, MatDialog } from '@angular/material/dialog';
import { GeneratorConfirmationComponent } from './components/generator-confirmation/generator-confirmation.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { LoTreeComponent } from './components/lo-tree/lo-tree.component';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { ChatConversationComponent } from '../../../../helpers/shared/chat-conversation/chat-conversation.component';
import { MessageI } from '../../../../helpers/services/conversation/conversation.interface';
import { ConversationService } from '../../../../helpers/services/conversation/conversation.service';
import { AssistantType } from '../../../../helpers/services/conversation/conversation.enums';
import { GeneratorAiHelperComponent } from './components/generator-ai-helper/generator-ai-helper.component';
import { MetaManager } from '../../../../helpers/services/course/meta.model';
import { sortLearningObjects } from './loSort';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-generator',
  standalone: true,
  imports: [
    MatExpansionModule,
    MatButtonModule,
    MatIconModule,
    GeneratorConfirmationComponent,
    LoTreeComponent,
    MatFormFieldModule,
    ReactiveFormsModule,
    FormsModule,
    MatInputModule,
    GeneratorAiHelperComponent,
    MatProgressSpinnerModule
  ],
  templateUrl: './generator.component.html',
  styleUrl: './generator.component.scss'
})
export class GeneratorComponent implements OnDestroy {
  availableCourses!: AvailableLOResponse;
  estimatedTime = 0;
  availableTimeControl = new FormControl();
  interval: any;
  metaData!: MetaManager;
  @ViewChildren(LoTreeComponent) loForms!: QueryList<LoTreeComponent>;
  inProgress = false;

  constructor(
    private courseService: CourseService,
    private matDialog: MatDialog,
    private snackBar: MatSnackBar,
    private router: Router,
    private conversationService: ConversationService
  ) {
    this.getCourseList();

    this.courseService.getMetaData().subscribe((meta) => {
      this.metaData = meta;
      this.interval = setInterval(() => {
        const cellIds = this.getSelectedCells();

        this.estimatedTime = meta.getEstimatedTime(cellIds);
      }, 1000);
    })
  }

  getCourseList() {
    this.courseService.getAvailableLO().subscribe((res) => {
      this.availableCourses = res;
    });
  }

  get availableUnit() {
    if (!this.availableCourses) {
      return [];
    }
    return Object.keys(this.availableCourses);
  }

  getTopics(unit: string) {
    return Object.keys(this.availableCourses[unit]);
  }

  getSelectedCells(showError = false) {
    const selectedOutComesSet = this.loForms.map(c => c.getSelectedOutcomes()).flat();

    if (showError && !selectedOutComesSet.length) {
      this.snackBar.open('Select atleast 1 Learning Outcome!');
      return [];
    }

    let cellIds: string[] = [];
    selectedOutComesSet.forEach((set) => {
      const unit = set[0];
      const topic = set[1];
      const lo = set[2];

      const thisCellIds = this.availableCourses[unit][topic].outcomes.filter((l) => l.outcome === lo).map(x => x.outcome_mapping).flat();
      cellIds = cellIds.concat(thisCellIds);
    })

    return cellIds
  }

  openAssistantDialog(): void {
    const position: DialogPosition = {
      bottom: '0',
      right: '64px'
    };

    const dialogRef = this.matDialog.open(GeneratorAiHelperComponent, {
      position,
      height: '600px',
      width: '400px'
    });
  }

  generateCourse() {
    if (this.inProgress) { return; }
    this.inProgress = true;
    const cellIds = this.getSelectedCells(true)
    // if (this.availableTimeControl.value && this.availableTimeControl.value < this.estimatedTime) {
    this.courseService.optimizeCourse(cellIds, this.availableTimeControl.value).subscribe((optimizedCells) => {
      const sorted = sortLearningObjects(this.metaData.metaData, optimizedCells);

      console.log('Sorted', sorted);

      this.createCourse(sorted);
    });
    // } else {
    //   this.createCourse(cellIds);
    // }
  }

  createCourse(cellIds: string[]) {
    const dialog = this.matDialog.open(GeneratorConfirmationComponent, {
      width: '500px',
      minHeight: '400px',
      data: { cellIds }
    });

    dialog.afterClosed().subscribe((data => {
      if (data) {
        this.inProgress = false;
        this.router.navigateByUrl('/dashboard');
      }
    }))
  }

  ngOnDestroy(): void {
    if (this.interval) {
      clearInterval(this.interval);
    }
  }
}
