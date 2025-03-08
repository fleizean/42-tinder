"use client";

import { useEffect } from "react";
import { Metadata } from 'next';

const metadata: Metadata = {
  title: 'Gizlilik Politikası | CrushIt',
  description: 'CrushIt gizlilik politikası, kişisel verilerin korunması ve kullanımı hakkında bilgiler.',
};

const PrivacyPage = () => {
  useEffect(() => {
    document.title = metadata.title as string;
  }, []);

  return (
    <section className="pt-[150px] pb-[120px] bg-[#1C1C1E]">
    <div className="max-w-4xl mx-auto bg-[#2C2C2E] rounded-lg shadow-lg p-8">
      <h1 className="text-4xl font-bold mb-4 text-center text-white">
        Gizlilik Politikası
      </h1>
      <p className="text-sm text-gray-400 text-center mb-8">
        Son güncelleme: {new Date().toLocaleDateString('tr-TR')}
      </p>

      <div className="space-y-8 text-gray-300">
        <section className="border-b border-[#3C3C3E] pb-6">
          <h2 className="text-2xl font-semibold mb-4 text-white">1. Giriş</h2>
          <p>CrushIt olarak, kullanıcılarımızın gizliliğini önemsiyoruz. Bu politika, kişisel verilerinizin nasıl toplandığını, kullanıldığını ve korunduğunu açıklamaktadır.</p>
        </section>

        <section className="border-b border-[#3C3C3E] pb-6">
          <h2 className="text-2xl font-semibold mb-4 text-white">2. Toplanan Kişisel Veriler</h2>
          <p>Aşağıdaki kişisel verileri toplayabiliriz:</p>
          <ul className="list-disc pl-6 space-y-1 mt-4">
            <li>Ad, soyad, e-posta adresi, telefon numarası gibi iletişim bilgileri</li>
            <li>Profil bilgileri (fotoğraflar, ilgi alanları, tercihler vb.)</li>
            <li>IP adresi, tarayıcı türü, işletim sistemi gibi teknik bilgiler</li>
            <li>Kullanım verileri (eşleşmeler, mesajlaşmalar vb.)</li>
          </ul>
        </section>

        <section className="border-b border-[#3C3C3E] pb-6">
          <h2 className="text-2xl font-semibold mb-4 text-white">3. Kişisel Verilerin Kullanım Amaçları</h2>
          <p>Kişisel verilerinizi aşağıdaki amaçlarla kullanabiliriz:</p>
          <ul className="list-disc pl-6 space-y-1 mt-4">
            <li>Size en uygun eşleşmeleri sunmak</li>
            <li>Platformun güvenliğini sağlamak</li>
            <li>Kullanıcı desteği sağlamak</li>
            <li>Hizmetlerimizi geliştirmek</li>
            <li>Yasal yükümlülükleri yerine getirmek</li>
          </ul>
        </section>
          <section className="border-b pb-6">
            <h2 className="text-2xl font-semibold mb-4">4. Kişisel Verilerin Paylaşımı</h2>
            <p>Kişisel verilerinizi aşağıdaki durumlar haricinde üçüncü taraflarla paylaşmayız:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Yasal zorunluluklar</li>
              <li>Hizmet sağlayıcılarımız (örneğin, hosting, ödeme işleme)</li>
              <li>Açık rızanızın olması</li>
            </ul>
          </section>

          <section className="border-b pb-6">
            <h2 className="text-2xl font-semibold mb-4">5. Kişisel Verilerin Güvenliği</h2>
            <p>Kişisel verilerinizi korumak için aşağıdaki önlemleri alıyoruz:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Şifreleme</li>
              <li>Erişim kontrolleri</li>
              <li>Güvenlik duvarları</li>
              <li>Düzenli güvenlik denetimleri</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4">6. Haklarınız</h2>
            <p>KVKK uyarınca aşağıdaki haklara sahipsiniz:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Kişisel verilerinize erişim</li>
              <li>Kişisel verilerinizi düzeltme</li>
              <li>Kişisel verilerinizi silme</li>
              <li>Kişisel verilerinizin işlenmesini kısıtlama</li>
              <li>Veri taşınabilirliği</li>
              <li>İtiraz etme</li>
            </ul>
          </section>
        </div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 z-[-1] h-full w-full bg-gradient-to-b from-[#1C1C1E] via-[#8A2BE2]/10 to-[#D63384]/10"></div>
    </section>
  );
};

export default PrivacyPage;