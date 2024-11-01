import { Routes } from '@angular/router';
import { authGuard } from './helpers/guards/auth/auth.guard';
import { dashboardGuard } from './helpers/guards/dashboard/dashboard.guard';

export const routes: Routes = [
    {
        path: 'auth',
        loadChildren: () => import('./modules/auth/auth.module').then(m => m.AuthModule),
        canActivate: [authGuard]
    },
    {
        path: 'dashboard',
        loadChildren: () => import('./modules/dashboard/dashboard.module').then(m => m.DashboardModule),
        canActivate: [dashboardGuard]
    },
    {
        path: '**',
        redirectTo: 'auth'
    }
];
