import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:4200',
    trace: 'on-first-retry'
  },
  webServer: [
    {
      command: 'DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/masterop SECRET_KEY=dev-secret ../../.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8010',
      url: 'http://127.0.0.1:8010/health',
      reuseExistingServer: true,
      timeout: 120000
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 4200',
      url: 'http://127.0.0.1:4200',
      reuseExistingServer: true,
      timeout: 120000
    }
  ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ]
});
