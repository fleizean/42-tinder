"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Image from "next/image";
import { FiHeart, FiMapPin, FiStar, FiTag, FiFilter } from "react-icons/fi";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";
import { useSession } from "next-auth/react";
import toast from "react-hot-toast";

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
interface SuggestedProfile {
  id: string;
  username: string;
  first_name: string;
  last_name: string;
  gender: string;
  sexual_preference: string;
  biography: string;
  latitude: number;
  longitude: number;
  fame_rating: number;
  is_online: boolean;
  last_online: string;
  pictures: {
    id: number;  // Changed from string to number based on your response
    profile_id: string;
    file_path: string;
    backend_url: string;
    is_primary: boolean;
    created_at: string;
  }[];
  tags: {  // Update to match the actual structure
    id: number;
    name: string;
  }[];
  birth_date: string;
}

interface FilterState {
  min_age: number;
  max_age: number;
  min_fame: number;
  max_fame: number;
  max_distance: number;
  tags: string[];
}

enum SortOption {
  AGE_ASC = 'age_asc',
  AGE_DESC = 'age_desc',
  DISTANCE = 'distance',
  FAME_RATING = 'fame_rating',
  TAGS_MATCH = 'tags_match'
}

const Dashboard = () => {
  const [ageRange, setAgeRange] = useState([18, 99]);
  const [fameRating, setFameRating] = useState([0, 5]);
  const [tags, setTags] = useState<string[]>([]);
  const { data: session } = useSession();
  const [profiles, setProfiles] = useState<SuggestedProfile[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const [filters, setFilters] = useState<FilterState>({
    min_age: 18,
    max_age: 99,
    min_fame: 0,
    max_fame: 5,
    max_distance: 5000,
    tags: []
  });
  const [likedProfiles, setLikedProfiles] = useState<Set<string>>(new Set());
  const [isLikeLoading, setIsLikeLoading] = useState<string | null>(null);
  const [filtersApplied, setFiltersApplied] = useState(false);
  const [sortBy, setSortBy] = useState<SortOption>(SortOption.DISTANCE);
  const [userProfile, setUserProfile] = useState<{
    latitude: number;
    longitude: number;
  } | null>(null);

    const distanceOptions = [
    { label: "5 km (Aynı mahalle)", value: 5 },
    { label: "10 km (Yakın semtler)", value: 10 },
    { label: "25 km (Aynı şehir)", value: 25 },
    { label: "50 km (Şehir ve çevresi)", value: 50 },
    { label: "100 km (Komşu şehirler)", value: 100 },
    { label: "250 km (Aynı bölge)", value: 250 },
    { label: "500 km (Bölgeler arası)", value: 500 },
    { label: "1000 km (Ülke geneli)", value: 1000 },
    { label: "2500 km (Komşu ülkeler)", value: 2500 },
    { label: "5000 km (Kıtasal)", value: 5000 },
    { label: "10000 km (Global)", value: 10000 },
    { label: "15000 km (Dünya geneli)", value: 15000 }
  ];
  const [distance, setDistance] = useState(50); // Başlangıç değeri olarak 50km

  // Update filter submit to set the filtersApplied flag
  const handleFilterSubmit = () => {
    setFilters({
      min_age: ageRange[0],
      max_age: ageRange[1],
      min_fame: fameRating[0],
      max_fame: fameRating[1],
      max_distance: distance,
      tags: tags
    });
    setFiltersApplied(true);
    setPage(0); // Reset page for new filters
  };

  useEffect(() => {
    setAgeRange([filters.min_age, filters.max_age]);
  }, []);

  const observer = useRef<IntersectionObserver>();
  const lastProfileRef = useCallback((node: HTMLDivElement) => {
    if (isLoading) return;
    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prev => prev + 1);
      }
    });

    if (node) observer.current.observe(node);
  }, [isLoading, hasMore]);

  const fetchUserProfile = async () => {
    if (!session?.user?.accessToken) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/profiles/me`,
        {
          headers: {
            'Authorization': `Bearer ${session.user.accessToken}`,
            'Content-Type': 'application/json',
          }
        }
      );

      if (!response.ok) throw new Error('Failed to fetch user profile');

      const data = await response.json();
      setUserProfile({
        latitude: data.latitude,
        longitude: data.longitude
      });
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const sortProfiles = (profiles: SuggestedProfile[]): SuggestedProfile[] => {
    // Profillerin bir kopyasını oluştur
    const sortedProfiles = [...profiles];
    
    switch (sortBy) {
      case SortOption.AGE_ASC:
        return sortedProfiles.sort((a, b) => 
          calculateAge(a.birth_date) - calculateAge(b.birth_date)
        );
      case SortOption.AGE_DESC:
        return sortedProfiles.sort((a, b) => 
          calculateAge(b.birth_date) - calculateAge(a.birth_date)
        );
      case SortOption.DISTANCE:
        if (userProfile) {
          return sortedProfiles.sort((a, b) => 
            calculateDistance(userProfile.latitude, userProfile.longitude, a.latitude, a.longitude) - 
            calculateDistance(userProfile.latitude, userProfile.longitude, b.latitude, b.longitude)
          );
        }
        return sortedProfiles;
      case SortOption.FAME_RATING:
        return sortedProfiles.sort((a, b) => b.fame_rating - a.fame_rating);
      case SortOption.TAGS_MATCH:
        // Kullanıcının etiketleriyle eşleşme sayısına göre sırala
        return sortedProfiles.sort((a, b) => {
          const aMatches = a.tags.filter(tag => tags.includes(tag.name)).length;
          const bMatches = b.tags.filter(tag => tags.includes(tag.name)).length;
          return bMatches - aMatches;
        });
      default:
        return sortedProfiles;
    }
  };

  // Sayfa yüklendiğinde kullanıcı profilini getir
  useEffect(() => {
    if (session?.user?.accessToken) {
      fetchUserProfile();
    }
  }, [session]);

  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371; // Dünya'nın yarıçapı (km)
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c; // Kilometre cinsinden mesafe
    return Math.round(distance); // En yakın tam sayıya yuvarla
  };

  // formatDistance fonksiyonu mesafeyi daha okunabilir hale getirir
  const formatDistance = (distance: number): string => {
    if (distance < 1) {
      return `${Math.round(distance * 1000)} m uzaklıkta`; // 1 km'den azsa metre cinsinden göster
    } else {
      return `${distance} km uzaklıkta`;
    }
  };

  const fetchProfiles = async () => {
    try {
      setIsLoading(true);
      const queryParams = new URLSearchParams({
        limit: '10',
        offset: (page * 10).toString(),
      });

      if (page > 0 || filtersApplied) {
        queryParams.append('min_age', filters.min_age.toString());
        queryParams.append('max_age', filters.max_age.toString());
        queryParams.append('min_fame', filters.min_fame.toString());
        queryParams.append('max_fame', filters.max_fame.toString());
        queryParams.append('max_distance', filters.max_distance.toString());

        if (filters.tags.length > 0) {
          filters.tags.forEach(tag => {
            queryParams.append('tags', tag);
          });
        }
      }


      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/profiles/suggested?${queryParams}`,
        {
          headers: {
            'Authorization': `Bearer ${session?.user?.accessToken}`,
            'Content-Type': 'application/json',
          }
        }
      );

      if (!response.ok) throw new Error('Failed to fetch profiles');

      const data = await response.json();
      setProfiles(prev => page === 0 ? data : [...prev, ...data]);
      setHasMore(data.length === 10);

    } catch (error) {
      console.error('Error fetching profiles:', error);
      toast.error('Profiller yüklenirken bir hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (session?.user?.accessToken) {
      setPage(0);
      fetchProfiles();
    }
  }, [session, filters]);

  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters
    }));
    setPage(0);
  };

  const calculateAge = (birthDate: string): number => {
    if (!birthDate) return 0;

    const today = new Date();
    const birth = new Date(birthDate);

    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();

    // Adjust age if birthday hasn't occurred this year
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }

    return age;
  };

  const handleLike = async (profileId: string) => {
    if (isLikeLoading === profileId) return;
    setIsLikeLoading(profileId);

    try {
      const isLiked = likedProfiles.has(profileId);
      const url = `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/interactions/like${isLiked ? `/${profileId}` : ''}`;

      const response = await fetch(url, {
        method: isLiked ? 'DELETE' : 'POST',
        headers: {
          'Authorization': `Bearer ${session?.user?.accessToken}`,
          'Content-Type': 'application/json',
        },
        ...(isLiked ? {} : { body: JSON.stringify({ liked_id: profileId }) })
      });

      if (!response.ok) throw new Error();

      setLikedProfiles(prev => {
        const newSet = new Set(prev);
        isLiked ? newSet.delete(profileId) : newSet.add(profileId);
        return newSet;
      });

      toast.success(isLiked ? 'Beğeni kaldırıldı' : 'Profil beğenildi');

    } catch (error) {
      toast.error('Bir hata oluştu');
    } finally {
      setIsLikeLoading(null);
    }
  };

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
                  min={18}
                  max={99}
                  value={ageRange}  // Use ageRange state
                  onChange={(value: number[]) => {
                    setAgeRange(value);  // Update ageRange state
                    setFilters(prev => ({
                      ...prev,
                      min_age: value[0],
                      max_age: value[1]
                    }));
                  }}
                  onChangeComplete={(value: number[]) => {
                    setPage(0);
                    fetchProfiles();
                  }}
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
                  min={0}
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
                <label className="text-gray-300 mb-2 block">Mesafe</label>
                <div className="mb-2">
                  <Slider
                    min={0}
                    max={distanceOptions.length - 1}
                    value={distanceOptions.findIndex(option => option.value === distance)}
                    onChange={(index: number) => {
                      const selectedDistance = distanceOptions[index].value;
                      setDistance(selectedDistance);
                    }}
                    className="mb-2"
                    railStyle={{ backgroundColor: '#3C3C3E' }}
                    trackStyle={{ backgroundColor: '#D63384' }}
                    handleStyle={[
                      { borderColor: '#8A2BE2', backgroundColor: '#8A2BE2' }
                    ]}
                    marks={distanceOptions.reduce((acc, option, index) => {
                      acc[index] = '';
                      return acc;
                    }, {} as Record<number, string>)}
                  />
                </div>

                <div className="flex justify-between text-gray-400 text-sm">
                  <span>Seçilen mesafe:</span>
                  <span className="font-medium">{distance} km</span>
                </div>

                <div className="grid grid-cols-5 gap-2 mt-3">
                  {distanceOptions.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setDistance(option.value);
                        setFilters(prev => ({
                          ...prev,
                          max_distance: option.value
                        }));
                      }}
                      title={option.label} // Tooltip olarak tüm açıklamayı göster
                      className={`text-xs py-1 px-2 rounded ${
                        distance === option.value
                          ? 'bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white'
                          : 'bg-[#3C3C3E] text-gray-300'
                      } transition-colors`}
                    >
                      {option.value} km
                    </button>
                  ))}
                </div>
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

              <button
                onClick={handleFilterSubmit}
                className="w-full bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 hover:scale-[1.02]"
              >
                Eşleştir
              </button>
            </div>
          </div>

          {/* Profile Cards Section */}
          <div className="w-full lg:w-3/4 lg:pl-12">
           {/* Sıralama seçimi */}
           <div className="flex justify-end mb-4">
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortOption)}
                  className="bg-[#2C2C2E] text-white py-2 pl-3 pr-8 rounded-lg border-none focus:outline-none focus:ring-2 focus:ring-[#D63384] appearance-none"
                >
                  <option value={SortOption.DISTANCE}>Mesafeye göre</option>
                  <option value={SortOption.AGE_ASC}>Yaş (Küçükten büyüğe)</option>
                  <option value={SortOption.AGE_DESC}>Yaş (Büyükten küçüğe)</option>
                  <option value={SortOption.FAME_RATING}>Popülerliğe göre</option>
                  <option value={SortOption.TAGS_MATCH}>Etiket eşleşmesine göre</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sortProfiles(profiles).map((profile, index) => (
                <div
                  key={profile.id}
                  ref={index === profiles.length - 1 ? lastProfileRef : null}
                  className="bg-[#2C2C2E] rounded-xl overflow-hidden"
                >
                  <div className="relative h-48 group">
                    <Image
                      src={profile.pictures.find(p => p.is_primary)?.backend_url || '/images/defaults/profile-default.jpg'}
                      alt={`${profile.first_name}'s profile`}
                      fill
                      className="object-cover"
                    />
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        handleLike(profile.id);
                      }}
                      disabled={isLikeLoading === profile.id}
                      className={`absolute top-2 right-2 p-2 rounded-full transition-all
      ${likedProfiles.has(profile.id)
                          ? 'bg-[#D63384] text-white'
                          : 'bg-white/80 hover:bg-white text-gray-600'}
      ${isLikeLoading === profile.id ? 'opacity-50' : ''}
    `}
                    >
                      <FiHeart
                        className={`w-5 h-5 ${likedProfiles.has(profile.id) ? 'fill-current' : ''}`}
                      />
                    </button>
                  </div>
                  <div className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-xl font-semibold text-white">
                        {profile.first_name}, {calculateAge(profile.birth_date)}
                      </h3>
                      <div className="flex items-center">
                        <FiStar className="w-4 h-4 text-[#D63384]" />
                        <span className="text-gray-300 ml-1">{Math.round(profile.fame_rating)}</span>
                      </div>
                    </div>

                    {/* Biography */}
                    <p className="text-gray-300 text-sm mb-3 line-clamp-2">
                      {profile.biography || "Henüz bir biyografi eklenmemiş."}
                    </p>

                    {/* Location */}
                    <div className="flex items-center text-gray-400 text-sm mb-3">
                      <FiMapPin className="w-4 h-4 mr-1" />
                      <span>
                        {userProfile
                          ? formatDistance(calculateDistance(
                            userProfile.latitude,
                            userProfile.longitude,
                            profile.latitude,
                            profile.longitude
                          ))
                          : "Mesafe hesaplanıyor..."
                        }
                      </span>
                    </div>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {profile.tags.map((tag, i) => (
                        <span
                          key={i}
                          className="text-xs bg-[#3C3C3E] text-gray-300 px-2 py-1 rounded-full"
                        >
                          #{tag.name}  {/* Use tag.name instead of tag */}
                        </span>
                      )).slice(0, 3)}
                      {profile.tags.length > 3 && (
                        <span className="text-xs text-gray-400">
                          +{profile.tags.length - 3}
                        </span>
                      )}
                    </div>


                  </div>
                </div>
              ))}
            </div>
            {isLoading && (
              <div className="flex justify-center mt-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#D63384]"></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Dashboard;