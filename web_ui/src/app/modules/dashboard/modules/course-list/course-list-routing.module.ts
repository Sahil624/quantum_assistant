import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CourseListComponent } from './course-list.component';

const routes: Routes = [
  {
    path: 'learn/:courseID',
    loadChildren: () => import('./modules/course-detail/course-detail.module').then(m => m.CourseDetailModule)
  },
  {
    path: '',
    component: CourseListComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CourseListRoutingModule { }
