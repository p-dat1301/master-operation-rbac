import { expect, test, type Page } from '@playwright/test';

async function signIn(page: Page, email = 'admin@company.vn', password = 'Admin@123') {
  await page.goto('/login');
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Password' }).fill(password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByTestId('admin-header')).toBeVisible();
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
