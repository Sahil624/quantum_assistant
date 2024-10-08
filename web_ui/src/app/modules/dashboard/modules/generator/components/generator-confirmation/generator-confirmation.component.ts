import { Component, inject } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogModule, MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { CourseService } from '../../../../../../helpers/services/course/course.service';
import { CreateCourseRequest } from '../../../../../../helpers/services/course/course.interface';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-generator-confirmation',
  standalone: true,
  imports: [
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    ReactiveFormsModule,
    FormsModule
  ],
  templateUrl: './generator-confirmation.component.html',
  styleUrl: './generator-confirmation.component.scss'
})
export class GeneratorConfirmationComponent {
  readonly modelData = inject(MAT_DIALOG_DATA);

  courseForm = new FormGroup({
    title: new FormControl(null, Validators.required),
    description: new FormControl()
  });

  constructor(
    private courseService: CourseService,
    private dialogRef: MatDialogRef<GeneratorConfirmationComponent>,
    private snackBar: MatSnackBar
  ) { }

  generate() {
    if (this.courseForm.invalid) {
      this.courseForm.get('title')?.markAllAsTouched();
      return;
    }
    const formValue = this.courseForm.value;
    const request: CreateCourseRequest = {
      title: (formValue.title as any),
      learning_object_ids: this.modelData['cellIds']
    }


    if (formValue.description) {
      request.description = formValue.description;
    }
    this.courseService.createCourse(request).subscribe((res) => {
      this.snackBar.open('Course Generated!');

      this.dialogRef.close(true);
    })
  }
}
