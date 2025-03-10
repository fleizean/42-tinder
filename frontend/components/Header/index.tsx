"use client";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { useSession, signOut } from "next-auth/react";
import { IoIosSettings } from "react-icons/io";
import ThemeToggler from "./ThemeToggler";
import menuData from "./menuData";
import { FaUserCircle, FaSignOutAlt, FaComment, FaBell, FaHeart, FaKissWinkHeart } from "react-icons/fa";

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
      <div className="pt-[120px] lg:pt-0 bg-white dark:bg-dark">
        <header
          className={`header left-0 top-0 z-40 flex w-full items-center mb-[72px] lg:mb-0 ${sticky
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
                    className={`navbar absolute right-0 top-[72px] z-30 w-[250px] rounded border-[.5px] border-body-color/50 bg-white px-6 py-4 duration-300 dark:border-body-color/20 dark:bg-dark lg:visible lg:static lg:w-auto lg:border-none lg:!bg-transparent lg:p-0 lg:opacity-100 ${navbarOpen ? "visibility opacity-100" : "invisible opacity-0"
                      }`}
                  >
                    <ul className="block lg:flex lg:space-x-12">
                      {/* Existing menu items */}
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
                    {/* Right side area */}
                    <div className="block lg:hidden border-t border-gray-200 dark:border-gray-600 mt-4 pt-4">

                      {status === "authenticated" && session ? (
                        <div className="flex flex-col space-y-2"> {/* Changed to flex-col */}
                          <Link
                            href="/chat"
                            className="flex items-center px-4 py-2 text-base text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
                          >
                            <FaComment className="mr-2" />
                            Chat
                          </Link>

                          <Link
                            href="/dashboard"
                            className="flex items-center px-4 py-2 text-base text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
                          >
                            <FaKissWinkHeart className="mr-2" />
                            Eşleştirme
                          </Link>

                          <Link
                            href="/profile/me"
                            className="flex items-center px-4 py-2 text-base text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
                          >
                            <FaUserCircle className="mr-2" />
                            Profilim
                          </Link>

                          <Link
                            href="/settings"
                            className="flex items-center px-4 py-2 text-base text-gray-700 hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-600"
                          >
                            <IoIosSettings className="mr-2" />
                            Ayarlar
                          </Link>

                          <button
                            onClick={() => signOut({
                              redirect: true,
                              callbackUrl: '/'
                            })}
                            className="flex items-center w-full px-4 py-2 text-base text-red-600 hover:bg-gray-100 dark:text-red-400 dark:hover:bg-gray-600"
                          >
                            <FaSignOutAlt className="mr-2" />
                            Çıkış
                          </button>

                        </div>

                      ) : (
                        /* User is not logged in */


                        <div className="flex flex-col space-y-4">
                          <Link
                            href="/signin"
                            className="group flex items-center px-4 py-2 text-base font-medium text-white/90 rounded-lg border border-pink-500/30 backdrop-blur-sm transition-all duration-300 hover:border-pink-500/60 hover:bg-white/5"
                          >
                            <FaHeart className="mr-2 text-pink-500 transition-all duration-300 group-hover:scale-110 group-hover:text-[#D63384]" />
                            <span className="transition-colors duration-300 group-hover:text-[#D63384]">Giriş</span>
                          </Link>
                          <Link
                            href="/signup"
                            className="flex items-center px-4 py-2 text-base font-medium text-white bg-gradient-to-r from-[#8A2BE2] to-[#D63384] rounded-lg transition-all duration-300 hover:opacity-90 hover:shadow-[0_0_10px_rgba(214,51,132,0.5)]"
                          >
                            <span>Kayıt Ol</span>
                          </Link>
                        </div>
                      )}
                    </div>
                  </nav>
                </div>
                {/* Desktop Menu */}
                <div className="hidden lg:flex lg:items-center lg:space-x-12">
                  {status === "authenticated" && session ? (
                    <>
                      <Link
                        href="/chat"
                        className="flex items-center text-base font-medium text-white/90 hover:text-[#D63384] transition-colors duration-300"
                      >
                        <FaComment className="mr-2 text-pink-500 transition-all duration-300 group-hover:scale-110" />
                        Chat
                      </Link>

                      <Link
                        href="/dashboard"
                        className="flex items-center text-base font-medium text-white/90 hover:text-[#D63384] transition-colors duration-300"
                      >
                        <FaKissWinkHeart className="mr-2 text-pink-500 transition-all duration-300 group-hover:scale-110" />
                        Eşleştirme
                      </Link>

                      <div className="relative group">
                        <button className="flex items-center text-base font-medium text-white/90 hover:text-[#D63384] transition-colors duration-300">
                          <FaUserCircle className="mr-2 text-pink-500 transition-all duration-300 group-hover:scale-110" />
                          <span>Hesabım</span>
                        </button>
                        <div className="absolute right-0 hidden w-48 py-2 mt-0 bg-white/10 backdrop-blur-sm rounded-lg border border-pink-500/20 shadow-xl group-hover:block dark:bg-gray-800/90">
                          <Link
                            href="/profile/me"
                            className="flex items-center px-4 py-2 text-sm text-white/90 hover:text-[#D63384] hover:bg-white/5 transition-all duration-300"
                          >
                            <FaUserCircle className="mr-2 text-pink-500" />
                            Profilim
                          </Link>
                          <Link
                            href="/settings"
                            className="flex items-center px-4 py-2 text-sm text-white/90 hover:text-[#D63384] hover:bg-white/5 transition-all duration-300"
                          >
                            <IoIosSettings className="mr-2 text-pink-500" />
                            Ayarlar
                          </Link>
                          <button
                            onClick={() => signOut({
                              redirect: true,
                              callbackUrl: '/'
                            })}
                            className="flex items-center w-full px-4 py-2 text-sm text-red-400 hover:text-red-500 hover:bg-white/5 transition-all duration-300"
                          >
                            <FaSignOutAlt className="mr-2" />
                            Çıkış
                          </button>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center space-x-6">
                      <Link
                        href="/signin"
                        className="group relative flex items-center px-7 py-3 text-base font-medium text-white overflow-hidden rounded-full border border-pink-500/30 backdrop-blur-sm transition-all duration-300 hover:border-pink-500/60 hover:bg-white/5"
                      >
                        <FaHeart className="mr-2 text-pink-500 transition-all duration-300 group-hover:scale-110 group-hover:text-[#D63384]" />
                        <span className="relative z-10 transition-colors duration-300 group-hover:text-[#D63384]">Giriş</span>
                      </Link>
                      <Link
                        href="/signup"
                        className="flex items-center px-8 py-3 text-base font-medium text-white bg-gradient-to-r from-[#8A2BE2] to-[#D63384] rounded-full transition-all duration-300 hover:shadow-[0_0_15px_rgba(138,43,226,0.5)] hover:scale-105"
                      >
                        Kayıt Ol
                      </Link>
                    </div>
                  )}
                </div>

              </div>
            </div>
          </div>
        </header>
      </div>
    </>
  );
};

export default Header;