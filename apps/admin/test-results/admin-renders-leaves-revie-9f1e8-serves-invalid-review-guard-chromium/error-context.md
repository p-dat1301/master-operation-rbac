# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin.spec.ts >> renders leaves review surface and preserves invalid review guard
- Location: e2e/admin.spec.ts:156:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByTestId('leave-review-modal')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByTestId('leave-review-modal')

```

```yaml
- text: MO
- paragraph: RBAC Console
- heading "Master Operation" [level=1]
- list:
  - listitem:
    - img "dashboard"
    - text: Dashboard
  - listitem:
    - img "bell"
    - text: Thông báo
  - listitem:
    - img "team"
    - text: Người dùng
  - listitem:
    - img "team"
    - text: Departments
  - listitem:
    - img "safety-certificate"
    - text: Roles
  - listitem:
    - img "key"
    - text: Permissions
  - listitem:
    - img "check-square"
    - text: Công việc
  - listitem:
    - img "calendar"
    - text: Nghỉ phép
  - listitem:
    - img "appstore"
    - text: Menu sync
  - listitem:
    - img "translation"
    - text: i18n sync
  - listitem:
    - img "file-search"
    - text: Audit Logs
- paragraph: Angular 21 + NG ZORRO
- text: System config workspace
- button "Toggle navigation":
  - img "menu-fold"
- paragraph: Admin control plane
- heading "Đơn nghỉ phép" [level=2]
- strong: Admin User
- text: admin
- button "Sign out"
- text: Local workspace Admin / Operations / Nghỉ phép
- paragraph: Leave Management
- heading "Đơn nghỉ phép" [level=2]
- paragraph: Duyệt và quản lý yêu cầu nghỉ phép của nhân viên.
- text: 18 Chờ duyệt 10 Đã duyệt Trạng thái
- textbox "Trạng thái Tất cả down"
- text: Tất cả
- img "down"
- text: Loại nghỉ
- textbox "Loại nghỉ Tất cả down"
- text: Tất cả
- img "down"
- button "reload Đặt lại":
  - img "reload"
  - text: Đặt lại
- paragraph: Chi tiết đơn nghỉ
- paragraph: ID:3 · Đã duyệt
- button "Sửa" [disabled]
- button "Hủy" [disabled]
- button "Duyệt" [disabled]
- button "Từ chối" [disabled]
- table:
  - rowgroup:
    - row "Loại annual Từ ngày 13/06/2026 Đến ngày 14/06/2026":
      - cell "Loại"
      - cell "annual"
      - cell "Từ ngày"
      - cell "13/06/2026"
      - cell "Đến ngày"
      - cell "14/06/2026"
    - row "Lý do Family vacation":
      - cell "Lý do"
      - cell "Family vacation"
    - row "Từ chối —":
      - cell "Từ chối"
      - cell "—"
- table:
  - rowgroup:
    - row "Năm 2026 Tổng ngày 12 Đã dùng 4":
      - cell "Năm"
      - cell "2026"
      - cell "Tổng ngày"
      - cell "12"
      - cell "Đã dùng"
      - cell "4"
    - row "Đang chờ 0 Còn lại 8 Admin Sửa số dư":
      - cell "Đang chờ"
      - cell "0"
      - cell "Còn lại"
      - cell "8"
      - cell "Admin"
      - cell "Sửa số dư":
        - button "Sửa số dư"
- table:
  - rowgroup:
    - row "# Nhân viên Loại Từ ngày Đến ngày Lý do Trạng thái Hành động":
      - columnheader "#"
      - columnheader "Nhân viên"
      - columnheader "Loại"
      - columnheader "Từ ngày"
      - columnheader "Đến ngày"
      - columnheader "Lý do"
      - columnheader "Trạng thái"
      - columnheader "Hành động"
  - rowgroup:
    - row "1 ID:3 annual 13/06/2026 14/06/2026 Family vacation Đã duyệt":
      - cell "1"
      - cell "ID:3"
      - cell "annual"
      - cell "13/06/2026"
      - cell "14/06/2026"
      - cell "Family vacation"
      - cell "Đã duyệt"
      - cell
    - row "2 ID:1 sick 13/06/2026 14/06/2026 Medical check Chờ duyệt Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
      - cell "2"
      - cell "ID:1"
      - cell "sick"
      - cell "13/06/2026"
      - cell "14/06/2026"
      - cell "Medical check"
      - cell "Chờ duyệt"
      - cell "Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
        - button "Duyệt đơn nghỉ của ID 1":
          - img "check"
        - button "Từ chối đơn nghỉ của ID 1":
          - img "close"
    - row "3 ID:3 annual 29/03/4476 30/03/4476 Family vacation Đã duyệt":
      - cell "3"
      - cell "ID:3"
      - cell "annual"
      - cell "29/03/4476"
      - cell "30/03/4476"
      - cell "Family vacation"
      - cell "Đã duyệt"
      - cell
    - row "4 ID:1 sick 26/11/3376 27/11/3376 Medical check Chờ duyệt Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
      - cell "4"
      - cell "ID:1"
      - cell "sick"
      - cell "26/11/3376"
      - cell "27/11/3376"
      - cell "Medical check"
      - cell "Chờ duyệt"
      - cell "Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
        - button "Duyệt đơn nghỉ của ID 1":
          - img "check"
        - button "Từ chối đơn nghỉ của ID 1":
          - img "close"
    - row "5 ID:3 annual 28/12/3646 29/12/3646 Family vacation Đã duyệt":
      - cell "5"
      - cell "ID:3"
      - cell "annual"
      - cell "28/12/3646"
      - cell "29/12/3646"
      - cell "Family vacation"
      - cell "Đã duyệt"
      - cell
    - row "6 ID:1 sick 26/11/3932 27/11/3932 Medical check Chờ duyệt Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
      - cell "6"
      - cell "ID:1"
      - cell "sick"
      - cell "26/11/3932"
      - cell "27/11/3932"
      - cell "Medical check"
      - cell "Chờ duyệt"
      - cell "Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
        - button "Duyệt đơn nghỉ của ID 1":
          - img "check"
        - button "Từ chối đơn nghỉ của ID 1":
          - img "close"
    - row "7 ID:3 annual 23/12/2582 24/12/2582 Family vacation Đã duyệt":
      - cell "7"
      - cell "ID:3"
      - cell "annual"
      - cell "23/12/2582"
      - cell "24/12/2582"
      - cell "Family vacation"
      - cell "Đã duyệt"
      - cell
    - row "8 ID:1 sick 16/03/3434 17/03/3434 Medical check Chờ duyệt Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
      - cell "8"
      - cell "ID:1"
      - cell "sick"
      - cell "16/03/3434"
      - cell "17/03/3434"
      - cell "Medical check"
      - cell "Chờ duyệt"
      - cell "Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
        - button "Duyệt đơn nghỉ của ID 1":
          - img "check"
        - button "Từ chối đơn nghỉ của ID 1":
          - img "close"
    - row "9 ID:3 annual 10/01/3018 11/01/3018 Family vacation Đã duyệt":
      - cell "9"
      - cell "ID:3"
      - cell "annual"
      - cell "10/01/3018"
      - cell "11/01/3018"
      - cell "Family vacation"
      - cell "Đã duyệt"
      - cell
    - row "10 ID:1 sick 31/03/3948 01/04/3948 Medical check Chờ duyệt Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
      - cell "10"
      - cell "ID:1"
      - cell "sick"
      - cell "31/03/3948"
      - cell "01/04/3948"
      - cell "Medical check"
      - cell "Chờ duyệt"
      - cell "Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
        - button "Duyệt đơn nghỉ của ID 1":
          - img "check"
        - button "Từ chối đơn nghỉ của ID 1":
          - img "close"
    - row "11 ID:3 annual 04/08/2436 05/08/2436 Family vacation Đã duyệt":
      - cell "11"
      - cell "ID:3"
      - cell "annual"
      - cell "04/08/2436"
      - cell "05/08/2436"
      - cell "Family vacation"
      - cell "Đã duyệt"
      - cell
    - row "12 ID:1 sick 21/07/3678 22/07/3678 Medical check Chờ duyệt Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
      - cell "12"
      - cell "ID:1"
      - cell "sick"
      - cell "21/07/3678"
      - cell "22/07/3678"
      - cell "Medical check"
      - cell "Chờ duyệt"
      - cell "Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
        - button "Duyệt đơn nghỉ của ID 1":
          - img "check"
        - button "Từ chối đơn nghỉ của ID 1":
          - img "close"
    - row "13 ID:3 annual 08/02/3932 09/02/3932 Family vacation Đã duyệt":
      - cell "13"
      - cell "ID:3"
      - cell "annual"
      - cell "08/02/3932"
      - cell "09/02/3932"
      - cell "Family vacation"
      - cell "Đã duyệt"
      - cell
    - row "14 ID:1 sick 20/11/2650 21/11/2650 Medical check Chờ duyệt Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
      - cell "14"
      - cell "ID:1"
      - cell "sick"
      - cell "20/11/2650"
      - cell "21/11/2650"
      - cell "Medical check"
      - cell "Chờ duyệt"
      - cell "Duyệt đơn nghỉ của ID 1 Từ chối đơn nghỉ của ID 1":
        - button "Duyệt đơn nghỉ của ID 1":
          - img "check"
        - button "Từ chối đơn nghỉ của ID 1":
          - img "close"
    - row "15 ID:3 annual 30/01/2051 31/01/2051 Family vacation Đã duyệt":
      - cell "15"
      - cell "ID:3"
      - cell "annual"
      - cell "30/01/2051"
      - cell "31/01/2051"
      - cell "Family vacation"
      - cell "Đã duyệt"
      - cell
- list:
  - listitem "Trang Trước":
    - button "left" [disabled]:
      - img "left"
  - listitem "1"
  - listitem "2"
  - listitem "Trang Kế":
    - button "right":
      - img "right"
- dialog:
  - document:
    - button "Close":
      - img "close"
    - img "question-circle"
    - text: Từ chối đơn nghỉ của "1"?
    - button "Huỷ"
    - button "Từ chối"
```

# Test source

```ts
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
  139 |   await expect(page.getByTestId('attendance-page')).toBeVisible();
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
> 165 |   await expect(page.getByTestId('leave-review-modal')).toBeVisible();
      |                                                        ^ Error: expect(locator).toBeVisible() failed
  166 |   await page.getByRole('button', { name: 'Từ chối' }).click();
  167 | 
  168 |   await expect(page.getByText('Vui lòng nhập lý do từ chối.')).toBeVisible();
  169 |   await expect(page.getByTestId('leave-review-modal')).toBeVisible();
  170 | });
  171 | 
```