"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { FiHeart, FiMessageSquare, FiMapPin, FiClock, FiStar, FiSlash, FiFlag } from "react-icons/fi";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

import { Metadata } from "next";

const metadata: Metadata = {
  title: "Profil | CrushIt",
  description: "CrushIt platformunda profilinizi düzenleyin ve diğer kullanıcıları keşfedin."
};

interface ProfileData {
  name: string;
  age: number;
  location: string;
  distance: number;
  fameRating: number;
  bio: string;
  tags: string[];
  gender: string;
  preference: string;
  lastSeen: string;
  isOnline: boolean;
  images: string[];
  hasLiked: boolean;
  isMatched: boolean;
  recentVisitors: Array<{
    id: string;
    name: string;
    avatar: string;
  }>;
}

const ProfilePage = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showLightbox, setShowLightbox] = useState(false);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportReason, setReportReason] = useState("");
  const [reportDescription, setReportDescription] = useState("");


  useEffect(() => {
    document.title = metadata.title as string;
  }
    , []);

  const handleBlock = () => {
    setShowBlockModal(true);
  };

  const handleReport = () => {
    setShowReportModal(true);
  };

  const confirmBlock = () => {
    // API call to block user
    alert("Kullanıcı engellendi");
    setShowBlockModal(false);
  };

  const submitReport = () => {
    // API call to report user
    alert("Kullanıcı rapor edildi");
    setShowReportModal(false);
    setReportReason("");
    setReportDescription("");
  };

  const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    beforeChange: (current: number, next: number) => setCurrentSlide(next)
  };

  const mockProfile: ProfileData = {
    name: "Ayşe",
    age: 24,
    location: "İstanbul",
    distance: 5,
    fameRating: 4,
    bio: "Hayatı dolu dolu yaşamayı seven, sürekli kendini geliştiren biriyim. Seyahat etmeyi ve yeni yerler keşfetmeyi seviyorum.",
    tags: ["Seyahat", "Fotoğrafçılık", "Yoga", "Kitap"],
    gender: "Kadın",
    preference: "Erkek",
    lastSeen: "2 saat önce",
    isOnline: true,
    images: [
      "https://images7.alphacoders.com/121/1218824.jpg",
      "https://images7.alphacoders.com/110/1104374.jpg",
      "https://images7.alphacoders.com/121/1218826.jpg"
    ],
    hasLiked: true,
    isMatched: true,
    recentVisitors: [
      { id: "1", name: "Mehmet", avatar: "https://images7.alphacoders.com/121/1218824.jpg" },
      { id: "2", name: "Ali", avatar: "https://images7.alphacoders.com/121/1218824.jpg" }
    ]
  };

  return (
    <section className="pt-[150px] pb-[120px] bg-[#1C1C1E]">
      <div className="container mx-auto px-4">
        {/* Profile Header */}
        <div className="relative mb-8">
          <div className="h-64 rounded-t-3xl overflow-hidden">
            <Image
              src={mockProfile.images[1]}
              alt="Cover"
              fill
              className="object-cover w-full h-full"
            />
          </div>
          <div className="absolute -bottom-16 left-8">
            <div className="w-32 h-32 rounded-full border-4 border-[#2C2C2E] overflow-hidden relative">
              <Image
                src={mockProfile.images[0]}
                alt="Avatar"
                fill
                className="object-cover"
              />
              <div className="absolute bottom-2 right-2 w-4 h-4 rounded-full bg-green-500 border-2 border-[#2C2C2E]" />
            </div>
          </div>
          
        </div>

        

        


        {/* Profile Info */}
        <div className="bg-[#2C2C2E] rounded-xl p-8 mb-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                {mockProfile.name}, {mockProfile.age}
              </h1>
              <div className="flex items-center text-gray-300">
                <FiMapPin className="mr-2" />
                {mockProfile.location}, {mockProfile.distance} km uzakta
              </div>
            </div>
            <div className="flex space-x-4">
              <button className="p-3 rounded-full bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white">
                <FiHeart className="w-6 h-6" />
              </button>
              {mockProfile.isMatched && (
                <button className="p-3 rounded-full bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white">
                  <FiMessageSquare className="w-6 h-6" />
                </button>
              )}
              <button
                onClick={handleBlock}
                className="p-3 rounded-full bg-[#3C3C3E] text-white hover:bg-[#4C4C4E]"
              >
                <FiSlash className="w-6 h-6" />
              </button>
              <button
                onClick={handleReport}
                className="p-3 rounded-full bg-[#3C3C3E] text-red-500 hover:bg-[#4C4C4E]"
              >
                <FiFlag className="w-6 h-6" />
              </button>
            </div>
          </div>

          <div className="flex items-center mb-6">
            {[...Array(5)].map((_, index) => (
              <FiStar
                key={index}
                className={`w-6 h-6 ${index < mockProfile.fameRating
                    ? "text-[#D63384]"
                    : "text-gray-600"
                  }`}
              />
            ))}
          </div>

          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-white mb-2">Hakkında</h2>
              <p className="text-gray-300">{mockProfile.bio}</p>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-white mb-2">İlgi Alanları</h2>
              <div className="flex flex-wrap gap-2">
                {mockProfile.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 rounded-full bg-[#3C3C3E] text-gray-300"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <h3 className="text-gray-400 mb-1">Cinsiyet</h3>
                <p className="text-white">{mockProfile.gender}</p>
              </div>
              <div>
                <h3 className="text-gray-400 mb-1">Tercih</h3>
                <p className="text-white">{mockProfile.preference}</p>
              </div>
            </div>

            <div className="flex items-center text-gray-300">
              <FiClock className="mr-2" />
              {mockProfile.isOnline ? "Çevrimiçi" : mockProfile.lastSeen}
            </div>
          </div>
        </div>

        {/* Photo Gallery */}
        <div className="bg-[#2C2C2E] rounded-xl p-8 mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Fotoğraflar</h2>
          <div className="h-[500px]"> {/* Slider container'ı için sabit yükseklik */}
            <Slider {...sliderSettings}>
              {mockProfile.images.map((image, index) => (
                <div key={index} className="px-2 h-[450px]"> {/* Her slide için yükseklik */}
                  <div
                    className="relative w-full h-full rounded-xl overflow-hidden cursor-pointer"
                    onClick={() => setShowLightbox(true)}
                  >
                    <Image
                      src={image}
                      alt={`Photo ${index + 1}`}
                      fill
                      className="object-cover"
                    />
                  </div>
                </div>
              ))}
            </Slider>
          </div>
        </div>

        {/* Recent Visitors */}
        {mockProfile.recentVisitors.length > 0 && (
          <div className="bg-[#2C2C2E] rounded-xl p-8">
            <h2 className="text-xl font-semibold text-white mb-4">
              Son Ziyaretçiler
            </h2>
            <div className="flex space-x-4">
              {mockProfile.recentVisitors.map((visitor) => (
                <div
                  key={visitor.id}
                  className="w-12 h-12 rounded-full overflow-hidden relative"
                >
                  <Image
                    src={visitor.avatar}
                    alt={visitor.name}
                    fill
                    className="object-cover"
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Block Modal */}
      {showBlockModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#2C2C2E] rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl text-white font-semibold mb-4">Kullanıcıyı Engelle</h3>
            <p className="text-gray-300 mb-6">
              Bu kullanıcıyı engellemek istediğinizden emin misiniz? Engellediğiniz kullanıcılar sizinle iletişim kuramaz.
            </p>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setShowBlockModal(false)}
                className="px-4 py-2 text-gray-300 hover:text-white"
              >
                İptal
              </button>
              <button
                onClick={confirmBlock}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                Engelle
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Report Modal */}
      {showReportModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#2C2C2E] rounded-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl text-white font-semibold mb-4">Kullanıcıyı Raporla</h3>

            <div className="mb-4">
              <label className="block text-gray-300 mb-2">Raporlama Nedeni</label>
              <select
                value={reportReason}
                onChange={(e) => setReportReason(e.target.value)}
                className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2"
              >
                <option value="">Seçiniz</option>
                <option value="spam">Spam</option>
                <option value="harassment">Taciz</option>
                <option value="inappropriate">Uygunsuz İçerik</option>
                <option value="fake">Sahte Profil</option>
                <option value="other">Diğer</option>
              </select>
            </div>

            <div className="mb-6">
              <label className="block text-gray-300 mb-2">Açıklama</label>
              <textarea
                value={reportDescription}
                onChange={(e) => setReportDescription(e.target.value)}
                className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 min-h-[100px]"
                placeholder="Lütfen detaylı açıklama yapınız..."
              />
            </div>

            <div className="flex justify-end space-x-4">
              <button
                onClick={() => {
                  setShowReportModal(false);
                  setReportReason("");
                  setReportDescription("");
                }}
                className="px-4 py-2 text-gray-300 hover:text-white"
              >
                İptal
              </button>
              <button
                onClick={submitReport}
                disabled={!reportReason || !reportDescription}
                className="px-4 py-2 bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white rounded-lg hover:opacity-90 disabled:opacity-50"
              >
                Raporla
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Lightbox */}
      {showLightbox && (
        <div
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center"
          onClick={() => setShowLightbox(false)}
        >
          <Image
            src={mockProfile.images[currentSlide]}
            alt="Full size"
            width={800}
            height={600}
            className="max-w-full max-h-[90vh] object-contain"
          />
        </div>
      )}
    </section>
  );
};

export default ProfilePage;