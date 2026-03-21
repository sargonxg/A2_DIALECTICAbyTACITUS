import { test, expect } from "@playwright/test";

test("complete demo journey", async ({ page }) => {
  // 1. Landing page loads
  await page.goto("/");
  await expect(page.getByText("Make conflict computable")).toBeVisible();

  // 2. Navigate to demo
  await page.click("text=Try the Demo");
  await expect(page).toHaveURL(/\/demo/);

  // 3. Email gate (dismiss if shown)
  const emailInput = page.getByPlaceholder(/email/i);
  if (await emailInput.isVisible({ timeout: 2000 }).catch(() => false)) {
    await emailInput.fill("e2e-test@tacitus.me");
    await page.click("text=Get");
    await page.waitForTimeout(500);
  }

  // 4. Load sample text
  await page.click("text=HR Dispute");
  const textarea = page.locator("textarea");
  await expect(textarea).not.toBeEmpty();

  // 5. Run analysis
  await page.click("text=Analyze");

  // 6. Wait for graph to render (fallback or live)
  await expect(page.locator("svg circle").first()).toBeVisible({
    timeout: 60000,
  });

  // 7. Verify multiple nodes rendered
  const nodeCount = await page.locator("svg circle").count();
  expect(nodeCount).toBeGreaterThanOrEqual(3);

  // 8. Verify analysis sidebar
  await expect(page.getByText(/nodes|entities|actors/i)).toBeVisible({
    timeout: 5000,
  });
});

test("landing page has all sections", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Make conflict computable")).toBeVisible();
  await expect(page.getByText("Try the Demo")).toBeVisible();
  await expect(
    page.getByText(/15 Node Types|30\+.*Framework/i)
  ).toBeVisible();
});

test("demo page loads sample texts", async ({ page }) => {
  await page.goto("/demo");

  // Dismiss email gate if present
  const emailInput = page.getByPlaceholder(/email/i);
  if (await emailInput.isVisible({ timeout: 1000 }).catch(() => false)) {
    await emailInput.fill("e2e-test@tacitus.me");
    await page.click("text=Get");
    await page.waitForTimeout(500);
  }

  // Click each sample button and verify textarea fills
  for (const label of ["HR Dispute", "Geopolitical Crisis", "Commercial"]) {
    const btn = page.getByText(label, { exact: false });
    if (await btn.isVisible({ timeout: 1000 }).catch(() => false)) {
      await btn.click();
      const textarea = page.locator("textarea");
      const value = await textarea.inputValue();
      expect(value.length).toBeGreaterThan(100);
    }
  }
});
