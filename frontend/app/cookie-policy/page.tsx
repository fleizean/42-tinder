"use client";

import { useEffect } from "react";
import { Metadata } from 'next';

const metadata: Metadata = {
  title: 'Çerez Politikası | CrushIt',
  description: 'CrushIt çerez politikası, çerez kullanımı ve gizlilik prosedürleri hakkında bilgiler.',
};

const CookiePolicyPage = () => {
  useEffect(() => {
    document.title = metadata.title as string;
  }, []);

  return (
    <section className="pt-[150px] pb-[120px] bg-[#1C1C1E]">
      <div className="max-w-4xl mx-auto bg-[#2C2C2E] rounded-lg shadow-lg p-8">
        <h1 className="text-4xl font-bold mb-4 text-center text-white">
          Çerez Politikası
        </h1>
        <p className="text-sm text-gray-400 text-center mb-8">
          Son güncelleme: {new Date().toLocaleDateString('tr-TR')}
        </p>

        <div className="space-y-8 text-gray-300">
          <section className="border-b border-[#3C3C3E] pb-6">
            <h2 className="text-2xl font-semibold mb-4 text-white">1. Giriş</h2>
            <p>CrushIt olarak çerez kullanım prensiplerimiz:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Çerezler, size daha iyi bir kullanıcı deneyimi sunmak için kullanılır.</li>
              <li>Oturum bilgileriniz güvenli şekilde saklanır.</li>
              <li>Tercihleriniz ve ayarlarınız korunur.</li>
            </ul>
          </section>

          <section className="border-b border-[#3C3C3E] pb-6">
            <h2 className="text-2xl font-semibold mb-4 text-white">2. Çerez Türleri</h2>
            <p>Kullandığımız çerez türleri:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Zorunlu çerezler (oturum ve güvenlik için)</li>
              <li>İşlevsel çerezler (tercihlerinizi hatırlamak için)</li>
              <li>Analitik çerezler (site kullanımını analiz etmek için)</li>
            </ul>
          </section>

          <section className="border-b border-[#3C3C3E] pb-6">
            <h2 className="text-2xl font-semibold mb-4 text-white">3. Çerezlerin Kullanım Amacı</h2>
            <p>Çerezleri aşağıdaki amaçlarla kullanıyoruz:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Oturum yönetimi ve güvenlik</li>
              <li>Kullanıcı tercihlerinin saklanması</li>
              <li>Site performansının iyileştirilmesi</li>
              <li>Kullanıcı deneyiminin kişiselleştirilmesi</li>
            </ul>
          </section>

          <section className="border-b border-[#3C3C3E] pb-6">
            <h2 className="text-2xl font-semibold mb-4 text-white">4. Çerez Kontrolü</h2>
            <p>Çerez tercihlerinizi yönetmek için:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Tarayıcı ayarlarınızdan çerezleri kontrol edebilirsiniz</li>
              <li>İstediğiniz zaman çerezleri silebilirsiniz</li>
              <li>Çerez tercihlerinizi güncelleyebilirsiniz</li>
            </ul>
          </section>

          <section className="border-b border-[#3C3C3E] pb-6">
            <h2 className="text-2xl font-semibold mb-4 text-white">5. Üçüncü Taraf Çerezleri</h2>
            <p>Platform üzerinde:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Google Analytics çerezleri</li>
              <li>Sosyal medya entegrasyonu çerezleri</li>
              <li>Güvenlik ve doğrulama çerezleri</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold mb-4 text-white">6. Daha Fazla Bilgi</h2>
            <p>Çerez politikamız hakkında:</p>
            <ul className="list-disc pl-6 space-y-1 mt-4">
              <li>Sorularınız için bizimle iletişime geçebilirsiniz</li>
              <li>Düzenli olarak politikamızı güncelliyoruz</li>
            </ul>
          </section>
        </div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 z-[-1] h-full w-full bg-gradient-to-b from-[#1C1C1E] via-[#8A2BE2]/10 to-[#D63384]/10"></div>
    </section>
  );
};

export default CookiePolicyPage;