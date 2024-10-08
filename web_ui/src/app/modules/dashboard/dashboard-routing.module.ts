import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DashboardComponent } from './dashboard.component';

const routes: Routes = [
  {
    path: '',
    component: DashboardComponent,
    children: [
      {
        path: '',
        redirectTo: 'courses',
        pathMatch: 'prefix'
      },
      {
        path: 'courses',
        loadChildren: () => import('./modules/course-list/course-list.module').then(m => m.CourseListModule)
      },
      {
        path: 'new',
        loadChildren: () => import('./modules/generator/generator.module').then(m => m.GeneratorModule)
      }
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DashboardRoutingModule { }
