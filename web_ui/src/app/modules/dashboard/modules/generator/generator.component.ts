import { Component } from '@angular/core';
import { CourseService } from '../../../../helpers/services/course/course.service';
import { AvailableLOResponse } from '../../../../helpers/services/course/course.interface';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { FormArray, FormBuilder, FormControl, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { GeneratorConfirmationComponent } from './components/generator-confirmation/generator-confirmation.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';

@Component({
  selector: 'app-generator',
  standalone: true,
  imports: [
    MatExpansionModule,
    MatCheckboxModule,
    MatButtonModule,
    MatIconModule,
    MatDividerModule,
    FormsModule,
    ReactiveFormsModule,
    GeneratorConfirmationComponent
  ],
  templateUrl: './generator.component.html',
  styleUrl: './generator.component.scss'
})
export class GeneratorComponent {
  availableCourses!: AvailableLOResponse;
  generatorForm!: FormGroup;

  constructor(
    private courseService: CourseService,
    private formBuilder: FormBuilder,
    private matDialog: MatDialog,
    private snackBar: MatSnackBar,
    private router: Router
  ) {
    this.getCourseList();
  }

  getCourseList() {
    this.courseService.getAvailableLO().subscribe((res) => {
      this.availableCourses = res;
      const controls: { [key: string]: FormControl } = {};
      Object.values(this.availableCourses).forEach((title) => {
        Object.values(title).forEach(outcome => {
          outcome.outcomes.forEach((outcome) => {
            controls[outcome.outcome.slice(0, outcome.outcome.length - 1)] = this.formBuilder.control(null);
          })
        })
      });


      this.generatorForm = this.formBuilder.group(controls);
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

  generateCourse() {
    if (this.generatorForm.invalid) { return; }

    const selectedOutComes = Object.keys(this.generatorForm.controls).
      filter(controlName => this.generatorForm.controls[controlName].value).
      map(name => name + '.');

      if(!selectedOutComes.length) {
        this.snackBar.open('Select atleast Learning Outcome!');
        return;
      }
      
    let cellIds: string[] = [];
    this.availableUnit.forEach((unit) => {
      this.getTopics(unit).forEach((topic) => {
        this.availableCourses[unit][topic].outcomes.forEach((lo) => {
          if(selectedOutComes.includes(lo.outcome)) {
            cellIds = cellIds.concat(lo.outcome_mapping);
          }
        })
      })
    });


    const dialog = this.matDialog.open(GeneratorConfirmationComponent, {
      width: '500px',
      minHeight: '400px',
      data : { cellIds }
    });

    dialog.afterClosed().subscribe((data => {
      if(data) {
        this.router.navigateByUrl('/dashboard');
      }
    }))
  }
}
