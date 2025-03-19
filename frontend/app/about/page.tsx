"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FiUsers, FiFileText, FiTrendingUp } from "react-icons/fi";
import { Metadata } from 'next'



const metadata: Metadata = {
  title: 'Hakkımızda | CrushIt',
  description: 'Modern dünyada aşkı bulmanın en romantik yolu. Yeni insanlarla tanışın ve hayatınızın aşkını bulun.',
  openGraph: {
    title: 'Hakkımızda | CrushIt',
    description: 'Modern dünyada aşkı bulmanın en romantik yolu. Yeni insanlarla tanışın ve hayatınızın aşkını bulun.',
    type: 'website',
  },
}

const AboutPage = () => {
  const [stats, setStats] = useState([
    { id: 1, name: 'Aktif Kullanıcı', value: '1', icon: FiUsers },
    { id: 2, name: 'Başarılı Eşleşme', value: '1', icon: FiFileText },
    { id: 3, name: 'Kullanıcı Memnuniyeti', value: '5/5', icon: FiTrendingUp },
  ]);

  useEffect(() => {
    document.title = metadata.title as string;
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute("content", metadata.description as string);
    } else {
      const meta = document.createElement("meta");
      meta.name = "description";
      meta.content = metadata.description as string;
      document.head.appendChild(meta);
    }
  }, []);
  
      const [isLoading, setIsLoading] = useState(true);

      useEffect(() => {
        const fetchStats = async () => {
          try {
            const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/About/GetAboutStats`);
            if (!response.ok) throw new Error('Stats fetch failed');
            
            const data = await response.json();
            
            setStats([
              { 
                id: 1, 
                name: 'Aktif Kullanıcı', 
                value: data.activeUsers.toLocaleString(), 
                icon: FiUsers 
              },
              { 
                id: 2, 
                name: 'Başarılı Eşleşme', 
                value: data.totalAnalyses.toLocaleString(), 
                icon: FiFileText 
              },
              { 
                id: 3, 
                name: 'Kullanıcı Memnuniyeti', 
                value: `${data.userRatingRate.toFixed(1)}/5`, 
                icon: FiTrendingUp 
              }
            ]);
          } catch (error) {
            console.error('Stats fetch error:', error);
          } finally {
            setIsLoading(false);
          }
        };
    
        fetchStats();
      }, []);

  return (
    <section className="pt-[150px] pb-[120px] bg-[#1C1C1E]">
      <div className="bg-[#1C1C1E]">
        {/* Hero Section */}
        <section className="pt-[150px] pb-[60px]">
          <div className="container px-4 mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center max-w-3xl mx-auto"
            >
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
                CrushIt Hakkında
              </h1>
              <p className="text-lg text-gray-300 mb-8">
                Modern dünyada aşkı bulmanın en romantik yolu. Güvenli ve eğlenceli bir ortamda yeni insanlarla tanışın.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Mission & Vision */}
        <section className="py-16 bg-[#2C2C2E]">
          <div className="container px-4 mx-auto">
            <div className="grid md:grid-cols-2 gap-12 max-w-6xl mx-auto">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="bg-[#3C3C3E] p-8 rounded-lg shadow-lg"
              >
                <h2 className="text-2xl font-bold text-white mb-4">Misyonumuz</h2>
                <p className="text-gray-300">
                  İnsanların gerçek aşkı bulmasına yardımcı olmak ve mutlu ilişkiler kurmalarını sağlamak.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="bg-[#3C3C3E] p-8 rounded-lg shadow-lg"
              >
                <h2 className="text-2xl font-bold text-white mb-4">Vizyonumuz</h2>
                <p className="text-gray-300">
                  Modern dünyanın en güvenilir ve saygın çevrimiçi tanışma platformu olmak.
                </p>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="py-16">
          <div className="container px-3 mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {stats.map((stat) => (
                <motion.div
                  key={stat.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: stat.id * 0.1 }}
                  className="text-center"
                >
                  <div className="flex justify-center mb-4">
                    <stat.icon className="w-8 h-8 text-[#D63384]" />
                  </div>
                  <div className="text-3xl font-bold text-white mb-2">
                    {stat.value}
                  </div>
                  <div className="text-sm text-gray-300">
                    {stat.name}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="py-16 bg-[#2C2C2E]">
          <div className="container px-4 mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-center max-w-3xl mx-auto mb-12"
            >
              <h2 className="text-3xl font-bold text-white mb-4">
                Neden CrushIt?
              </h2>
              <p className="text-gray-300">
                Güvenli ve samimi bir ortamda hayatınızın aşkını bulun.
              </p>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {[
                {
                  title: 'Güvenli Ortam',
                  description: 'En üst düzey güvenlik önlemleriyle korunan bir platform.'
                },
                {
                  title: 'Akıllı Eşleşme',
                  description: 'Size en uygun adaylarla tanışmanızı sağlayan akıllı algoritma.'
                },
                {
                  title: 'Özel Profiller',
                  description: 'Kendinizi en iyi şekilde ifade edebileceğiniz detaylı profiller.'
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.2 }}
                  className="bg-[#3C3C3E] p-8 rounded-lg shadow-lg hover:shadow-[0_0_20px_rgba(214,51,132,0.2)] transition-all duration-300"
                >
                  <h3 className="text-xl font-bold text-white mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-gray-300">
                    {feature.description}
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </section>
  );
}; 

export default AboutPage;