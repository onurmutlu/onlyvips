import { test, expect } from '@playwright/test';

test.describe('Mesaj İşlemleri Testleri', () => {
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

  test('Yeni mesaj ekleyip dashboard\'da listeleme', async ({ page }) => {
    // Mesaj ekleme sayfasına git
    await page.getByRole('link', { name: 'Mesaj Ekle' }).click();
    await expect(page).toHaveURL('/add-message');
    
    // Mesaj bilgilerini doldur
    const mesajBaşlık = `Test Mesajı ${Date.now()}`;
    await page.getByLabel('Başlık').fill(mesajBaşlık);
    await page.getByLabel('İçerik').fill('Bu bir test mesajının içeriğidir.');
    
    // Alıcı seç
    await page.getByRole('combobox', { name: 'Alıcı' }).click();
    await page.getByRole('option', { name: 'Tüm Aboneler' }).click();
    
    // Mesajı gönder
    await page.getByRole('button', { name: 'Gönder' }).click();
    
    // Başarı mesajını kontrol et
    await expect(page.getByText('Mesaj başarıyla gönderildi')).toBeVisible();
    
    // Dashboard'a geri dön
    await page.getByRole('link', { name: 'Dashboard' }).click();
    await expect(page).toHaveURL('/dashboard');
    
    // Mesajın listede görünmesini kontrol et
    await expect(page.getByText(mesajBaşlık)).toBeVisible();
    
    // Mesaj detaylarını kontrol et
    await page.getByText(mesajBaşlık).click();
    await expect(page.getByText('Bu bir test mesajının içeriğidir.')).toBeVisible();
  });

  test('Dashboard\'da mesaj güncelleme', async ({ page }) => {
    // Dashboard'a git
    await page.goto('/dashboard');
    
    // İlk mesajı seç
    const mesajKartı = page.locator('.message-card').first();
    await mesajKartı.getByRole('button', { name: 'Düzenle' }).click();
    
    // Mesaj bilgilerini güncelle
    const yeniBaslik = `Güncellenmiş Mesaj ${Date.now()}`;
    await page.getByLabel('Başlık').fill(yeniBaslik);
    await page.getByLabel('İçerik').fill('Bu içerik güncellenmiştir.');
    
    // Değişiklikleri kaydet
    await page.getByRole('button', { name: 'Güncelle' }).click();
    
    // Başarı mesajını kontrol et
    await expect(page.getByText('Mesaj başarıyla güncellendi')).toBeVisible();
    
    // Dashboard'a geri dön
    await page.goto('/dashboard');
    
    // Güncellenmiş mesajın listede görünmesini kontrol et
    await expect(page.getByText(yeniBaslik)).toBeVisible();
  });

  test('Dashboard\'da mesaj silme', async ({ page }) => {
    // Dashboard'a git
    await page.goto('/dashboard');
    
    // Silinecek mesajın başlığını al
    const mesajKartı = page.locator('.message-card').first();
    const mesajBaslik = await mesajKartı.locator('.message-title').textContent();
    
    // Silme butonuna tıkla
    await mesajKartı.getByRole('button', { name: 'Sil' }).click();
    
    // Onay dialogunu onayla
    await page.getByRole('button', { name: 'Evet, Sil' }).click();
    
    // Silme işleminin başarılı olduğunu kontrol et
    await expect(page.getByText('Mesaj başarıyla silindi')).toBeVisible();
    
    // Mesajın artık listede olmadığını doğrula
    await expect(page.getByText(mesajBaslik)).toBeHidden();
  });
}); 