"use client";

import { Metadata } from "next";
import React, { useEffect } from "react";

const metadata: Metadata = {
    title: 'Başarı Hikayeleri | CrushIt',
    description: 'CrushIt üzerinde başarılı eşleşmeler ve mutlu ilişki hikayeleri.',
};

const SuccessStoriesPage = () => {
    useEffect(() => {
        document.title = metadata.title as string;
    }, []);

    return (
        <section className="pt-[150px] pb-[120px] bg-[#1C1C1E]">
            <div className="max-w-4xl mx-auto bg-[#2C2C2E] rounded-lg shadow-lg p-8">
                <h1 className="text-4xl font-bold mb-4 text-center text-white">
                    Başarı Hikayeleri
                </h1>
                <p className="text-sm text-gray-400 text-center mb-8">
                CrushIt da başlayan aşk hikayeleri
                </p>

                <div className="space-y-8 text-gray-300">
                    <section className="border-b border-[#3C3C3E] pb-6">
                        <h2 className="text-2xl font-semibold mb-4 text-white">Ayşe & Mehmet</h2>
                        <p className="mb-4">
                            CrushIt da tanıştık ve ilk mesajlaşmamızdan itibaren aramızdaki kimyayı hissettik. 
                            6 ay sonra nişanlandık ve şimdi evliliğe hazırlanıyoruz.
                        </p>
                        <p className="text-sm text-gray-400">İstanbul, 2023</p>
                    </section>

                    <section className="border-b border-[#3C3C3E] pb-6">
                        <h2 className="text-2xl font-semibold mb-4 text-white">Deniz & Ali</h2>
                        <p className="mb-4">
                            Ortak ilgi alanlarımız sayesinde eşleştik. İlk buluşmamızdan sonra birbirimizden 
                            hiç ayrılmadık. Şimdi mutlu bir çiftiz.
                        </p>
                        <p className="text-sm text-gray-400">Ankara, 2023</p>
                    </section>

                    <section className="border-b border-[#3C3C3E] pb-6">
                        <h2 className="text-2xl font-semibold mb-4 text-white">Zeynep & Can</h2>
                        <p className="mb-4">
                            İkimiz de doğru kişiyi arıyorduk ve CrushIt sayesinde birbirimizi bulduk. 
                            Artık hayatımızı birlikte planlıyoruz.
                        </p>
                        <p className="text-sm text-gray-400">İzmir, 2023</p>
                    </section>

                    <section>
                        <h2 className="text-2xl font-semibold mb-4 text-white">Sizin Hikayaniz</h2>
                        <p className="mb-4">
                            Belki de sıradaki başarı hikayesi sizinki olacak. CrushIt da aşkı bulmak için 
                            hemen üye olun ve yeni insanlarla tanışın.
                        </p>
                        <a href="/signup" className="text-[#D63384] hover:text-[#8A2BE2] transition-colors duration-300">
                            Hemen Üye Ol →
                        </a>
                    </section>
                </div>
            </div>
            <div className="absolute bottom-0 left-0 right-0 z-[-1] h-full w-full bg-gradient-to-b from-[#1C1C1E] via-[#8A2BE2]/10 to-[#D63384]/10"></div>
        </section>
    );
};

export default SuccessStoriesPage;