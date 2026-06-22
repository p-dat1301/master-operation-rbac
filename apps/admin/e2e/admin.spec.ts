import { expect, test, type Page } from '@playwright/test';

async function signIn(page: Page, email = 'admin@company.vn', password = 'Admin@123') {
  await page.goto('/login');
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Password' }).fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByTestId('admin-header')).toBeVisible();
}

async function assertTableHasAtLeastOneDataRow(page: Page, tableTestId: string) {
  const rows = page.getByTestId(tableTestId).locator('tbody tr');
  await expect(rows.first()).toBeVisible();
}

test('renders admin shell after login', async ({ page }) => {
  await signIn(page);

  await expect(page.getByTestId('admin-sider')).toBeVisible();
  await expect(page.getByTestId('admin-header')).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
});

test('blocks manager from protected sync route', async ({ page }) => {
  await signIn(page, 'manager@company.vn', 'Manager@123');

  await page.goto('/config/menu-sync');

  await expect(page.getByTestId('forbidden-page')).toBeVisible();
});

test('runs menu sync from UI and renders summary', async ({ page }) => {
  await signIn(page);

  await page.goto('/config/menu-sync');
  await page.getByTestId('sync-menu-button').click();
  await expect(page.getByTestId('sync-confirm-modal')).toBeVisible();
  await page.getByRole('button', { name: 'Confirm sync' }).click();

  await expect(page.getByTestId('sync-summary-created')).toBeVisible();
  await expect(page.getByTestId('sync-summary-updated')).toBeVisible();
  await expect(page.getByTestId('sync-summary-skipped')).toBeVisible();
});

test('shows graceful error feedback on sync failure', async ({ page }) => {
  await page.route('http://127.0.0.1:8010/api/v1/admin/config/i18n/sync', async (route) => {
    await route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Injected sync failure' })
    });
  });

  await signIn(page);
  await page.goto('/config/i18n-sync');
  await page.getByTestId('sync-i18n-button').click();
  await page.getByRole('button', { name: 'Confirm sync' }).click();

  await expect(page.getByText('i18n sync failed: Injected sync failure')).toBeVisible();
});

test('cleans up confirm modal when route changes', async ({ page }) => {
  await signIn(page);
  await page.goto('/config/menu-sync');
  await page.getByTestId('sync-menu-button').click();
  await expect(page.getByTestId('sync-confirm-modal')).toBeVisible();

  await page.goto('/config/i18n-sync');

  await expect(page.getByTestId('sync-confirm-modal')).toBeHidden();
  await expect(page.getByTestId('i18n-sync-page')).toBeVisible();
});

test('supports permissions CRUD UI', async ({ page }) => {
  await signIn(page);
  await page.goto('/rbac/permissions');

  await expect(page.getByTestId('permissions-page')).toBeVisible();
  await page.getByTestId('create-permission-btn').click();
  await page.getByTestId('permission-code-input').fill('system.frontend.test');
  await page.getByTestId('permission-description-input').fill('Frontend test permission');
  await page.getByRole('button', { name: 'Tạo', exact: true }).last().click();

  await expect(page.getByText('system.frontend.test')).toBeVisible();

  await page.getByTestId(/edit-permission-/).first().click();
  await page.getByTestId('permission-description-input').fill('Updated frontend test permission');
  await page.getByRole('button', { name: 'Lưu' }).click();

  await expect(page.getByText('Updated frontend test permission')).toBeVisible();

  const createdRow = page.locator('tr', { hasText: 'system.frontend.test' });
  await createdRow.getByTestId(/delete-permission-/).click();
  await page.getByRole('button', { name: 'Xóa' }).click();
  await expect(createdRow).toBeHidden();
});

test('renders departments directory as read-only list', async ({ page }) => {
  await signIn(page);
  await page.goto('/system/departments');

  await expect(page.getByTestId('departments-page')).toBeVisible();
  await expect(page.getByTestId('departments-table')).toBeVisible();
  await expect(page.getByRole('button', { name: /tạo department/i })).toHaveCount(0);
});

test('supports users create validation before API calls', async ({ page }) => {
  await signIn(page);
  await page.goto('/users');

  await expect(page.getByTestId('users-page')).toBeVisible();
  await page.getByTestId('create-user-btn').click();
  await page.getByRole('button', { name: 'Tạo', exact: true }).last().click();

  await expect(page.getByText('Vui lòng nhập email hợp lệ.')).toBeVisible();
  await expect(page.getByTestId('user-form-modal')).toBeVisible();
});

test('renders task lifecycle list and blocks invalid assignment', async ({ page }) => {
  await signIn(page);
  await page.goto('/tasks');

  await expect(page.getByTestId('tasks-page')).toBeVisible();
  await expect(page.getByTestId('tasks-table')).toBeVisible();
  await assertTableHasAtLeastOneDataRow(page, 'tasks-table');

  await page.getByTestId(/assign-task-/).first().click();
  await expect(page.getByTestId('task-assign-modal')).toBeVisible();
  await page.getByRole('button', { name: 'Phân công' }).click();

  await expect(page.getByText('Vui lòng nhập ID nhân sự hợp lệ.')).toBeVisible();
  await expect(page.getByTestId('task-assign-modal')).toBeVisible();
});

test('renders attendance heatmap and surfaces API failures', async ({ page }) => {
  await signIn(page);
  await page.goto('/attendance');

  await expect(page.getByTestId('attendance-page')).toBeVisible();
  await expect(page.getByTestId('attendance-table')).toBeVisible();
  await assertTableHasAtLeastOneDataRow(page, 'attendance-table');

  await page.route('http://127.0.0.1:8010/api/v1/attendance/heatmap**', async (route) => {
    await route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Injected attendance failure' })
    });
  });

  await page.reload();

  await expect(page.getByText('Không tải được dữ liệu chấm công: Injected attendance failure')).toBeVisible();
});

test('renders leaves review surface and preserves invalid review guard', async ({ page }) => {
  await signIn(page);
  await page.goto('/leaves');

  await expect(page.getByTestId('leaves-page')).toBeVisible();
  await expect(page.getByTestId('leaves-table')).toBeVisible();
  await assertTableHasAtLeastOneDataRow(page, 'leaves-table');

  await page.getByTestId(/reject-leave-/).first().click();
  await expect(page.getByTestId('leave-review-modal')).toBeVisible();
  await page.getByRole('button', { name: 'Từ chối' }).click();

  await expect(page.getByText('Vui lòng nhập lý do từ chối.')).toBeVisible();
  await expect(page.getByTestId('leave-review-modal')).toBeVisible();
});
