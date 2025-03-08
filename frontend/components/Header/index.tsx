"use client";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useSession, signOut } from "next-auth/react";
import { IoIosSettings } from "react-icons/io";
import ThemeToggler from "./ThemeToggler";
import menuData from "./menuData";
import { FaUserCircle, FaSignOutAlt, FaComment, FaBell, FaKissWinkHeart } from "react-icons/fa";

const Header = () => {
  const [navbarOpen, setNavbarOpen] = useState(false);
  const [sticky, setSticky] = useState(false);
  const [openIndex, setOpenIndex] = useState(-1);
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      type: "like",
      message: "Ayşe profilini beğendi",
      time: "5 dakika önce",
      read: false
    },
    {
      id: 2,
      type: "match",
      message: "Mehmet ile eşleştin!",
      time: "1 saat önce",
      read: true
    }
  ]);
  const [showNotifications, setShowNotifications] = useState(false);

  // 2. useSession hook
  const { data: session, status } = useSession();

  // 3. usePathname hook
  const pathname = usePathname();
  const usePathName = pathname === "/" ? "/home" : pathname;

  // 5. useEffect hook
  useEffect(() => {
    window.addEventListener("scroll", handleStickyNavbar);
    return () => {
      window.removeEventListener("scroll", handleStickyNavbar);
    };
  }, []);


  // 4. Event handlers
  const navbarToggleHandler = () => {
    setNavbarOpen(!navbarOpen);
  };

  const handleStickyNavbar = () => {
    setSticky(window.scrollY >= 80);
  };

  const handleSubmenu = (index: number) => {
    setOpenIndex(openIndex === index ? -1 : index);
  };



  // Loading state
  if (status === "loading") {
    return null;
  }

  return (
    <>
      <header
        className={`header left-0 top-0 z-40 flex w-full items-center ${sticky
          ? "dark:bg-gray-dark dark:shadow-sticky-dark fixed z-[9999] bg-white !bg-opacity-80 shadow-sticky backdrop-blur-sm transition"
          : "absolute bg-transparent"
          }`}
      >
        <div className="container">
          <div className="relative -mx-4 flex items-center justify-between">
            <div className="w-60 max-w-full px-4 xl:mr-12">
              <Link
                href={session ? "/dashboard" : "/"}
                className={`header-logo block w-full ${sticky ? "py-5 lg:py-2" : "py-8"
                  } `}
              >
                <Image
                  src="/images/logo/logo.svg"
                  alt="logo"
                  width={230}
                  height={50}
                  className="w-full dark:hidden"
                />
                <Image
                  src="/images/logo/logo.svg"
                  alt="logo"
                  width={230}
                  height={50}
                  className="hidden w-full dark:block"
                />
              </Link>
            </div>
            <div className="flex w-full items-center justify-between px-4">
              <div>
                <button
                  onClick={navbarToggleHandler}
                  id="navbarToggler"
                  aria-label="Mobile Menu"
                  className="absolute right-4 top-1/2 block translate-y-[-50%] rounded-lg px-3 py-[6px] ring-primary focus:ring-2 lg:hidden"
                >
                  <span
                    className={`relative my-1.5 block h-0.5 w-[30px] bg-black transition-all duration-300 dark:bg-white ${navbarOpen ? " top-[7px] rotate-45" : ""
                      }`}
                  />
                  <span
                    className={`relative my-1.5 block h-0.5 w-[30px] bg-black transition-all duration-300 dark:bg-white ${navbarOpen ? "opacity-0" : ""
                      }`}
                  />
                  <span
                    className={`relative my-1.5 block h-0.5 w-[30px] bg-black transition-all duration-300 dark:bg-white ${navbarOpen ? " top-[-8px] -rotate-45" : ""
                      }`}
                  />
                </button>
                <nav
                  id="navbarCollapse"
                  className={`navbar absolute right-0 z-30 w-[250px] rounded border-[.5px] border-body-color/50 bg-white px-6 py-4 duration-300 dark:border-body-color/20 dark:bg-dark lg:visible lg:static lg:w-auto lg:border-none lg:!bg-transparent lg:p-0 lg:opacity-100 ${navbarOpen
                    ? "visibility top-full opacity-100"
                    : "invisible top-[120%] opacity-0"
                    }`}
                >
                  <ul className="block lg:flex lg:space-x-12">
                    {menuData.map((menuItem, index) => (
                      <li key={index} className="group relative">
                        {menuItem.path ? (
                          <Link
                            href={menuItem.path}
                            className={`flex py-2 text-base lg:mr-0 lg:inline-flex lg:px-0 lg:py-6 ${usePathName === menuItem.path
                              ? "text-primary dark:text-white"
                              : "text-dark hover:text-primary dark:text-white/70 dark:hover:text-white"
                              }`}
                          >
                            {menuItem.title}
                          </Link>
                        ) : (
                          <>
                            <p
                              onClick={() => handleSubmenu(index)}
                              className="flex cursor-pointer items-center justify-between py-2 text-base text-dark group-hover:text-primary dark:text-white/70 dark:group-hover:text-white lg:mr-0 lg:inline-flex lg:px-0 lg:py-6"
                            >
                              {menuItem.title}
                              <span className="pl-3">
                                <svg width="25" height="24" viewBox="0 0 25 24">
                                  <path
                                    fillRule="evenodd"
                                    clipRule="evenodd"
                                    d="M6.29289 8.8427C6.68342 8.45217 7.31658 8.45217 7.70711 8.8427L12 13.1356L16.2929 8.8427C16.6834 8.45217 17.3166 8.45217 17.7071 8.8427C18.0976 9.23322 18.0976 9.86639 17.7071 10.2569L12 15.964L6.29289 10.2569C5.90237 9.86639 5.90237 9.23322 6.29289 8.8427Z"
                                    fill="currentColor"
                                  />
                                </svg>
                              </span>
                            </p>
                            <div
                              className={`submenu relative left-0 top-full rounded-sm bg-white transition-[top] duration-300 group-hover:opacity-100 dark:bg-dark lg:invisible lg:absolute lg:top-[110%] lg:block lg:w-[250px] lg:p-4 lg:opacity-0 lg:shadow-lg lg:group-hover:visible lg:group-hover:top-full ${openIndex === index ? "block" : "hidden"
                                }`}
                            >
                              {menuItem.submenu?.map((submenuItem, i) => (
                                <Link
                                  href={submenuItem.path}
                                  key={i}
                                  className="block rounded py-2.5 text-sm text-dark hover:text-primary dark:text-white/70 dark:hover:text-white lg:px-3"
                                >
                                  {submenuItem.title}
                                </Link>
                              ))}
                            </div>
                          </>
                        )}
                      </li>
                    ))}
                  </ul>
                </nav>
              </div>

              {/* Right side area */}
              <div className="flex items-center justify-end pr-16 lg:pr-0">

                {status === "authenticated" && session ? (
                  <div className="flex items-center space-x-4">
                    <Link
                      href="/chat"
                      className="flex items-center px-4 py-2 text-base font-medium hover:opacity-70 dark:text-white"
                    >
                      <span className="inline-flex items-center">
                        <FaComment className="mr-2" />
                        Chat
                      </span>
                    </Link>

                    <Link
                      href="/dashboard"
                      className="flex items-center px-4 py-2 text-base font-medium hover:opacity-70 dark:text-white"
                    >
                      <span className="inline-flex items-center">
                        <FaKissWinkHeart className="mr-2" />
                        Eşleştirme
                      </span>
                    </Link>

                    <div className="relative group">
                      <button className="flex items-center px-4 py-2 text-base font-medium hover:opacity-70 dark:text-white">
                        <span className="inline-flex items-center">
                          <FaUserCircle className="mr-2" />
                          <span>Hesabım</span>
                        </span>
                      </button>

                      <div className="absolute right-0 hidden w-48 py-2 mt-0 bg-white rounded-lg shadow-xl group-hover:block dark:bg-gray-700">
                        <Link
                          href="/profile/me"
                          className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
                        >
                          <FaUserCircle className="mr-2 w-4 h-4" />
                          Profilim
                        </Link>

                        <hr className="my-2 border-gray-200 dark:border-gray-600" />

                        <Link
                          href="/settings"
                          className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
                        >
                          <IoIosSettings className="mr-2 w-4 h-4" />
                          Ayarlar
                        </Link>

                        <hr className="my-2 border-gray-200 dark:border-gray-600" />

                        <button
                          onClick={() => signOut({
                            redirect: true,
                            callbackUrl: '/'
                          })}
                          className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-gray-100 dark:text-red-400 dark:hover:bg-gray-600"
                        >
                          <FaSignOutAlt className="mr-2 w-4 h-4" />
                          Çıkış
                        </button>
                      </div>
                    </div>

                    <div className="relative group mx-2">
                      <button
                        className="flex items-center px-4 py-2 text-base font-medium hover:opacity-70 dark:text-white"
                        onClick={() => setShowNotifications(!showNotifications)}
                      >
                        <div className="relative">
                          <FaBell className="w-5 h-5" />
                          {notifications.some(n => !n.read) && (
                            <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></div>
                          )}
                        </div>
                      </button>

                      {showNotifications && (
                        <div className="absolute right-0 w-80 mt-2 py-2 bg-white rounded-lg shadow-xl dark:bg-gray-700">
                          <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-600">
                            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200">
                              Bildirimler
                            </h3>
                          </div>

                          <div className="max-h-80 overflow-y-auto">
                            {notifications.length > 0 ? (
                              notifications.map((notification) => (
                                <div
                                  key={notification.id}
                                  className={`px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-600 ${!notification.read ? 'bg-blue-50 dark:bg-gray-600/50' : ''
                                    }`}
                                >
                                  <p className="text-sm text-gray-700 dark:text-gray-200">
                                    {notification.message}
                                  </p>
                                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                    {notification.time}
                                  </p>
                                </div>
                              ))
                            ) : (
                              <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                                Bildirim bulunmuyor
                              </div>
                            )}
                          </div>

                          {notifications.length > 0 && (
                            <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-600">
                              <button
                                className="text-sm text-center w-full text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                                onClick={() => {
                                  setNotifications(notifications.map(n => ({ ...n, read: true })));
                                }}
                              >
                                Tümünü okundu işaretle
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  /* User is not logged in */
                  <>
                    <Link
                      href="/signin"
                      className="hidden px-7 py-3 text-base font-medium text-white hover:text-[#D63384] transition-colors duration-300 md:block"
                    >
                      Giriş
                    </Link>
                    <Link
                      href="/signup"
                      className="hidden md:block px-8 py-3 text-base font-medium text-white bg-gradient-to-r from-[#8A2BE2] to-[#D63384] rounded-full transition-all duration-300 hover:shadow-[0_0_15px_rgba(138,43,226,0.5)] hover:scale-105 md:px-9 lg:px-6 xl:px-9"
                    >
                      Kayıt Ol
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>
    </>
  );
};

export default Header;