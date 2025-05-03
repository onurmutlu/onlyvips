import { test, expect } from '@playwright/test';

test.describe('Log Sayfası Testleri', () => {
  test.beforeEach(async ({ page }) => {
    // Test öncesi giriş yapma işlemi
    await page.goto('/');
    await page.getByRole('button', { name: 'Giriş Yap' }).click();
    await page.getByPlaceholder('Kullanıcı Adı').fill('test_user');
    await page.getByPlaceholder('Şifre').fill('test_password');
    await page.getByRole('button', { name: 'Giriş' }).click();
    
    // Dashboard sayfasına geçiş
    await expect(page).toHaveURL('/dashboard');
  });

  test('Log sayfasının yüklenmesi ve filtreleme', async ({ page }) => {
    // Log sayfasına git
    await page.getByRole('link', { name: 'Loglar' }).click();
    await expect(page).toHaveURL('/logs');
    
    // Sayfa başlığını kontrol et
    await expect(page.getByRole('heading', { name: 'Sistem Logları' })).toBeVisible();
    
    // Tabloyu kontrol et
    await expect(page.locator('table')).toBeVisible();
    await expect(page.locator('th', { hasText: 'Tarih' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Seviye' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Mesaj' })).toBeVisible();
    await expect(page.locator('th', { hasText: 'Kaynak' })).toBeVisible();
    
    // Filtreleme işlemini test et
    await page.getByRole('combobox', { name: 'Seviye' }).selectOption('error');
    await page.getByRole('button', { name: 'Filtrele' }).click();
    
    // Sadece hata loglarının görüntülendiğini doğrula
    const seviyeHücreleri = page.locator('td.log-level');
    await expect(seviyeHücreleri).toHaveCount(await seviyeHücreleri.count());
    
    for (let i = 0; i < await seviyeHücreleri.count(); i++) {
      await expect(seviyeHücreleri.nth(i)).toHaveText('error');
    }
    
    // Tarih aralığını filtrele
    const bugün = new Date();
    const biAyÖnce = new Date();
    biAyÖnce.setMonth(biAyÖnce.getMonth() - 1);
    
    const bugünStr = bugün.toISOString().split('T')[0];
    const biAyÖnceStr = biAyÖnce.toISOString().split('T')[0];
    
    await page.getByLabel('Başlangıç Tarihi').fill(biAyÖnceStr);
    await page.getByLabel('Bitiş Tarihi').fill(bugünStr);
    await page.getByRole('button', { name: 'Filtrele' }).click();
    
    // Sonuçların yüklendiğini kontrol et
    await expect(page.getByText('Yükleniyor...')).not.toBeVisible();
    
    // Sıralama işlemini test et
    await page.locator('th', { hasText: 'Tarih' }).click(); // Tarihe göre sırala
    
    // İndirme butonunu test et
    await page.getByRole('button', { name: 'CSV İndir' }).click();
    await expect(page.getByText('Log dosyası indiriliyor...')).toBeVisible();
  });

  test('Log detaylarını görüntüleme', async ({ page }) => {
    // Log sayfasına git
    await page.goto('/logs');
    
    // İlk log kaydına tıkla
    await page.locator('tr').nth(1).click();
    
    // Detay modalının açıldığını kontrol et
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Log Detayı' })).toBeVisible();
    
    // Detay alanlarını kontrol et
    await expect(page.getByText('ID:')).toBeVisible();
    await expect(page.getByText('Tarih:')).toBeVisible();
    await expect(page.getByText('Seviye:')).toBeVisible();
    await expect(page.getByText('Mesaj:')).toBeVisible();
    await expect(page.getByText('Kaynak:')).toBeVisible();
    await expect(page.getByText('Kullanıcı:')).toBeVisible();
    await expect(page.getByText('Stack Trace:')).toBeVisible();
    
    // Modalı kapat
    await page.getByRole('button', { name: 'Kapat' }).click();
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });
}); 