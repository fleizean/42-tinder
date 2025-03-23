"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Image from "next/image";
import { FiHeart, FiMapPin, FiStar, FiTag, FiFilter, FiMoreHorizontal } from "react-icons/fi";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";
import { useSession } from "next-auth/react";
import toast from "react-hot-toast";
import Link from "next/link";
import { useRouter } from "next/navigation";

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

const Match = () => {
  const router = useRouter();
  const DEFAULT_MIN_AGE = 18;
  const DEFAULT_MAX_AGE = 99;
  const DEFAULT_MIN_FAME = 0;
  const DEFAULT_MAX_FAME = 5;
  const DEFAULT_MAX_DISTANCE = 20000;
  const [ageRange, setAgeRange] = useState([DEFAULT_MIN_AGE, DEFAULT_MAX_AGE]);
  const [fameRating, setFameRating] = useState([DEFAULT_MIN_FAME, DEFAULT_MAX_FAME]);
  const [tags, setTags] = useState<string[]>([]);
  const { data: session } = useSession();
  const [profiles, setProfiles] = useState<SuggestedProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(0);
  const [filters, setFilters] = useState<FilterState>({
    min_age: DEFAULT_MIN_AGE,
    max_age: DEFAULT_MAX_AGE,
    min_fame: DEFAULT_MIN_FAME,
    max_fame: DEFAULT_MAX_FAME,
    max_distance: DEFAULT_MAX_DISTANCE,
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
  const [loadedProfileIds, setLoadedProfileIds] = useState<Set<string>>(new Set());

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
    { label: "20000 km (Dünya geneli)", value: 20000 }
  ];
  const [distance, setDistance] = useState(DEFAULT_MAX_DISTANCE); // Başlangıç değeri olarak 50km

  // handleFilterSubmit fonksiyonunu güncelle
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
    setPage(0);
    setLoadedProfileIds(new Set()); // Yüklenen profiller listesini sıfırla
  };

  useEffect(() => {
    setAgeRange([filters.min_age, filters.max_age]);
  }, []);

  const observer = useRef<IntersectionObserver>();
  // Bu ref son eleman görünür olduğunda tetiklenir
  const lastProfileRef = useCallback((node: HTMLDivElement) => {
    if (isLoading) return;
    if (observer.current) observer.current.disconnect();

    observer.current = new IntersectionObserver(entries => {
      // Kullanıcı sayfanın sonuna geldiğinde ve daha fazla veri varsa
      if (entries[0].isIntersecting && hasMore) {
        setPage(prev => prev + 1);  // Sayfa numarasını artır
      }
    });

    if (node) observer.current.observe(node);
  }, [isLoading, hasMore]);

  useEffect(() => {
    const initializeData = async () => {
      if (session?.user?.accessToken) {
        setIsLoading(true);
        // Önce kullanıcı profilini getir
        await fetchUserProfile();

        // Sonra diğer işlemleri yap
        setPage(0);
        setLoadedProfileIds(new Set());
        await fetchProfiles();
      }
    };

    initializeData();
  }, [session, filters]);

  // fetchUserProfile fonksiyonunu Promise döndürecek şekilde güncelleyelim
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

      return data; // Veriyi döndür
    } catch (error) {
      console.error('Error fetching user profile:', error);
      toast.error('Kullanıcı konumu alınamadı');
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

  useEffect(() => {
    const checkLikedProfiles = async () => {
      if (!session?.user?.accessToken || profiles.length === 0) return;

      try {
        // Her profil için beğeni durumunu kontrol et
        const likedStatusPromises = profiles.map(async (profile) => {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/profiles/me/is-liked/${profile.username}`,
            {
              headers: {
                'Authorization': `Bearer ${session.user.accessToken}`,
                'Content-Type': 'application/json',
              }
            }
          );

          if (response.ok) {
            const data = await response.json();
            return { profileId: profile.id, isLiked: data.is_liked };
          }
          return { profileId: profile.id, isLiked: false };
        });

        const likedStatuses = await Promise.all(likedStatusPromises);

        // Beğenilen profilleri Set'e ekle
        const newLikedProfiles = new Set<string>();
        likedStatuses.forEach(status => {
          if (status.isLiked) {
            newLikedProfiles.add(status.profileId);
          }
        });

        setLikedProfiles(newLikedProfiles);
      } catch (error) {
        console.error('Error checking liked profiles:', error);
      }
    };

    checkLikedProfiles();
  }, [profiles, session]);

  // Sayfa yüklendiğinde kullanıcı profilini getir


  
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
  
      // Filtre parametrelerini ekle
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
  
      // Hata kontrolü - daha detaylı debug logları
      if (!response.ok) {
        const responseText = await response.text(); // Önce text olarak yanıtı al
        console.log("API Hata yanıtı:", responseText);
        
        // Ardından JSON olarak parse etmeyi dene
        let errorMessage;
        try {
          const errorData = JSON.parse(responseText);
          console.log("Parse edilen hata:", errorData);
          
          // API'den dönen detail bilgisine göre hata mesajını oluştur
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map(err => err.msg || JSON.stringify(err)).join(', ');
          } else if (errorData.detail && typeof errorData.detail === 'object') {
            errorMessage = JSON.stringify(errorData.detail);
          } else {
            errorMessage = `Profiller yüklenirken bir hata oluştu: ${response.status}`;
          }
        } catch (parseError) {
          console.error("JSON parse hatası:", parseError);
          errorMessage = `Profiller yüklenirken bir hata oluştu: ${response.status} - ${response.statusText}`;
        }
        
        // Özel durumları kontrol et
        if (errorMessage.includes("profilinizi tamamlayın")) {
          // Benzersiz ID ile toast göster
          toast.dismiss('profile-incomplete-toast');
          toast.error("Lütfen profilinizi tamamlayın", { 
            id: 'profile-incomplete-toast',
            duration: 5000,
            position: 'top-center'
          });
          
          // Yönlendirme işlemi
          setTimeout(() => {
            router.push('/settings');
          }, 500);
          
          return; // Fonksiyondan çık
        }
        
        throw new Error(errorMessage);
      }
  
      const data = await response.json();
  
      // Geri kalan kod değişmeden kalabilir...
      const uniqueNewProfiles = data.filter((profile: SuggestedProfile) =>
        !loadedProfileIds.has(profile.id)
      );
  
      if (uniqueNewProfiles.length === 0) {
        setHasMore(false);
        return;
      }
  
      const updatedProfileIds = new Set(loadedProfileIds);
      uniqueNewProfiles.forEach((profile: SuggestedProfile) => {
        updatedProfileIds.add(profile.id);
      });
      setLoadedProfileIds(updatedProfileIds);
  
      setProfiles(prev =>
        page === 0 ? uniqueNewProfiles : [...prev, ...uniqueNewProfiles]
      );
  
      setHasMore(data.length === 10);
  
    } catch (error) {
      console.error("Profil yükleme hatası:", error);
      
      // Benzersiz ID ile toast göster
      toast.dismiss('profile-loading-error');
      try {
        toast.error(error instanceof Error ? error.message : 'Profiller yüklenirken bir hata oluştu', {
          id: 'profile-loading-error',
          duration: 4000
        });
      } catch (toastError) {
        console.error("Toast hatası:", toastError);
      }
      
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
  if (!session?.user?.accessToken) return;
  
  const initializeData = async () => {
    setIsLoading(true);
    await fetchUserProfile();
    setPage(0);
    setLoadedProfileIds(new Set());
    await fetchProfiles();
  };
  
  // SESSION DEĞIŞTIĞINDE VE FILTERS DEĞİŞTİĞİNDE ÇALIŞIR
  initializeData();

  // Page değişikliği için bağımsız useEffect kullanacağız
}, [session, filters]);

  // Filtreler değiştiğinde ayrı bir useEffect kullanın
  useEffect(() => {
    if (page > 0 && session?.user?.accessToken) {
      fetchProfiles();
    }
  }, [page]);

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

  const resetFilters = () => {
    setFilters({
      min_age: DEFAULT_MIN_AGE,
      max_age: DEFAULT_MAX_AGE,
      min_fame: DEFAULT_MIN_FAME,
      max_fame: DEFAULT_MAX_FAME,
      max_distance: DEFAULT_MAX_DISTANCE,
      tags: []
    });
    setAgeRange([DEFAULT_MIN_AGE, DEFAULT_MAX_AGE]);
    setFameRating([DEFAULT_MIN_FAME, DEFAULT_MAX_FAME]);
    setDistance(DEFAULT_MAX_DISTANCE);
    setTags([]);
    setFiltersApplied(false);
    setPage(0);
    setLoadedProfileIds(new Set());
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
                <label className="text-gray-300 mb-2 block">Popülerlik</label>
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
                      className={`text-xs py-1 px-2 rounded ${distance === option.value
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
                <div className="flex justify-between items-center mb-2">
                  <label className="text-gray-300 block">Etiketler</label>
                  {tags.length > 0 && (
                    <button
                      onClick={() => {
                        setTags([]);
                        toast.success('Tüm etiketler temizlendi');
                      }}
                      className="text-xs text-pink-400 hover:text-pink-300 transition-colors"
                    >
                      Hepsini Temizle
                    </button>
                  )}
                </div>
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
              </div>{/* Biography with character limit and visual treatment */}

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
            {isLoading ? (
              <div className="flex justify-center items-center h-60">
                <div className="animate-pulse flex flex-col items-center">
                  <div className="h-10 w-10 border-4 border-t-transparent border-[#D63384] rounded-full animate-spin mb-4"></div>
                  <p className="text-gray-300 font-medium">Profiller yükleniyor...</p>
                </div>
              </div>
            ) : (
              <>
                {profiles.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-60 text-center p-8 bg-[#2C2C2E] rounded-xl">
                    <div className="text-gray-300 text-xl mb-2">Bu filtrelere uygun profil bulunamadı</div>
                    <div className="text-gray-400 mb-4">Farklı filtre seçeneklerini deneyebilirsiniz</div>
                    <button
                      onClick={resetFilters}
                      className="px-6 py-2 bg-gradient-to-r from-[#8A2BE2] to-[#D63384] text-white rounded-lg hover:opacity-90 transition-opacity"
                    >
                      Filtreleri Sıfırla
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {sortProfiles(profiles).map((profile, index) => (
                        <div
                          key={profile.id}
                          ref={index === profiles.length - 1 ? lastProfileRef : null}
                          className="bg-[#2C2C2E] rounded-xl overflow-hidden"
                        >
                          <Link href={`/profile/${profile.username}`}>
                            <div className="relative h-48 group">
                              <Image
                                src={profile.pictures.find(p => p.is_primary)?.backend_url || '/images/defaults/profile-default.jpg'}
                                alt={`${profile.first_name}'s profile`}
                                fill
                                priority
                                sizes="100%"
                                className="object-cover"
                                unoptimized
                              />
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
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
                          </Link>
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
                            <div className="relative mb-3">
                              <p className="text-gray-300 text-sm line-clamp-2">
                                {profile.biography || "Henüz bir biyografi eklenmemiş."}
                              </p>
                              {profile.biography && profile.biography.length > 100 && (
                                <div className="absolute bottom-0 right-0 bg-gradient-to-l from-[#2C2C2E] to-transparent pl-2 pr-1">
                                  <Link href={`/profile/${profile.username}`}>
                                    <FiMoreHorizontal className="w-4 h-4 text-gray" />
                                  </Link>
                                </div>
                              )}
                            </div>

                            {/* Location */}
                            <div className="flex items-center text-gray-400 text-sm mb-3">
                              <FiMapPin className="w-4 h-4 mr-1" />
                              <span>
                                {userProfile ? (
                                  formatDistance(calculateDistance(
                                    userProfile.latitude,
                                    userProfile.longitude,
                                    profile.latitude,
                                    profile.longitude
                                  ))
                                ) : (
                                  <span className="flex items-center">
                                    <div className="w-3 h-3 mr-1 rounded-full border-2 border-t-0 border-l-0 border-[#D63384] animate-spin"></div>
                                    Konum alınıyor...
                                  </span>
                                )}
                              </span>
                            </div>

                            {/* Tags */}
                            <div className="flex flex-wrap gap-2 mb-4">
                              {profile.tags.map((tag, i) => (
                                <span
                                  key={i}
                                  className="text-xs bg-[#3C3C3E] text-gray-300 px-2 py-1 rounded-full cursor-pointer hover:bg-[#4C4C4E] transition-colors"
                                  onClick={(e) => {
                                    e.preventDefault(); // Prevent navigation to profile page
                                    e.stopPropagation(); // Stop event propagation

                                    // Only add the tag if it's not already in the filters
                                    if (!tags.includes(tag.name)) {
                                      setTags([...tags, tag.name]);
                                      toast.success(`'${tag.name}' etiketi filtrelere eklendi`);
                                    } else {
                                      toast.error(`'${tag.name}' etiketi zaten eklenmiş`);
                                    }
                                  }}
                                >
                                  #{tag.name}
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

                    {/* Buraya da "loadMore" spinner'ı ve "Tüm profiller yüklendi" mesajları */}
                    {hasMore && (
                      <div className="flex justify-center items-center py-8" ref={lastProfileRef}>
                        <div className="animate-pulse flex flex-col items-center">
                          <div className="h-8 w-8 border-t-2 border-b-2 border-[#D63384] rounded-full animate-spin mb-2"></div>
                          <p className="text-gray-400">Yeni profiller aranıyor...</p>
                        </div>
                      </div>
                    )}

                    {!hasMore && !isLoading && (
                      <div className="text-center py-8 text-gray-400">
                        <p className="mb-1">Tüm profiller yüklendi ({profiles.length})</p>
                        <p className="text-sm">Filtreleri değiştirerek daha fazla profil bulabilirsiniz</p>
                      </div>
                    )}
                  </>
                )}
              </>
            )}

          </div>
        </div>
      </div>
    </section>
  );
};

export default Match;