"use client";

import { useState, useRef,useEffect } from "react";
import Image from "next/image";
import { FiUpload, FiX, FiTag, FiFile } from "react-icons/fi";
import { Metadata } from 'next';

const metadata: Metadata = {
    title: 'Profil Bilgileri | CrushIt',
    description: 'CrushIt profil bilgileri ve ayarları.',
};


interface FormData {
  images: string[];
  birthDate: string;
  gender: string;
  preference: string;
  tags: string[];
  biography: string;
  location: {
    latitude: number | null;
    longitude: number | null;
    city?: string;
    country?: string;
  };
}

const FirstTimeSetup = () => {
  const [formData, setFormData] = useState<FormData>({
    images: [],
    birthDate: "",
    gender: "",
    preference: "",
    tags: [],
    biography: "",
    location: {
      latitude: null,
      longitude: null
    }
  });

  const [locationError, setLocationError] = useState<string>("");
  const [isLocating, setIsLocating] = useState(false);

  const getLocationByIP = async () => {
    try {
      const response = await fetch('https://ipapi.co/json/');
      const data = await response.json();
      setFormData(prev => ({
        ...prev,
        location: {
          latitude: data.latitude,
          longitude: data.longitude,
          city: data.city,
          country: data.country_name
        }
      }));
    } catch (error) {
      setLocationError("Konum bilgisi alınamadı.");
    }
  };

  const requestGeolocation = () => {
    setIsLocating(true);
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        // Success
        async (position) => {
          try {
            // Reverse geocoding to get city and country
            const response = await fetch(
              `https://nominatim.openstreetmap.org/reverse?format=json&lat=${position.coords.latitude}&lon=${position.coords.longitude}`
            );
            const data = await response.json();
            
            setFormData(prev => ({
              ...prev,
              location: {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                city: data.address.city || data.address.town,
                country: data.address.country
              }
            }));
            setLocationError("");
          } catch (error) {
            getLocationByIP();
          }
        },
        // Error
        (error) => {
          getLocationByIP();
        }
      );
    } else {
      getLocationByIP();
    }
    setIsLocating(false);
  };

  useEffect(() => {
    requestGeolocation();
  }, []);

  // Add this section in the form after the biography section
  const locationSection = (
    <div>
      <label className="block text-white mb-2">Konum</label>
      <div className="bg-[#3C3C3E] rounded-lg p-4">
        {isLocating ? (
          <div className="text-gray-300">Konum bulunuyor...</div>
        ) : formData.location.latitude && formData.location.longitude ? (
          <div className="text-gray-300">
            <p>{formData.location.city}, {formData.location.country}</p>
            <p className="text-sm text-gray-400">
              ({formData.location.latitude.toFixed(6)}, {formData.location.longitude.toFixed(6)})
            </p>
          </div>
        ) : (
          <div className="text-gray-300">
            {locationError || "Konum bilgisi bulunamadı"}
          </div>
        )}
        <button
          type="button"
          onClick={requestGeolocation}
          className="mt-2 px-4 py-2 bg-[#4C4C4E] text-white rounded-lg hover:bg-[#5C5C5E] transition-colors"
        >
          Konumu Güncelle
        </button>
      </div>
    </div>
  );

  useEffect(() => {
          document.title = metadata.title as string;
      }, []);

  const [isLoading, setIsLoading] = useState(false);
  const [currentTag, setCurrentTag] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && formData.images.length < 5) {
      const file = files[0];
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData(prev => ({
          ...prev,
          images: [...prev.images, reader.result as string]
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // API call logic here
    setIsLoading(false);
  };

  return (
    <section className="pt-[150px] pb-[120px] bg-[#1C1C1E]">
    <div className="min-h-screen bg-[#1C1C1E] py-16">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-white mb-8 text-center">Profil Bilgilerinizi Tamamlayın</h1>
        
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Image Upload */}
          <div className="bg-[#2C2C2E] p-6 rounded-xl">
            <h2 className="text-xl text-white mb-4">Profil Fotoğrafları</h2>
            <div className="grid grid-cols-5 gap-4 mb-4">
              {formData.images.map((img, index) => (
                <div key={index} className="relative aspect-square">
                  <Image
                    src={img}
                    alt={`Profile ${index + 1}`}
                    fill
                    className="object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => setFormData(prev => ({
                      ...prev,
                      images: prev.images.filter((_, i) => i !== index)
                    }))}
                    className="absolute -top-2 -right-2 bg-red-500 rounded-full p-1"
                  >
                    <FiX className="text-white" />
                  </button>
                </div>
              ))}
              {formData.images.length < 5 && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="aspect-square bg-[#3C3C3E] rounded-lg flex items-center justify-center"
                >
                  <FiUpload className="text-gray-400 w-8 h-8" />
                </button>
              )}
            </div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleImageUpload}
              className="hidden"
              accept="image/*"
            />
            <p className="text-purple-500 flex items-center">
              <FiFile className="mr-2" /> 
              İlk fotoğrafınız profil fotoğrafı, ikinci fotoğrafınız ise kapak fotoğrafı olarak kullanılacaktır.
            </p>          
          </div>

          {/* Personal Info */}
          <div className="bg-[#2C2C2E] p-6 rounded-xl space-y-6">
            <div>
              <label className="block text-white mb-2">Doğum Tarihi</label>
              <input
                type="date"
                value={formData.birthDate}
                onChange={e => setFormData(prev => ({ ...prev, birthDate: e.target.value }))}
                className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2"
              />
            </div>

            <div>
              <label className="block text-white mb-2">Cinsiyet</label>
              <select
                value={formData.gender}
                onChange={e => setFormData(prev => ({ ...prev, gender: e.target.value }))}
                className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2"
              >
                <option value="">Seçiniz</option>
                <option value="male">Erkek</option>
                <option value="female">Kadın</option>
                <option value="other">Diğer</option>
              </select>
            </div>

            <div>
              <label className="block text-white mb-2">Cinsiyet Tercihi</label>
              <select
                value={formData.preference}
                onChange={e => setFormData(prev => ({ ...prev, preference: e.target.value }))}
                className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2"
              >
                <option value="">Seçiniz</option>
                <option value="male">Erkek</option>
                <option value="female">Kadın</option>
                <option value="both">Her ikisi</option>
              </select>
            </div>

            <div>
              <label className="block text-white mb-2">Etiketler</label>
              <div className="flex flex-wrap gap-2 mb-2">
                {formData.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white px-3 py-1 rounded-full text-sm flex items-center"
                  >
                    {tag}
                    <button
                      type="button"
                      onClick={() => setFormData(prev => ({
                        ...prev,
                        tags: prev.tags.filter((_, i) => i !== index)
                      }))}
                      className="ml-2"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <input
                type="text"
                value={currentTag}
                onChange={e => setCurrentTag(e.target.value)}
                onKeyPress={e => {
                  if (e.key === 'Enter' && currentTag.trim()) {
                    e.preventDefault();
                    setFormData(prev => ({
                      ...prev,
                      tags: [...prev.tags, currentTag.trim()]
                    }));
                    setCurrentTag("");
                  }
                }}
                className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2"
                placeholder="Etiket eklemek için yazın ve Enter'a basın"
              />
            </div>

            {locationSection}

            <div>
              <label className="block text-white mb-2">Biyografi</label>
              <textarea
                value={formData.biography}
                onChange={e => setFormData(prev => ({ ...prev, biography: e.target.value }))}
                className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 min-h-[150px]"
                placeholder="Kendinizden bahsedin..."
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 hover:scale-[1.02] disabled:opacity-50"
          >
            {isLoading ? "Kaydediliyor..." : "Kaydet"}
          </button>
        </form>
      </div>
    </div>
    </section>
  );
};

export default FirstTimeSetup;