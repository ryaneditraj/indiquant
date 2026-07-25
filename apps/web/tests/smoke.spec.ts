import { test, expect } from "@playwright/test";

const web = process.env.WEB_BASE || "http://localhost:3000";
const api = process.env.API_BASE || "http://localhost:8000";

test("api health", async ({ request }) => {
  const res = await request.get(`${api}/api/v1/health`);
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  expect(body.status).toBe("ok");
  expect(String(body.app_name)).toMatch(/Indiquant/i);
});

test("dashboard loads", async ({ page }) => {
  await page.goto(web);
  await expect(page.getByText(/Indiquant|Prove every edge|Money Radar/i).first()).toBeVisible({
    timeout: 15000,
  });
});
