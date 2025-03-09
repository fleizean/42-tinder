"use client";

import { useState } from "react";
import Image from "next/image";
import { FiHeart, FiMapPin, FiStar, FiTag, FiFilter } from "react-icons/fi";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";

interface Profile {
  id: string;
  name: string;
  age: number;
  image: string;
  fameRating: number;
  distance: number;
  tags: string[];
  location: string;
}

const Dashboard = () => {
  const [ageRange, setAgeRange] = useState([18, 99]);
  const [fameRating, setFameRating] = useState([1, 5]);
  const [distance, setDistance] = useState(100);
  const [tags, setTags] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState('distance');
  const [profiles, setProfiles] = useState([]);

  return (
    <section className="pt-16 md:pt-20 lg:pt-28 bg-[#1E1E1E]">
      <div className="container mx-auto px-4">
        <div className="flex flex-wrap">
          {/* Filter Sidebar */}
          <div className="w-full lg:w-1/4 mb-8 lg:mb-0">
            <div className="bg-[#2C2C2E] rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-6">Filtreler</h3>
              
              <div className="mb-6">
                <label className="text-gray-300 mb-2 block">Yaş Aralığı</label>
                <Slider
                  range
                  min={16}
                  max={99}
                  value={ageRange}
                  onChange={(value: number[]) => setAgeRange(value)}
                  className="mb-2"
                  railStyle={{ backgroundColor: '#3C3C3E' }}
                  trackStyle={[{ backgroundColor: '#D63384' }]}
                  handleStyle={[
                    { borderColor: '#8A2BE2', backgroundColor: '#8A2BE2' },
                    { borderColor: '#D63384', backgroundColor: '#D63384' }
                  ]}
                />
                <div className="text-gray-400 text-sm">
                  {ageRange[0]} - {ageRange[1]} yaş
                </div>
              </div>

              <div className="mb-6">
                <label className="text-gray-300 mb-2 block">Fame Rating</label>
                <Slider
                  range
                  min={1}
                  max={5}
                  value={fameRating}
                  onChange={(value: number[]) => setFameRating(value)}
                  className="mb-2"
                  railStyle={{ backgroundColor: '#3C3C3E' }}
                  trackStyle={[{ backgroundColor: '#D63384' }]}
                  handleStyle={[
                    { borderColor: '#8A2BE2', backgroundColor: '#8A2BE2' },
                    { borderColor: '#D63384', backgroundColor: '#D63384' }
                  ]}
                />
                <div className="text-gray-400 text-sm">
                  {fameRating[0]} - {fameRating[1]} yıldız
                </div>
              </div>

              <div className="mb-6">
                <label className="text-gray-300 mb-2 block">Mesafe (km)</label>
                <Slider
                  min={0}
                  max={5000}
                  value={distance}
                  onChange={(value: number) => setDistance(value)}
                  className="mb-2"
                  railStyle={{ backgroundColor: '#3C3C3E' }}
                  trackStyle={{ backgroundColor: '#D63384' }}
                  handleStyle={[
                    { borderColor: '#8A2BE2', backgroundColor: '#8A2BE2' },
                    { borderColor: '#D63384', backgroundColor: '#D63384' }
                  ]}
                />
                <div className="text-gray-400 text-sm">{distance} km</div>
              </div>

              <div className="mb-6">
                <label className="text-gray-300 mb-2 block">Etiketler</label>
                <input
                  type="text"
                  className="w-full bg-[#3C3C3E] border-none rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-[#D63384] outline-none"
                  placeholder="Etiket ekle..."
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      const value = e.currentTarget.value.trim();
                      if (value && !tags.includes(value)) {
                        setTags([...tags, value]);
                        e.currentTarget.value = '';
                      }
                    }
                  }}
                />
                <div className="flex flex-wrap gap-2 mt-2">
                  {tags.map((tag, index) => (
                    <span
                      key={index}
                      className="bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white px-3 py-1 rounded-full text-sm flex items-center"
                    >
                      {tag}
                      <button
                        onClick={() => setTags(tags.filter((_, i) => i !== index))}
                        className="ml-2"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <button className="w-full bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 hover:scale-[1.02]">
                Eşleştir
              </button>
            </div>
          </div>

          {/* Profile Cards Section */}
          <div className="w-full lg:w-3/4 lg:pl-12">
            {/* Sorting Buttons */}
            <div className="grid grid-cols-4 gap-4 mb-12">
              {['Mesafe', 'Rating', 'Konum', 'Etiket'].map((sort) => (
                <button
                  key={sort}
                  className={`w-full px-4 py-3 rounded-lg font-medium transition-all duration-300
                    ${sortBy === sort.toLowerCase() 
                      ? 'bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white'
                      : 'bg-[#2C2C2E] text-gray-300 hover:bg-[#3C3C3E]'
                    }`}
                  onClick={() => setSortBy(sort.toLowerCase())}
                >
                  {sort}
                </button>
              ))}
            </div>

            {/* Profile Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Example Profile Card */}
              <div className="bg-[#2C2C2E] rounded-xl overflow-hidden">
                <div className="relative h-48">
                  <Image
                    src="https://images7.alphacoders.com/121/1218824.jpg"
                    alt="Profile"
                    fill
                    className="object-cover"
                  />
                  <button className="absolute top-4 right-4 bg-white/10 backdrop-blur-md p-2 rounded-full hover:bg-white/20 transition-all duration-300">
                    <FiHeart className="w-6 h-6 text-white" />
                  </button>
                </div>
                <div className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-xl font-semibold text-white">Ayşe, 24</h3>
                    <div className="flex items-center">
                      <FiStar className="w-4 h-4 text-[#D63384]" />
                      <span className="text-gray-300 ml-1">4</span>
                    </div>
                  </div>
                  <div className="flex items-center text-gray-300 text-sm mb-3">
                    <FiMapPin className="w-4 h-4 mr-1" />
                    <span>2.5 km uzakta</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {['Müzik', 'Seyahat', 'Spor'].map((tag) => (
                      <span
                        key={tag}
                        className="bg-[#3C3C3E] text-gray-300 px-2 py-1 rounded-full text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Dashboard;