import { test, expect } from '@playwright/test';

test.describe('Ayarlar Sayfası Testleri', () => {
  test.beforeEach(async ({ page }) => {
    // Test öncesi giriş yapma işlemi
    await page.goto('/');
    await page.getByRole('button', { name: 'Giriş Yap' }).click();
    await page.getByPlaceholder('Kullanıcı Adı').fill('test_user');
    await page.getByPlaceholder('Şifre').fill('test_password');
    await page.getByRole('button', { name: 'Giriş' }).click();
    
    // Giriş başarılı olmalı
    await expect(page).toHaveURL('/dashboard');
  });

  test('Ayarlar sayfasına gidip bilgileri kaydetme', async ({ page }) => {
    // Ayarlar sayfasına git
    await page.getByRole('link', { name: 'Ayarlar' }).click();
    await expect(page).toHaveURL('/settings');
    
    // Form alanlarını doldur
    await page.getByLabel('İsim').fill('Test Kullanıcı');
    await page.getByLabel('Bio').fill('Bu bir test biyografisidir.');
    await page.getByLabel('E-posta').fill('test@example.com');
    await page.getByLabel('Telegram Kullanıcı Adı').fill('test_telegram');
    
    // Bildirim tercihlerini güncelle
    await page.getByLabel('Yeni mesajlar için bildirim').check();
    await page.getByLabel('Ödeme bildirimleri').check();
    
    // Değişiklikleri kaydet
    await page.getByRole('button', { name: 'Kaydet' }).click();
    
    // Başarı mesajını kontrol et
    await expect(page.getByText('Ayarlar başarıyla kaydedildi')).toBeVisible();
    
    // Sayfayı yenile ve değerlerin kalıcı olduğunu doğrula
    await page.reload();
    
    await expect(page.getByLabel('İsim')).toHaveValue('Test Kullanıcı');
    await expect(page.getByLabel('Bio')).toHaveValue('Bu bir test biyografisidir.');
    await expect(page.getByLabel('E-posta')).toHaveValue('test@example.com');
    await expect(page.getByLabel('Telegram Kullanıcı Adı')).toHaveValue('test_telegram');
    await expect(page.getByLabel('Yeni mesajlar için bildirim')).toBeChecked();
    await expect(page.getByLabel('Ödeme bildirimleri')).toBeChecked();
  });
}); 