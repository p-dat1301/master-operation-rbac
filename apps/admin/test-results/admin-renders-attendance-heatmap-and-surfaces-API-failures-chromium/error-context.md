# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin.spec.ts >> renders attendance heatmap and surfaces API failures
- Location: e2e/admin.spec.ts:135:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByTestId('attendance-page')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByTestId('attendance-page')

```

```yaml
- img
- text: Không đủ quyền Tài khoản hiện tại không có quyền truy cập màn hình này.
- link "Quay về trang tổng quan":
  - /url: /
  - text: Về tổng quan
```

# Test source

```ts
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
  108 |   await signIn(page);
  109 |   await page.goto('/users');
  110 | 
  111 |   await expect(page.getByTestId('users-page')).toBeVisible();
  112 |   await page.getByTestId('create-user-btn').click();
  113 |   await page.getByRole('button', { name: 'Tạo' }).click();
  114 | 
  115 |   await expect(page.getByText('Vui lòng nhập email hợp lệ.')).toBeVisible();
  116 |   await expect(page.getByTestId('user-form-modal')).toBeVisible();
  117 | });
  118 | 
  119 | test('renders task lifecycle list and blocks invalid assignment', async ({ page }) => {
  120 |   await signIn(page);
  121 |   await page.goto('/tasks');
  122 | 
  123 |   await expect(page.getByTestId('tasks-page')).toBeVisible();
  124 |   await expect(page.getByTestId('tasks-table')).toBeVisible();
  125 |   await assertTableHasAtLeastOneDataRow(page, 'tasks-table');
  126 | 
  127 |   await page.getByTestId(/assign-task-/).first().click();
  128 |   await expect(page.getByTestId('task-assign-modal')).toBeVisible();
  129 |   await page.getByRole('button', { name: 'Phân công' }).click();
  130 | 
  131 |   await expect(page.getByText('Vui lòng nhập ID nhân sự hợp lệ.')).toBeVisible();
  132 |   await expect(page.getByTestId('task-assign-modal')).toBeVisible();
  133 | });
  134 | 
  135 | test('renders attendance heatmap and surfaces API failures', async ({ page }) => {
  136 |   await signIn(page);
  137 |   await page.goto('/attendance');
  138 | 
> 139 |   await expect(page.getByTestId('attendance-page')).toBeVisible();
      |                                                     ^ Error: expect(locator).toBeVisible() failed
  140 |   await expect(page.getByTestId('attendance-table')).toBeVisible();
  141 |   await assertTableHasAtLeastOneDataRow(page, 'attendance-table');
  142 | 
  143 |   await page.route('http://127.0.0.1:8010/api/v1/attendance/heatmap**', async (route) => {
  144 |     await route.fulfill({
  145 |       status: 500,
  146 |       contentType: 'application/json',
  147 |       body: JSON.stringify({ detail: 'Injected attendance failure' })
  148 |     });
  149 |   });
  150 | 
  151 |   await page.reload();
  152 | 
  153 |   await expect(page.getByText('Không tải được dữ liệu chấm công: Injected attendance failure')).toBeVisible();
  154 | });
  155 | 
  156 | test('renders leaves review surface and preserves invalid review guard', async ({ page }) => {
  157 |   await signIn(page);
  158 |   await page.goto('/leaves');
  159 | 
  160 |   await expect(page.getByTestId('leaves-page')).toBeVisible();
  161 |   await expect(page.getByTestId('leaves-table')).toBeVisible();
  162 |   await assertTableHasAtLeastOneDataRow(page, 'leaves-table');
  163 | 
  164 |   await page.getByTestId(/reject-leave-/).first().click();
  165 |   await expect(page.getByTestId('leave-review-modal')).toBeVisible();
  166 |   await page.getByRole('button', { name: 'Từ chối' }).click();
  167 | 
  168 |   await expect(page.getByText('Vui lòng nhập lý do từ chối.')).toBeVisible();
  169 |   await expect(page.getByTestId('leave-review-modal')).toBeVisible();
  170 | });
  171 | 
```