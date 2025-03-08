"use client";

import Link from "next/link";

const NotFound = () => {
  return (
    <>
      <section className="relative z-10 pb-16 pt-36 md:pb-20 lg:pb-28 lg:pt-[180px] bg-[#1C1C1E]">
        <div className="container">
          <div className="flex flex-wrap -mx-4">
            <div className="w-full px-4">
              <div className="mx-auto max-w-[530px] text-center">
                <div className="mx-auto text-center mb-9">
                  <svg className="w-full" height="210" viewBox="0 0 474 210">
                    <path
                      className="fill-[#D63384]"
                      d="M404 126C404 155.823 379.823 180 350 180C320.177 180 296 155.823 296 126C296 96.1766 320.177 72 350 72C379.823 72 404 96.1766 404 126Z"
                    />
                    <path
                      className="fill-[#8A2BE2]"
                      d="M178 126C178 155.823 153.823 180 124 180C94.1766 180 70 155.823 70 126C70 96.1766 94.1766 72 124 72C153.823 72 178 96.1766 178 126Z"
                    />
                  </svg>
                </div>
                <h3 className="mb-4 text-3xl font-bold text-white sm:text-4xl">
                  404 - Sayfa Bulunamadı
                </h3>
                <p className="mb-10 text-base font-medium leading-relaxed text-gray-300 sm:text-lg sm:leading-relaxed">
                  Aradığınız sayfa taşınmış, silinmiş veya hiç var olmamış olabilir.
                </p>
                <Link
                  href="/"
                  className="inline-flex items-center justify-center rounded-lg bg-gradient-to-r from-[#8A2BE2] to-[#D63384] px-8 py-3 text-base font-medium text-white transition-all duration-300 hover:shadow-[0_0_20px_rgba(138,43,226,0.3)] hover:scale-[1.02] md:px-9 lg:px-8 xl:px-9"
                >
                  Ana Sayfaya Dön
                </Link>
              </div>
            </div>
          </div>
        </div>
        <div className="absolute bottom-0 left-0 right-0 z-[-1] h-full w-full bg-gradient-to-b from-[#1C1C1E] via-[#8A2BE2]/10 to-[#D63384]/10"></div>
      </section>
    </>
  );
};

export default NotFound;