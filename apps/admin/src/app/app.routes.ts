import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { permissionGuard } from './core/guards/permission.guard';
import { LoginPageComponent } from './features/auth/login-page.component';
import { DashboardPageComponent } from './features/dashboard/dashboard-page.component';
import { I18nSyncPageComponent } from './features/config/i18n-sync-page.component';
import { MenuSyncPageComponent } from './features/config/menu-sync-page.component';
import { AuditLogsPageComponent } from './features/audit/audit-logs-page.component';
import { LeavesPageComponent } from './features/leaves/leaves-page.component';
import { NotificationsPageComponent } from './features/notifications/notifications-page.component';
import { PermissionsPageComponent } from './features/rbac/permissions-page.component';
import { RolesPageComponent } from './features/rbac/roles-page.component';
import { TasksPageComponent } from './features/tasks/tasks-page.component';
import { UsersPageComponent } from './features/users/users-page.component';
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
			// ── Configuration ──────────────────────────────────────────────────────
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
			},
			// ── Users ──────────────────────────────────────────────────────────────
			{
				path: 'users',
				component: UsersPageComponent,
				canActivate: [permissionGuard('manage_org')],
				data: { title: 'Quản lý người dùng' }
			},
			// ── RBAC ───────────────────────────────────────────────────────────────
			{
				path: 'rbac/roles',
				component: RolesPageComponent,
				canActivate: [permissionGuard('manage_org')],
				data: { title: 'Roles' }
			},
			{
				path: 'rbac/permissions',
				component: PermissionsPageComponent,
				canActivate: [permissionGuard('manage_org')],
				data: { title: 'Permissions' }
			},
			// ── Operations ─────────────────────────────────────────────────────────
			{
				path: 'tasks',
				component: TasksPageComponent,
				canActivate: [permissionGuard('create_task')],
				data: { title: 'Công việc' }
			},
			{
				path: 'leaves',
				component: LeavesPageComponent,
				canActivate: [permissionGuard('approve_leave')],
				data: { title: 'Đơn nghỉ phép' }
			},
			// ── Notifications (auth-only, no special permission) ────────────────────
			{
				path: 'notifications',
				component: NotificationsPageComponent,
				data: { title: 'Thông báo' }
			},
			// ── Audit ──────────────────────────────────────────────────────────────
			{
				path: 'audit-logs',
				component: AuditLogsPageComponent,
				canActivate: [permissionGuard('audit:view')],
				data: { title: 'Audit Logs' }
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
