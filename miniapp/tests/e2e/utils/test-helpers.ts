import { Page, expect } from '@playwright/test';

/**
 * Dashboard sayfasına git ve yüklendiğinden emin ol
 */
export async function gotoDashboard(page: Page): Promise<void> {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByText('Yükleniyor...')).not.toBeVisible({ timeout: 5000 });
}

/**
 * Ayarlar sayfasına git ve yüklendiğinden emin ol
 */
export async function gotoSettings(page: Page): Promise<void> {
  await page.goto('/settings');
  await expect(page.getByRole('heading', { name: 'Ayarlar' })).toBeVisible();
  await expect(page.getByText('Yükleniyor...')).not.toBeVisible({ timeout: 5000 });
}

/**
 * Mesaj ekleme sayfasına git ve yüklendiğinden emin ol
 */
export async function gotoAddMessage(page: Page): Promise<void> {
  await page.goto('/add-message');
  await expect(page.getByRole('heading', { name: 'Yeni Mesaj' })).toBeVisible();
  await expect(page.getByText('Yükleniyor...')).not.toBeVisible({ timeout: 5000 });
}

/**
 * Log sayfasına git ve yüklendiğinden emin ol
 */
export async function gotoLogs(page: Page): Promise<void> {
  await page.goto('/logs');
  await expect(page.getByRole('heading', { name: 'Sistem Logları' })).toBeVisible();
  await expect(page.getByText('Yükleniyor...')).not.toBeVisible({ timeout: 5000 });
}

/**
 * Rastgele bir mesaj başlığı oluştur
 */
export function generateRandomMessageTitle(): string {
  return `Test Mesajı ${Date.now()}`;
}

/**
 * Sayfada bir başarı mesajı gösterildiğini doğrula
 */
export async function waitForSuccessToast(page: Page, messageText: string): Promise<void> {
  await expect(page.getByText(messageText)).toBeVisible({ timeout: 3000 });
}

/**
 * Bir dialog mesajını yanıtla
 */
export async function handleConfirmationDialog(page: Page, confirm: boolean): Promise<void> {
  if (confirm) {
    await page.getByRole('button', { name: 'Evet' }).click();
  } else {
    await page.getByRole('button', { name: 'Hayır' }).click();
  }
} 