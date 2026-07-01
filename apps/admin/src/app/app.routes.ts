import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';
import { permissionGuard } from './core/guards/permission.guard';
import { AdminShellComponent } from './layouts/admin-shell/admin-shell.component';

export const routes: Routes = [
	{
		path: 'login',
		loadComponent: () => import('./features/auth/login-page.component').then((m) => m.LoginPageComponent)
	},
	{
		path: '',
		component: AdminShellComponent,
		canActivate: [authGuard],
		children: [
			{
				path: '',
				loadComponent: () => import('./features/dashboard/dashboard-page.component').then((m) => m.DashboardPageComponent),
				data: { title: 'Dashboard' }
			},
			// ── Configuration ──────────────────────────────────────────────────────
			{
				path: 'config/menu-sync',
				loadComponent: () => import('./features/config/menu-sync-page.component').then((m) => m.MenuSyncPageComponent),
				canActivate: [permissionGuard('system.config.manage')],
				data: { title: 'Menu sync' }
			},
			{
				path: 'config/i18n-sync',
				loadComponent: () => import('./features/config/i18n-sync-page.component').then((m) => m.I18nSyncPageComponent),
				canActivate: [permissionGuard('system.config.manage')],
				data: { title: 'i18n sync' }
			},
			// ── Users ──────────────────────────────────────────────────────────────
			{
				path: 'users',
				loadComponent: () => import('./features/users/users-page.component').then((m) => m.UsersPageComponent),
				canActivate: [permissionGuard('manage_org')],
				data: { title: 'Quản lý người dùng' }
			},
			// ── RBAC ───────────────────────────────────────────────────────────────
			{
				path: 'rbac/roles',
				loadComponent: () => import('./features/rbac/roles-page.component').then((m) => m.RolesPageComponent),
				canActivate: [permissionGuard('manage_org')],
				data: { title: 'Roles' }
			},
			{
				path: 'rbac/permissions',
				loadComponent: () => import('./features/rbac/permissions-page.component').then((m) => m.PermissionsPageComponent),
				canActivate: [permissionGuard('manage_org')],
				data: { title: 'Permissions' }
			},
			{
				path: 'system/departments',
				loadComponent: () => import('./features/system/departments-page.component').then((m) => m.DepartmentsPageComponent),
				canActivate: [permissionGuard('manage_org')],
				data: { title: 'Departments' }
			},
			// ── Operations ─────────────────────────────────────────────────────────
			{
				path: 'tasks',
				loadComponent: () => import('./features/tasks/tasks-page.component').then((m) => m.TasksPageComponent),
				canActivate: [permissionGuard('create_task')],
				data: { title: 'Công việc' }
			},
			{
				path: 'leaves',
				loadComponent: () => import('./features/leaves/leaves-page.component').then((m) => m.LeavesPageComponent),
				canActivate: [permissionGuard('approve_leave')],
				data: { title: 'Đơn nghỉ phép' }
			},
			{
				path: 'attendance',
				loadComponent: () => import('./features/attendance/attendance-page.component').then((m) => m.AttendancePageComponent),
				canActivate: [permissionGuard('view_attendance_self')],
				data: { title: 'Attendance' }
			},
			// ── Notifications (auth-only, no special permission) ────────────────────
			{
				path: 'notifications',
				loadComponent: () => import('./features/notifications/notifications-page.component').then((m) => m.NotificationsPageComponent),
				data: { title: 'Thông báo' }
			},
			{
				path: 'chat',
				loadComponent: () => import('./features/chat/chat-window.component').then((m) => m.ChatWindowComponent),
				canActivate: [authGuard],
				data: { title: 'Chat' }
			},
			{
				path: 'agentic/conversations',
				loadComponent: () => import('./features/chat/agentic-conversations-page.component').then((m) => m.AgenticConversationsPageComponent),
				canActivate: [authGuard],
				data: { title: 'Conversations' }
			},
			{
				path: 'agentic/documents',
				loadComponent: () => import('./features/documents/documents-page.component').then((m) => m.DocumentsPageComponent),
				canActivate: [authGuard],
				data: { title: 'Documents' }
			},
			// ── Audit ──────────────────────────────────────────────────────────────
			{
				path: 'audit-logs',
				loadComponent: () => import('./features/audit/audit-logs-page.component').then((m) => m.AuditLogsPageComponent),
				canActivate: [permissionGuard('audit:view')],
				data: { title: 'Audit Logs' }
			}
		]
	},
	{
		path: 'unauthorized',
		loadComponent: () => import('./features/system/unauthorized-page.component').then((m) => m.UnauthorizedPageComponent)
	},
	{
		path: 'forbidden',
		loadComponent: () => import('./features/system/forbidden-page.component').then((m) => m.ForbiddenPageComponent)
	},
	{
		path: 'not-found',
		loadComponent: () => import('./features/system/not-found-page.component').then((m) => m.NotFoundPageComponent)
	},
	{
		path: '**',
		redirectTo: '/not-found'
	}
];
