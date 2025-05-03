import { test as setup, expect } from '@playwright/test';

// CI ortamında auth skip edilebilir
const authFile = process.env.CI ? undefined : 'tests/e2e/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/');
  
  // Eğer kimlik doğrulama dosyası zaten varsa, işlemi atlayabilirsiniz
  if (authFile) {
    try {
      // Dosya var mı diye okunamaya çalışılır, hata verirse dosya yoktur
      require(authFile);
      console.log('Auth dosyası zaten mevcut, kimlik doğrulama atlanıyor.');
      return;
    } catch (error) {
      console.log('Auth dosyası bulunamadı, kimlik doğrulama başlıyor.');
    }
  }

  // Giriş formuna git
  await page.getByRole('button', { name: 'Giriş Yap' }).click();
  
  // Form alanlarını doldur
  await page.getByPlaceholder('Kullanıcı Adı').fill('test_user');
  await page.getByPlaceholder('Şifre').fill('test_password');
  
  // Giriş yap
  await page.getByRole('button', { name: 'Giriş' }).click();
  
  // Başarılı giriş olduğundan emin ol
  await expect(page).toHaveURL('/dashboard');
  
  // Çerezleri kaydet
  if (authFile) {
    await page.context().storageState({ path: authFile });
    console.log('Auth bilgileri kaydedildi:', authFile);
  }
}); 