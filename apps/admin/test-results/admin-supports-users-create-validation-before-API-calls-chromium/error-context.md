# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin.spec.ts >> supports users create validation before API calls
- Location: e2e/admin.spec.ts:107:5

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Sign in' })

```

# Test source

```ts
  1   | import { expect, test, type Page } from '@playwright/test';
  2   | 
  3   | async function signIn(page: Page, email = 'admin@company.vn', password = 'Admin@123') {
  4   |   await page.goto('/login');
  5   |   await page.getByRole('textbox', { name: 'Email' }).fill(email);
  6   |   await page.getByRole('textbox', { name: 'Password' }).fill(password);
> 7   |   await page.getByRole('button', { name: 'Sign in' }).click();
      |                                                       ^ Error: locator.click: Test timeout of 30000ms exceeded.
  8   |   await expect(page.getByTestId('admin-header')).toBeVisible();
  9   | }
  10  | 
  11  | async function assertTableHasAtLeastOneDataRow(page: Page, tableTestId: string) {
  12  |   const rows = page.getByTestId(tableTestId).locator('tbody tr');
  13  |   await expect(rows.first()).toBeVisible();
  14  | }
  15  | 
  16  | test('renders admin shell after login', async ({ page }) => {
  17  |   await signIn(page);
  18  | 
  19  |   await expect(page.getByTestId('admin-sider')).toBeVisible();
  20  |   await expect(page.getByTestId('admin-header')).toBeVisible();
  21  |   await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  22  | });
  23  | 
  24  | test('blocks manager from protected sync route', async ({ page }) => {
  25  |   await signIn(page, 'manager@company.vn', 'Manager@123');
  26  | 
  27  |   await page.goto('/config/menu-sync');
  28  | 
  29  |   await expect(page.getByTestId('forbidden-page')).toBeVisible();
  30  | });
  31  | 
  32  | test('runs menu sync from UI and renders summary', async ({ page }) => {
  33  |   await signIn(page);
  34  | 
  35  |   await page.goto('/config/menu-sync');
  36  |   await page.getByTestId('sync-menu-button').click();
  37  |   await expect(page.getByTestId('sync-confirm-modal')).toBeVisible();
  38  |   await page.getByRole('button', { name: 'Confirm sync' }).click();
  39  | 
  40  |   await expect(page.getByTestId('sync-summary-created')).toBeVisible();
  41  |   await expect(page.getByTestId('sync-summary-updated')).toBeVisible();
  42  |   await expect(page.getByTestId('sync-summary-skipped')).toBeVisible();
  43  | });
  44  | 
  45  | test('shows graceful error feedback on sync failure', async ({ page }) => {
  46  |   await page.route('http://127.0.0.1:8010/api/v1/admin/config/i18n/sync', async (route) => {
  47  |     await route.fulfill({
  48  |       status: 500,
  49  |       contentType: 'application/json',
  50  |       body: JSON.stringify({ detail: 'Injected sync failure' })
  51  |     });
  52  |   });
  53  | 
  54  |   await signIn(page);
  55  |   await page.goto('/config/i18n-sync');
  56  |   await page.getByTestId('sync-i18n-button').click();
  57  |   await page.getByRole('button', { name: 'Confirm sync' }).click();
  58  | 
  59  |   await expect(page.getByText('i18n sync failed: Injected sync failure')).toBeVisible();
  60  | });
  61  | 
  62  | test('cleans up confirm modal when route changes', async ({ page }) => {
  63  |   await signIn(page);
  64  |   await page.goto('/config/menu-sync');
  65  |   await page.getByTestId('sync-menu-button').click();
  66  |   await expect(page.getByTestId('sync-confirm-modal')).toBeVisible();
  67  | 
  68  |   await page.goto('/config/i18n-sync');
  69  | 
  70  |   await expect(page.getByTestId('sync-confirm-modal')).toBeHidden();
  71  |   await expect(page.getByTestId('i18n-sync-page')).toBeVisible();
  72  | });
  73  | 
  74  | test('supports permissions CRUD UI', async ({ page }) => {
  75  |   await signIn(page);
  76  |   await page.goto('/rbac/permissions');
  77  | 
  78  |   await expect(page.getByTestId('permissions-page')).toBeVisible();
  79  |   await page.getByTestId('create-permission-btn').click();
  80  |   await page.getByTestId('permission-code-input').fill('system.frontend.test');
  81  |   await page.getByTestId('permission-description-input').fill('Frontend test permission');
  82  |   await page.getByRole('button', { name: 'Tạo' }).click();
  83  | 
  84  |   await expect(page.getByText('system.frontend.test')).toBeVisible();
  85  | 
  86  |   await page.getByTestId(/edit-permission-/).first().click();
  87  |   await page.getByTestId('permission-description-input').fill('Updated frontend test permission');
  88  |   await page.getByRole('button', { name: 'Lưu' }).click();
  89  | 
  90  |   await expect(page.getByText('Updated frontend test permission')).toBeVisible();
  91  | 
  92  |   const createdRow = page.locator('tr', { hasText: 'system.frontend.test' });
  93  |   await createdRow.getByTestId(/delete-permission-/).click();
  94  |   await page.getByRole('button', { name: 'Xóa' }).click();
  95  |   await expect(createdRow).toBeHidden();
  96  | });
  97  | 
  98  | test('renders departments directory as read-only list', async ({ page }) => {
  99  |   await signIn(page);
  100 |   await page.goto('/system/departments');
  101 | 
  102 |   await expect(page.getByTestId('departments-page')).toBeVisible();
  103 |   await expect(page.getByTestId('departments-table')).toBeVisible();
  104 |   await expect(page.getByRole('button', { name: /tạo department/i })).toHaveCount(0);
  105 | });
  106 | 
  107 | test('supports users create validation before API calls', async ({ page }) => {
```