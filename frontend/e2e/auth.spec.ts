import { test, expect } from "@playwright/test";

test.describe("Authentication pages", () => {
  test("login page renders email and password fields", async ({ page }) => {
    await page.goto("/login");
    await expect(page.getByRole("heading", { name: /sign in/i })).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /sign in/i })).toBeVisible();
  });

  test("register page renders registration form", async ({ page }) => {
    await page.goto("/register");
    await expect(
      page.getByRole("heading", { name: /create account/i }),
    ).toBeVisible();
    await expect(page.getByLabel(/email/i)).toBeVisible();
    await expect(page.getByLabel(/password/i)).toBeVisible();
  });

  test("login page shows error on invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill("invalid@test.com");
    await page.getByLabel(/password/i).fill("wrongpassword");
    await page.getByRole("button", { name: /sign in/i }).click();
    await expect(page.getByRole("alert").or(page.locator("text=/error|invalid/i"))).toBeVisible({ timeout: 5000 });
  });
});
