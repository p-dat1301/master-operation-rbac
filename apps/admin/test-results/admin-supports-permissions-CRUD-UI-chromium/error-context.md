# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: admin.spec.ts >> supports permissions CRUD UI
- Location: e2e/admin.spec.ts:74:5

# Error details

```
Error: locator.click: Error: strict mode violation: getByRole('button', { name: 'Tạo' }) resolved to 2 elements:
    1) <button nz-button="" nzsize="large" nztype="primary" _ngcontent-ng-c2795036021="" data-testid="create-permission-btn" class="ant-btn ant-btn-primary ant-btn-lg" ant-click-animating-without-extra-node="true">…</button> aka getByTestId('create-permission-btn')
    2) <button nz-button="" class="ant-btn ant-btn-primary">…</button> aka getByRole('button', { name: 'Tạo', exact: true })

Call log:
  - waiting for getByRole('button', { name: 'Tạo' })

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e4]:
    - generic [ref=e7]:
      - generic [ref=e8]:
        - generic [ref=e9]: MO
        - generic [ref=e10]:
          - paragraph [ref=e11]: RBAC Console
          - heading "Master Operation" [level=1] [ref=e12]
      - list [ref=e13]:
        - listitem [ref=e14] [cursor=pointer]:
          - generic [ref=e15]:
            - img "dashboard" [ref=e16]:
              - img [ref=e17]
            - text: Dashboard
        - listitem [ref=e19] [cursor=pointer]:
          - generic [ref=e20]:
            - img "bell" [ref=e21]:
              - img [ref=e22]
            - text: Thông báo
        - listitem [ref=e24] [cursor=pointer]:
          - generic [ref=e25]:
            - img "team" [ref=e26]:
              - img [ref=e27]
            - text: Người dùng
        - listitem [ref=e29] [cursor=pointer]:
          - generic [ref=e30]:
            - img "team" [ref=e31]:
              - img [ref=e32]
            - text: Departments
        - listitem [ref=e34] [cursor=pointer]:
          - generic [ref=e35]:
            - img "safety-certificate" [ref=e36]:
              - img [ref=e37]
            - text: Roles
        - listitem [ref=e39] [cursor=pointer]:
          - generic [ref=e40]:
            - img "key" [ref=e41]:
              - img [ref=e42]
            - text: Permissions
        - listitem [ref=e44] [cursor=pointer]:
          - generic [ref=e45]:
            - img "check-square" [ref=e46]:
              - img [ref=e47]
            - text: Công việc
        - listitem [ref=e50] [cursor=pointer]:
          - generic [ref=e51]:
            - img "calendar" [ref=e52]:
              - img [ref=e53]
            - text: Nghỉ phép
        - listitem [ref=e55] [cursor=pointer]:
          - generic [ref=e56]:
            - img "appstore" [ref=e57]:
              - img [ref=e58]
            - text: Menu sync
        - listitem [ref=e60] [cursor=pointer]:
          - generic [ref=e61]:
            - img "translation" [ref=e62]:
              - img [ref=e63]
            - text: i18n sync
        - listitem [ref=e66] [cursor=pointer]:
          - generic [ref=e67]:
            - img "file-search" [ref=e68]:
              - img [ref=e69]
            - text: Audit Logs
      - generic [ref=e71]:
        - paragraph [ref=e72]: Angular 21 + NG ZORRO
        - generic [ref=e73]: System config workspace
    - generic [ref=e74]:
      - generic [ref=e75]:
        - generic [ref=e76]:
          - button "Toggle navigation" [ref=e77] [cursor=pointer]:
            - img "menu-fold" [ref=e78]:
              - img [ref=e79]
          - generic [ref=e81]:
            - paragraph [ref=e82]: Admin control plane
            - heading "Permissions" [level=2] [ref=e83]
        - generic [ref=e84]:
          - generic [ref=e85]:
            - strong [ref=e86]: Admin User
            - generic [ref=e87]: admin
          - button "Sign out" [ref=e88] [cursor=pointer]:
            - generic [ref=e89]: Sign out
          - generic [ref=e90]: Local workspace
      - generic [ref=e92]:
        - generic [ref=e93]:
          - generic [ref=e94]:
            - text: Admin
            - generic [ref=e95]: /
          - generic [ref=e96]:
            - text: RBAC
            - generic [ref=e97]: /
          - generic [ref=e98]: Permissions
        - generic [ref=e101]:
          - generic [ref=e102]:
            - generic [ref=e103]:
              - paragraph [ref=e104]: RBAC Management
              - heading "Permissions" [level=2] [ref=e105]
              - paragraph [ref=e106]: Quản lý danh sách quyền trong hệ thống.
            - button "plus Tạo permission" [ref=e107] [cursor=pointer]:
              - img "plus" [ref=e108]:
                - img [ref=e109]
              - generic [ref=e112]: Tạo permission
          - generic [ref=e117]:
            - table [ref=e121]:
              - rowgroup [ref=e128]:
                - row "# Mã quyền Mô tả Nhóm Hành động" [ref=e129]:
                  - columnheader "#" [ref=e130]
                  - columnheader "Mã quyền" [ref=e131]
                  - columnheader "Mô tả" [ref=e132]
                  - columnheader "Nhóm" [ref=e133]
                  - columnheader "Hành động" [ref=e134]
              - rowgroup [ref=e135]:
                - row "1 postman:permission:updated Updated by automated script postman edit delete" [ref=e136]:
                  - cell "1" [ref=e137]
                  - cell "postman:permission:updated" [ref=e138]:
                    - code [ref=e139]: postman:permission:updated
                  - cell "Updated by automated script" [ref=e140]
                  - cell "postman" [ref=e141]:
                    - generic [ref=e142]: postman
                  - cell "edit delete" [ref=e143]:
                    - button "edit" [ref=e144] [cursor=pointer]:
                      - img "edit" [ref=e145]:
                        - img [ref=e146]
                    - button "delete" [ref=e148] [cursor=pointer]:
                      - img "delete" [ref=e149]:
                        - img [ref=e150]
                - row "2 create_task Create tasks create_task edit delete" [ref=e152]:
                  - cell "2" [ref=e153]
                  - cell "create_task" [ref=e154]:
                    - code [ref=e155]: create_task
                  - cell "Create tasks" [ref=e156]
                  - cell "create_task" [ref=e157]:
                    - generic [ref=e158]: create_task
                  - cell "edit delete" [ref=e159]:
                    - button "edit" [ref=e160] [cursor=pointer]:
                      - img "edit" [ref=e161]:
                        - img [ref=e162]
                    - button "delete" [ref=e164] [cursor=pointer]:
                      - img "delete" [ref=e165]:
                        - img [ref=e166]
                - row "3 assign_task Assign tasks to others assign_task edit delete" [ref=e168]:
                  - cell "3" [ref=e169]
                  - cell "assign_task" [ref=e170]:
                    - code [ref=e171]: assign_task
                  - cell "Assign tasks to others" [ref=e172]
                  - cell "assign_task" [ref=e173]:
                    - generic [ref=e174]: assign_task
                  - cell "edit delete" [ref=e175]:
                    - button "edit" [ref=e176] [cursor=pointer]:
                      - img "edit" [ref=e177]:
                        - img [ref=e178]
                    - button "delete" [ref=e180] [cursor=pointer]:
                      - img "delete" [ref=e181]:
                        - img [ref=e182]
                - row "4 approve_leave Approve or reject leave requests approve_leave edit delete" [ref=e184]:
                  - cell "4" [ref=e185]
                  - cell "approve_leave" [ref=e186]:
                    - code [ref=e187]: approve_leave
                  - cell "Approve or reject leave requests" [ref=e188]
                  - cell "approve_leave" [ref=e189]:
                    - generic [ref=e190]: approve_leave
                  - cell "edit delete" [ref=e191]:
                    - button "edit" [ref=e192] [cursor=pointer]:
                      - img "edit" [ref=e193]:
                        - img [ref=e194]
                    - button "delete" [ref=e196] [cursor=pointer]:
                      - img "delete" [ref=e197]:
                        - img [ref=e198]
                - row "5 view_attendance_all View attendance for all departments view_attendance_all edit delete" [ref=e200]:
                  - cell "5" [ref=e201]
                  - cell "view_attendance_all" [ref=e202]:
                    - code [ref=e203]: view_attendance_all
                  - cell "View attendance for all departments" [ref=e204]
                  - cell "view_attendance_all" [ref=e205]:
                    - generic [ref=e206]: view_attendance_all
                  - cell "edit delete" [ref=e207]:
                    - button "edit" [ref=e208] [cursor=pointer]:
                      - img "edit" [ref=e209]:
                        - img [ref=e210]
                    - button "delete" [ref=e212] [cursor=pointer]:
                      - img "delete" [ref=e213]:
                        - img [ref=e214]
                - row "6 view_attendance_dept View attendance for own department view_attendance_dept edit delete" [ref=e216]:
                  - cell "6" [ref=e217]
                  - cell "view_attendance_dept" [ref=e218]:
                    - code [ref=e219]: view_attendance_dept
                  - cell "View attendance for own department" [ref=e220]
                  - cell "view_attendance_dept" [ref=e221]:
                    - generic [ref=e222]: view_attendance_dept
                  - cell "edit delete" [ref=e223]:
                    - button "edit" [ref=e224] [cursor=pointer]:
                      - img "edit" [ref=e225]:
                        - img [ref=e226]
                    - button "delete" [ref=e228] [cursor=pointer]:
                      - img "delete" [ref=e229]:
                        - img [ref=e230]
                - row "7 audit:view View audit logs audit edit delete" [ref=e232]:
                  - cell "7" [ref=e233]
                  - cell "audit:view" [ref=e234]:
                    - code [ref=e235]: audit:view
                  - cell "View audit logs" [ref=e236]
                  - cell "audit" [ref=e237]:
                    - generic [ref=e238]: audit
                  - cell "edit delete" [ref=e239]:
                    - button "edit" [ref=e240] [cursor=pointer]:
                      - img "edit" [ref=e241]:
                        - img [ref=e242]
                    - button "delete" [ref=e244] [cursor=pointer]:
                      - img "delete" [ref=e245]:
                        - img [ref=e246]
                - row "8 system.config.manage Manage admin system configuration sync system edit delete" [ref=e248]:
                  - cell "8" [ref=e249]
                  - cell "system.config.manage" [ref=e250]:
                    - code [ref=e251]: system.config.manage
                  - cell "Manage admin system configuration sync" [ref=e252]
                  - cell "system" [ref=e253]:
                    - generic [ref=e254]: system
                  - cell "edit delete" [ref=e255]:
                    - button "edit" [ref=e256] [cursor=pointer]:
                      - img "edit" [ref=e257]:
                        - img [ref=e258]
                    - button "delete" [ref=e260] [cursor=pointer]:
                      - img "delete" [ref=e261]:
                        - img [ref=e262]
                - row "9 manage_org Manage organization (users, roles, departments) manage_org edit delete" [ref=e264]:
                  - cell "9" [ref=e265]
                  - cell "manage_org" [ref=e266]:
                    - code [ref=e267]: manage_org
                  - cell "Manage organization (users, roles, departments)" [ref=e268]
                  - cell "manage_org" [ref=e269]:
                    - generic [ref=e270]: manage_org
                  - cell "edit delete" [ref=e271]:
                    - button "edit" [ref=e272] [cursor=pointer]:
                      - img "edit" [ref=e273]:
                        - img [ref=e274]
                    - button "delete" [ref=e276] [cursor=pointer]:
                      - img "delete" [ref=e277]:
                        - img [ref=e278]
            - list [ref=e281]:
              - listitem "Trang Trước" [ref=e282]:
                - button "left" [disabled] [ref=e283]:
                  - img "left" [ref=e284]:
                    - img [ref=e285]
              - listitem "1" [ref=e287] [cursor=pointer]:
                - generic [ref=e288]: "1"
              - listitem "Trang Kế" [ref=e289]:
                - button "right" [disabled] [ref=e290]:
                  - img "right" [ref=e291]:
                    - img [ref=e292]
  - dialog [ref=e296]:
    - document:
      - generic [ref=e297]:
        - button "Close" [ref=e298] [cursor=pointer]:
          - img "close" [ref=e300]:
            - img [ref=e301]
        - generic [ref=e305]: Tạo permission
        - generic [ref=e307]:
          - generic [ref=e308]:
            - generic [ref=e309]: Permission key *
            - textbox "Permission key *" [ref=e310]:
              - /placeholder: e.g. audit:view
              - text: system.frontend.test
          - generic [ref=e311]:
            - generic [ref=e312]: Mô tả
            - textbox "Mô tả" [active] [ref=e313]:
              - /placeholder: Mô tả quyền
              - text: Frontend test permission
        - generic [ref=e314]:
          - button "Huỷ" [ref=e315] [cursor=pointer]:
            - generic [ref=e316]: Huỷ
          - button "Tạo" [ref=e317] [cursor=pointer]:
            - generic [ref=e318]: Tạo
```

# Test source

```ts
  1   | import { expect, test, type Page } from '@playwright/test';
  2   | 
  3   | async function signIn(page: Page, email = 'admin@company.vn', password = 'Admin@123') {
  4   |   await page.goto('/login');
  5   |   await page.getByRole('textbox', { name: 'Email' }).fill(email);
  6   |   await page.getByRole('textbox', { name: 'Password' }).fill(password);
  7   |   await page.getByRole('button', { name: 'Sign in' }).click();
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
> 82  |   await page.getByRole('button', { name: 'Tạo' }).click();
      |                                                   ^ Error: locator.click: Error: strict mode violation: getByRole('button', { name: 'Tạo' }) resolved to 2 elements:
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
  165 |   await expect(page.getByTestId('leave-review-modal')).toBeVisible();
  166 |   await page.getByRole('button', { name: 'Từ chối' }).click();
  167 | 
  168 |   await expect(page.getByText('Vui lòng nhập lý do từ chối.')).toBeVisible();
  169 |   await expect(page.getByTestId('leave-review-modal')).toBeVisible();
  170 | });
  171 | 
```