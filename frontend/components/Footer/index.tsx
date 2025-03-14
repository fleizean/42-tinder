"use client";
import Image from "next/image";
import Link from "next/link";

const Footer = () => {
  return (
    <>
      <footer
        className="wow fadeInUp relative z-10 bg-[#1C1C1E] pt-16 md:pt-20 lg:pt-24"
        data-wow-delay=".1s"
      >
        <div className="container">
          <div className="-mx-4 flex flex-wrap">
            <div className="w-full px-4 md:w-1/2 lg:w-4/12 xl:w-5/12">
              <div className="mb-12 max-w-[360px] lg:mb-16">
                <Link href="/" className="mb-8 inline-block">
                  <Image
                    src="/images/logo/logo.svg"
                    alt="logo"
                    priority
                    className="w-full"
                    width={120}
                    height={30}
                    style={{ marginLeft: '-30px' }}
                  />
                </Link>
                <p className="mb-9 text-base leading-relaxed text-gray-300">
                  CrushIt, modern dünyada aşkı bulmanın en romantik yolu. Güvenli ve eğlenceli bir ortamda yeni insanlarla tanışın.
                </p>
                   
                <div className="flex items-center">
                  {/* Sosyal medya ikonları */}
                </div>
              </div>
            </div>

            <div className="w-full px-4 sm:w-1/2 md:w-1/2 lg:w-2/12 xl:w-2/12">
              <div className="mb-12 lg:mb-16">
                <h2 className="mb-10 text-xl font-bold text-white">
                  Hızlı Erişim
                </h2>
                <ul>
                  <li>
                    <a
                      href="/about"
                      className="mb-4 inline-block text-base text-gray-300 duration-300 hover:text-[#D63384]"
                    >
                      Hakkımızda
                    </a>
                  </li>
                  <li>
                    <a
                      href="/success-stories"
                      className="mb-4 inline-block text-base text-gray-300 duration-300 hover:text-[#D63384]"
                    >
                      Başarı Hikayeleri
                    </a>
                  </li>
                  <li>
                    <a
                      href="/safety"
                      className="mb-4 inline-block text-base text-gray-300 duration-300 hover:text-[#D63384]"
                    >
                      Güvenlik İpuçları
                    </a>
                  </li>
                </ul>
              </div>
            </div>

            <div className="w-full px-4 sm:w-1/2 md:w-1/2 lg:w-2/12 xl:w-2/12">
              <div className="mb-12 lg:mb-16">
                <h2 className="mb-10 text-xl font-bold text-white">
                  Yasal
                </h2>
                <ul>
                  <li>
                    <a
                      href="/terms"
                      className="mb-4 inline-block text-base text-gray-300 duration-300 hover:text-[#D63384]"
                    >
                      Kullanım Koşulları
                    </a>
                  </li>
                  <li>
                    <a
                      href="/privacy"
                      className="mb-4 inline-block text-base text-gray-300 duration-300 hover:text-[#D63384]"
                    >
                      Gizlilik Politikası
                    </a>
                  </li>
                  <li>
                    <a
                      href="/cookie-policy"
                      className="mb-4 inline-block text-base text-gray-300 duration-300 hover:text-[#D63384]"
                    >
                      Çerez Politikası
                    </a>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="h-px w-full bg-gradient-to-r from-transparent via-[#8A2BE2]/20 to-transparent"></div>
          <div className="py-8">
            <p className="text-center text-base text-gray-300">
              © {new Date().getFullYear()} CrushIt. Tüm hakları saklıdır.
            </p>
          </div>
        </div>
      </footer>
    </>
  );
};

export default Footer;