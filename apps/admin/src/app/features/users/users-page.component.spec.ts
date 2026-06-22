import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { provideNzIcons } from 'ng-zorro-antd/icon';
import {
	CheckCircleOutline, DeleteOutline, EditOutline, EyeOutline,
	LockOutline, PlusOutline, ReloadOutline, StopOutline
} from '@ant-design/icons-angular/icons';

import { UserListItem } from '../../models/user.models';
import { UserApiService } from '../../services/user-api.service';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalService } from 'ng-zorro-antd/modal';
import { UsersPageComponent } from './users-page.component';

describe('UsersPageComponent', () => {
	const users: UserListItem[] = [
		{
			id: 1,
			employee_code: 'EMP001',
			email: 'active@company.vn',
			full_name: 'Active User',
			role_name: 'admin',
			permissions: ['system.config.manage'],
			phone: null,
			job_title: 'Manager',
			department_id: null,
			manager_id: null,
			is_active: true
		},
		{
			id: 2,
			employee_code: 'EMP002',
			email: 'inactive@company.vn',
			full_name: 'Inactive User',
			role_name: 'employee',
			permissions: [],
			phone: null,
			job_title: null,
			department_id: null,
			manager_id: null,
			is_active: false
		}
	];

	const userApiMock = {
		listUsers: vi.fn(() => of(users)),
		createUser: vi.fn(),
		updateUser: vi.fn(),
		deleteUser: vi.fn(),
		activateUser: vi.fn(),
		deactivateUser: vi.fn(),
		resetPassword: vi.fn()
	};

	const messageMock = {
		success: vi.fn(),
		warning: vi.fn(),
		error: vi.fn()
	};

	const modalMock = {
		confirm: vi.fn()
	};

	let fixture: ComponentFixture<UsersPageComponent>;

	beforeEach(async () => {
		userApiMock.listUsers.mockClear();
		messageMock.success.mockClear();
		messageMock.warning.mockClear();
		messageMock.error.mockClear();
		modalMock.confirm.mockClear();

		await TestBed.configureTestingModule({
			imports: [UsersPageComponent],
			providers: [
				{ provide: UserApiService, useValue: userApiMock },
				{ provide: NzMessageService, useValue: messageMock },
				{ provide: NzModalService, useValue: modalMock },
				provideNzIcons([
					PlusOutline, ReloadOutline, EyeOutline, EditOutline, StopOutline,
					CheckCircleOutline, LockOutline, DeleteOutline
				])
			]
		}).compileComponents();

		fixture = TestBed.createComponent(UsersPageComponent);
		fixture.detectChanges();
		await fixture.whenStable();
	});

	it('loads users and applies the active filter counts', () => {
		const component = fixture.componentInstance;

		expect(userApiMock.listUsers).toHaveBeenCalledTimes(1);
		expect(component.allUsers()).toHaveLength(2);
		expect(component.activeCount()).toBe(1);
		expect(component.inactiveCount()).toBe(1);
		expect(component.filteredUsers()).toHaveLength(2);
	});

	it('filters, resets, and formats user-derived helper values', () => {
		const component = fixture.componentInstance;

		component.filters.is_active = true;
		component.applyFilters();
		expect(component.filteredUsers()).toHaveLength(1);
		expect(component.filteredUsers()[0].id).toBe(1);

		component.resetFilters();
		expect(component.filteredUsers()).toHaveLength(2);
		expect(component.getInitials('Admin User')).toBe('AU');
	});

	it('validates create form input before submitting', async () => {
		const component = fixture.componentInstance;

		component.openCreateUser();
		await component.submitUserForm();

		expect(messageMock.warning).toHaveBeenCalledWith('Vui lòng nhập đủ thông tin bắt buộc.');
		expect(userApiMock.createUser).not.toHaveBeenCalled();
	});
});
