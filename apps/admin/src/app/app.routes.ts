import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { permissionGuard } from './core/guards/permission.guard';
import { LoginPageComponent } from './features/auth/login-page.component';
import { DashboardPageComponent } from './features/dashboard/dashboard-page.component';
import { I18nSyncPageComponent } from './features/config/i18n-sync-page.component';
import { MenuSyncPageComponent } from './features/config/menu-sync-page.component';
import { ForbiddenPageComponent } from './features/system/forbidden-page.component';
import { NotFoundPageComponent } from './features/system/not-found-page.component';
import { UnauthorizedPageComponent } from './features/system/unauthorized-page.component';
import { AdminShellComponent } from './layouts/admin-shell/admin-shell.component';

export const routes: Routes = [
	{
		path: 'login',
		component: LoginPageComponent
	},
	{
		path: '',
		component: AdminShellComponent,
		canActivate: [authGuard],
		children: [
			{
				path: '',
				component: DashboardPageComponent,
				data: { title: 'Dashboard' }
			},
			{
				path: 'config/menu-sync',
				component: MenuSyncPageComponent,
				canActivate: [permissionGuard('system.config.manage')],
				data: { title: 'Menu sync' }
			},
			{
				path: 'config/i18n-sync',
				component: I18nSyncPageComponent,
				canActivate: [permissionGuard('system.config.manage')],
				data: { title: 'i18n sync' }
			}
		]
	},
	{
		path: 'unauthorized',
		component: UnauthorizedPageComponent
	},
	{
		path: 'forbidden',
		component: ForbiddenPageComponent
	},
	{
		path: 'not-found',
		component: NotFoundPageComponent
	},
	{
		path: '**',
		redirectTo: '/not-found'
	}
];
