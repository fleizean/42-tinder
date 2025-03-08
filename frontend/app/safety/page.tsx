"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { FiShield, FiLock, FiAlertTriangle, FiHeart, FiMessageCircle, FiMapPin } from "react-icons/fi";
import { Metadata } from 'next';

const metadata: Metadata = {
  title: 'Güvenlik Önerileri | Vow',
  description: 'Vow platformunda güvenli tanışma ve buluşma önerileri.',
};

const SafetyPage = () => {
  useEffect(() => {
    document.title = metadata.title as string;
  }, []);

  const safetyTips = [
    {
      icon: FiShield,
      title: "Kişisel Bilgilerinizi Koruyun",
      description: "Tanımadığınız kişilerle özel bilgilerinizi paylaşmayın.",
      tips: [
        "Adres ve telefon numaranızı gizli tutun",
        "Sosyal medya hesaplarınızı hemen paylaşmayın",
        "Finansal bilgilerinizi asla paylaşmayın"
      ]
    },
    {
      icon: FiMessageCircle,
      title: "İletişimde Dikkatli Olun",
      description: "Platform içi mesajlaşmayı tercih edin ve şüpheli durumlarda bildirin.",
      tips: [
        "İlk aşamada platform içi mesajlaşmayı kullanın",
        "Şüpheli mesajları hemen bildirin",
        "Rahatsız edici kullanıcıları engelleyin"
      ]
    },
    {
      icon: FiMapPin,
      title: "Güvenli Buluşma",
      description: "İlk buluşmalarınızı güvenli ve kalabalık yerlerde planlayın.",
      tips: [
        "Halka açık yerlerde buluşun",
        "Ulaşımınızı kendiniz sağlayın",
        "Güvendiğiniz birini bilgilendirin"
      ]
    },
    {
      icon: FiAlertTriangle,
      title: "Dikkat Edilmesi Gerekenler",
      description: "Potansiyel risklere karşı tetikte olun.",
      tips: [
        "Para talep eden kişilerden uzak durun",
        "Şüpheli profilleri bildirin",
        "Kendinizi baskı altında hissetmeyin"
      ]
    }
  ];

  return (
    <section className="pt-[150px] pb-[120px] bg-[#1C1C1E]">
      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Güvenli Buluşma Önerileri
          </h1>
          <p className="text-lg text-gray-300">
            Güvenliğiniz bizim için önemli. Lütfen bu önerileri dikkate alın.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {safetyTips.map((tip, index) => (
            <motion.div
              key={tip.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              className="bg-[#2C2C2E] rounded-xl p-8 shadow-lg border border-[#3C3C3E]"
            >
              <div className="flex items-center mb-4">
                <div className="p-3 rounded-full mr-4 bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white">
                  <tip.icon className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white">{tip.title}</h3>
              </div>
              <p className="text-gray-300 mb-4">{tip.description}</p>
              <ul className="space-y-2">
                {tip.tips.map((item, itemIndex) => (
                  <li key={itemIndex} className="flex items-center text-gray-300">
                    <FiHeart className="w-4 h-4 text-[#D63384] mr-2" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 z-[-1] h-full w-full bg-gradient-to-b from-[#1C1C1E] via-[#8A2BE2]/10 to-[#D63384]/10"></div>
    </section>
  );
};

export default SafetyPage;