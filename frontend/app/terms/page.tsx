"use client";

import { useEffect } from "react";
import { Metadata } from 'next';

const metadata: Metadata = {
    title: 'Kullanım Koşulları | CrushIt',
    description: 'CrushIt kullanım koşulları, hizmet şartları ve yasal bilgiler.',
};

const TermsPage = () => {
    useEffect(() => {
        document.title = metadata.title as string;
    }, []);

    return (
        <section className="pt-[150px] pb-[120px] bg-[#1C1C1E]">
            <div className="max-w-4xl mx-auto bg-[#2C2C2E] rounded-lg shadow-lg p-8">
                <h1 className="text-4xl font-bold mb-4 text-center text-white">
                    CrushIt Kullanım Koşulları
                </h1>
                <p className="text-sm text-gray-400 text-center mb-8">
                    Son güncelleme: {new Date().toLocaleDateString('tr-TR')}
                </p>

                <div className="space-y-8 text-gray-300">
                    <section className="border-b border-[#3C3C3E] pb-6">
                        <h2 className="text-2xl font-semibold mb-4 text-white">1. Genel Kullanım Koşulları</h2>
                        <p>CrushIt platformunu kullanarak aşağıdaki koşulları kabul etmiş sayılırsınız:</p>
                        <ul className="list-disc pl-6 space-y-1 mt-4">
                            <li>Platform, yalnızca 18 yaş ve üzeri kullanıcılar içindir.</li>
                            <li>Kullanıcılar, profil bilgilerinin doğruluğundan sorumludur.</li>
                            <li>Rahatsız edici veya uygunsuz davranışlar yasaktır.</li>
                        </ul>
                    </section>

                    <section className="border-b border-[#3C3C3E] pb-6">
                        <h2 className="text-2xl font-semibold mb-4 text-white">2. Profil ve Eşleşme</h2>
                        <p>Platform kullanımı kapsamında:</p>
                        <ul className="list-disc pl-6 space-y-1 mt-4">
                            <li>Profil fotoğrafları gerçek ve güncel olmalıdır</li>
                            <li>Kişisel bilgiler güvenle saklanır</li>
                            <li>Eşleşme tercihleri gizli tutulur</li>
                        </ul>
                    </section>

                    <section className="border-b border-[#3C3C3E] pb-6">
                        <h2 className="text-2xl font-semibold mb-4 text-white">3. Güvenlik Kuralları</h2>
                        <p>Güvenli kullanım için:</p>
                        <ul className="list-disc pl-6 space-y-1 mt-4">
                            <li>Kişisel bilgilerinizi koruyun</li>
                            <li>Şüpheli durumları bildirin</li>
                            <li>İlk buluşmalar güvenli ortamlarda yapılmalıdır</li>
                        </ul>
                    </section>

                    <section className="border-b border-[#3C3C3E] pb-6">
                        <h2 className="text-2xl font-semibold mb-4 text-white">4. Premium Üyelik</h2>
                        <p>Premium üyelik avantajları:</p>
                        <ul className="list-disc pl-6 space-y-1 mt-4">
                            <li>Sınırsız mesajlaşma</li>
                            <li>Gelişmiş filtreleme özellikleri</li>
                            <li>Görüntülü görüşme imkanı</li>
                        </ul>
                    </section>

                    <section className="border-b border-[#3C3C3E] pb-6">
                        <h2 className="text-2xl font-semibold mb-4 text-white">5. İptal ve İade Koşulları</h2>
                        <p>Üyelik iptali ve iade süreçleri:</p>
                        <ul className="list-disc pl-6 space-y-1 mt-4">
                            <li>Premium üyelik her an iptal edilebilir</li>
                            <li>Kalan süre için iade yapılmaz</li>
                            <li>Hesap silme işlemi geri alınamaz</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">6. Gizlilik ve Veri Güvenliği</h2>
                        <p>Veri işleme politikası:</p>
                        <ul className="list-disc pl-6 space-y-1 mt-4">
                            <li>Kişisel veriler KVKK kapsamında korunur</li>
                            <li>Mesajlaşmalar şifrelenir</li>
                            <li>Veriler üçüncü taraflarla paylaşılmaz</li>
                        </ul>
                    </section>
                </div>
            </div>
            <div className="absolute bottom-0 left-0 right-0 z-[-1] h-full w-full bg-gradient-to-b from-[#1C1C1E] via-[#8A2BE2]/10 to-[#D63384]/10"></div>
        </section>
    );
};

export default TermsPage;