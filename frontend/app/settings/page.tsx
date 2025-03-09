"use client";

import React, { useState, useEffect, useCallback, useRef } from "react";
import Image from "next/image";
import { useSession } from "next-auth/react";
import { FiUser, FiLock, FiEye, FiBell, FiUserX, FiX, FiPlus } from "react-icons/fi";
import { toast, Toaster } from "react-hot-toast";

interface BlockedUser {
  id: string;
  name: string;
  avatar: string;
  blockedDate: string;
}

import { Metadata } from "next";

const metadata: Metadata = {
  title: "Ayarlar | CrushIt",
  description: "CrushIt platformunda profilinizi düzenleyin ve diğer kullanıcıları keşfedin."
};

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState("account");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const { data: session } = useSession();

  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    messageNotifications: true,
    matchNotifications: true,
  });
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const passwordInputRef = useRef(null);
  const handlePasswordChange = async () => {
    if (!currentPassword || !newPassword || !confirmPassword) {
      toast.error("Tüm alanları doldurunuz");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("Yeni şifreler eşleşmiyor");
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.user?.accessToken}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Şifre değiştirme başarısız');
      }

      toast.success('Şifre başarıyla değiştirildi');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      return;
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Bir hata oluştu');
    }
  };



  // Add this handler function:
  const handleDeleteAccount = () => {
    if (!deletePassword) {
      alert("Lütfen şifrenizi girin");
      return;
    }
    // API call would go here
    alert("Hesap silme işlemi başlatıldı");
    setShowDeleteModal(false);
    setDeletePassword("");
  };


  const [profileInfo, setProfileInfo] = useState({
    firstName: "",
    lastName: "",
    username: "",
    email: "",
    tag: "",
    birthDate: "",
    gender: "",
    preference: "",
    location: "",
    biography: "",
    photos: [] as string[]
  });

  const mockBlockedUsers: BlockedUser[] = [
    {
      id: "1",
      name: "Ahmet Yılmaz",
      avatar: "https://images7.alphacoders.com/121/1218824.jpg",
      blockedDate: "2024-03-15",
    },
    {
      id: "2",
      name: "Mehmet Demir",
      avatar: "https://images7.alphacoders.com/110/1104374.jpg",
      blockedDate: "2024-03-14",
    },
  ];

  useEffect(() => {
    document.title = metadata.title as string;
  }, []);


  const handleUnblock = (userId: string) => {
    // API call to unblock user
    alert(`Kullanıcının engeli kaldırıldı: ${userId}`);
  };
  const TabButton = ({ value, icon: Icon, label }: { value: string; icon: any; label: string }) => (
    <button
      onClick={() => setActiveTab(value)}
      className={`w-full flex items-center space-x-2 p-3 text-left rounded-lg transition-colors ${activeTab === value
        ? "bg-[#3C3C3E] text-white"
        : "text-gray-400 hover:bg-[#3C3C3E] hover:text-white"
        }`}
    >
      <Icon />
      <span>{label}</span>
    </button>
  );





  return (
    <section className="pt-[150px] pb-[120px] bg-[#1C1C1E] min-h-screen">
      <Toaster position="top-right" /> 
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-white mb-8">Ayarlar</h1>

        <div className="grid grid-cols-1 lg:grid-cols-[250px_1fr] gap-8">
          {/* Sidebar - existing code */}
          <div className="bg-[#2C2C2E] rounded-xl p-4 space-y-2">
            <TabButton value="account" icon={FiUser} label="Hesap Ayarları" />
            <TabButton value="privacy" icon={FiLock} label="Gizlilik" />
            <TabButton value="notifications" icon={FiBell} label="Bildirimler" />
            <TabButton value="blocked" icon={FiUserX} label="Engellenen Kullanıcılar" />
          </div>
          {/* Content */}
          <div className="bg-[#2C2C2E] rounded-xl p-8">
            {activeTab === "account" && (
              <div>
                <h2 className="text-2xl font-semibold text-white mb-6">Hesap Ayarları</h2>
                <div className="space-y-8">
                  {/* Profile Photos */}
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-4">Profil Fotoğrafları</h3>
                    <div className="grid grid-cols-5 gap-4">
                      {[...Array(5)].map((_, index) => (
                        <div key={index} className="aspect-square rounded-lg bg-[#3C3C3E] overflow-hidden relative">
                          {profileInfo.photos[index] ? (
                            <>
                              <Image
                                src={profileInfo.photos[index]}
                                alt={`Photo ${index + 1}`}
                                fill
                                className="object-cover"
                              />
                              <button
                                onClick={() => {/* Handle photo remove */ }}
                                className="absolute top-2 right-2 p-1 bg-red-500 rounded-full"
                              >
                                <FiX className="text-white" />
                              </button>
                            </>
                          ) : (
                            <label className="flex items-center justify-center h-full cursor-pointer">
                              <input
                                type="file"
                                className="hidden"
                                accept="image/*"
                                onChange={(e) => {/* Handle photo upload */ }}
                              />
                              <FiPlus className="text-gray-400 w-8 h-8" />
                            </label>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Basic Info */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-300 mb-2">İsim</label>
                      <input
                        type="text"
                        value={profileInfo.firstName}
                        onChange={(e) => setProfileInfo({ ...profileInfo, firstName: e.target.value })}
                        placeholder="İsminiz"
                        className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 mb-2">Soyisim</label>
                      <input
                        value={profileInfo.lastName}
                        onChange={(e) => setProfileInfo({ ...profileInfo, lastName: e.target.value })}
                        placeholder="Soyisminiz"
                        className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 mb-2">Kullanıcı Adı</label>
                      <input
                        value={profileInfo.username}
                        onChange={(e) => setProfileInfo({ ...profileInfo, username: e.target.value })}
                        placeholder="Kullanıcı adınız"
                        className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 mb-2">E-posta</label>
                      <input
                        type="email"
                        value={profileInfo.email}
                        onChange={(e) => setProfileInfo({ ...profileInfo, email: e.target.value })}
                        placeholder="E-posta adresiniz"
                        className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                      />
                    </div>
                  </div>

                  {/* Personal Info */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-300 mb-2">Doğum Tarihi</label>
                      <input
                        type="date"
                        value={profileInfo.birthDate}
                        onChange={(e) => setProfileInfo({ ...profileInfo, birthDate: e.target.value })}
                        className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 mb-2">Etiket</label>
                      <input
                        value={profileInfo.tag}
                        onChange={(e) => setProfileInfo({ ...profileInfo, tag: e.target.value })}
                        placeholder="#etiket"
                        className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 mb-2">Cinsiyet</label>
                      <select
                        value={profileInfo.gender}
                        onChange={(e) => setProfileInfo({ ...profileInfo, gender: e.target.value })}
                        className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2"
                      >
                        <option value="">Seçiniz</option>
                        <option value="male">Erkek</option>
                        <option value="female">Kadın</option>
                        <option value="other">Diğer</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-gray-300 mb-2">Cinsiyet Tercihi</label>
                      <select
                        value={profileInfo.preference}
                        onChange={(e) => setProfileInfo({ ...profileInfo, preference: e.target.value })}
                        className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2"
                      >
                        <option value="">Seçiniz</option>
                        <option value="male">Erkek</option>
                        <option value="female">Kadın</option>
                        <option value="both">Her ikisi</option>
                      </select>
                    </div>
                  </div>

                  {/* Location & Bio */}
                  <div>
                    <label className="block text-gray-300 mb-2">Konum</label>
                    <input
                      value={profileInfo.location}
                      onChange={(e) => setProfileInfo({ ...profileInfo, location: e.target.value })}
                      placeholder="Şehir, Ülke"
                      className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 mb-2">Biyografi</label>
                    <textarea
                      value={profileInfo.biography}
                      onChange={(e) => setProfileInfo({ ...profileInfo, biography: e.target.value })}
                      className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 min-h-[100px]"
                      placeholder="Kendinizden bahsedin..."
                    />
                  </div>



                  <div className="flex justify-end">
                    <button
                      className="bg-[#D63384] text-white py-2 px-4 rounded-lg hover:bg-[#D63384] transition-colors"
                    >Değişiklikleri Kaydet</button>
                  </div>
                </div>
              </div>
            )}

            {/* Privacy Tab */}
            {activeTab === "privacy" && (
              <div>
                <h2 className="text-2xl font-semibold text-white mb-6">Gizlilik</h2>
                <div className="space-y-8">
                  {/* Password Change Section */}
                  <div className="border-b border-[#3C3C3E] pb-6">
                    <h3 className="text-xl font-semibold text-white mb-4">Şifre Değiştir</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-gray-300 mb-2">Mevcut Şifre</label>
                        <input
                          type="password"
                          value={currentPassword}
                          onChange={(e) => setCurrentPassword(e.target.value)}
                          placeholder="Mevcut şifrenizi girin"
                          className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                        />
                      </div>
                      <div>
                        <label className="block text-gray-300 mb-2">Yeni Şifre</label>
                        <input
                          type="password"
                          value={newPassword}
                          onChange={(e) => setNewPassword(e.target.value)}
                          placeholder="Yeni şifrenizi girin"
                          className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                        />
                      </div>
                      <div>
                        <label className="block text-gray-300 mb-2">Yeni Şifre (Tekrar)</label>
                        <input
                          type="password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          placeholder="Yeni şifrenizi tekrar girin"
                          className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                        />
                      </div>
                      <div className="flex justify-start space-x-3">
                        
                        <button
                          className="bg-[#D63384] text-white py-2 px-4 rounded-lg hover:bg-[#D63384] transition-colors"
                          onClick={handlePasswordChange}
                          type="button"
                        >
                          Şifreyi Değiştir
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Account Deletion Section */}
                  <div>
                    <h3 className="text-xl font-semibold text-red-500 mb-4">Hesap Silme</h3>
                    <p className="text-gray-400 mb-4">
                      Hesabınızı silmek geri alınamaz bir işlemdir. Tüm verileriniz kalıcı olarak silinecektir.
                    </p>
                    <button
                      className="bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition-colors"
                      onClick={() => setShowDeleteModal(true)}
                    >
                      Hesabımı Sil
                    </button>
                  </div>
                </div>

                {/* Delete Account Modal */}
                {showDeleteModal && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-[#2C2C2E] p-6 rounded-lg max-w-md w-full mx-4">
                      <h3 className="text-xl font-semibold text-white mb-4">Hesap Silme Onayı</h3>
                      <p className="text-gray-400 mb-4">
                        Hesabınızı silmek için lütfen şifrenizi girin.
                      </p>
                      <div className="space-y-4">
                        <input
                          type="password"

                          ref={passwordInputRef}
                          value={deletePassword}
                          onChange={handlePasswordChange}
                          placeholder="Şifrenizi girin"
                          className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                        />
                        <div className="flex justify-end space-x-3">
                          <button
                            className="w-full bg-[#3C3C3E] text-white rounded-lg px-4 py-2 border border-[#4C4C4E] focus:outline-none focus:border-[#D63384]"
                            onClick={() => {
                              setShowDeleteModal(false);
                              setDeletePassword("");
                            }}
                          >
                            İptal
                          </button>
                          <button
                            className="bg-red-500 text-white py-2 px-4 rounded-lg hover:bg-red-600 transition-colors"
                            onClick={handleDeleteAccount}
                          >
                            Hesabı Sil
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            {/* Notifications Tab */}
            {activeTab === "notifications" && (
              <div>
                <h2 className="text-2xl font-semibold text-white mb-6">Bildirimler</h2>
                <div className="space-y-8">
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-4">E-posta Bildirimleri</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">Yeni bir mesaj aldığımda</span>
                        <button
                          type="button"
                          role="switch"
                          aria-checked={notifications.emailNotifications}
                          onClick={() => setNotifications(prev => ({ ...prev, emailNotifications: !prev.emailNotifications }))}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${notifications.emailNotifications ? "bg-[#D63384]" : "bg-[#3C3C3E]"
                            }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${notifications.emailNotifications ? "translate-x-6" : "translate-x-1"
                              }`}
                          />
                        </button>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">Yeni bir eşleşme olduğunda</span>
                        <button
                          type="button"
                          role="switch"
                          aria-checked={notifications.matchNotifications}
                          onClick={() => setNotifications(prev => ({ ...prev, matchNotifications: !prev.matchNotifications }))}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${notifications.matchNotifications ? "bg-[#D63384]" : "bg-[#3C3C3E]"
                            }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${notifications.matchNotifications ? "translate-x-6" : "translate-x-1"
                              }`}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-white mb-4">Mobil Bildirimleri</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-300">Yeni bir mesaj aldığımda</span>
                        <button
                          type="button"
                          role="switch"
                          aria-checked={notifications.messageNotifications}
                          onClick={() => setNotifications(prev => ({ ...prev, messageNotifications: !prev.messageNotifications }))}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${notifications.messageNotifications ? "bg-[#D63384]" : "bg-[#3C3C3E]"
                            }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${notifications.messageNotifications ? "translate-x-6" : "translate-x-1"
                              }`}
                          />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Blocked Users Tab */}
            {activeTab === "blocked" && (
              <div>
                <h2 className="text-2xl font-semibold text-white mb-6">Engellenen Kullanıcılar</h2>
                <div className="space-y-8">
                  {mockBlockedUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 relative overflow-hidden rounded-full">
                          <Image
                            src={user.avatar}
                            alt={user.name}
                            fill
                            className="object-cover"
                          />
                        </div>
                        <span className="text-white">{user.name}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className="text-gray-300">{user.blockedDate}</span>
                        <button
                          className="bg-[#D63384] text-white py-2 px-4 rounded-lg hover:bg-[#D63384] transition-colors"
                          onClick={() => handleUnblock(user.id)}
                        >
                          Engeli Kaldır
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default SettingsPage;