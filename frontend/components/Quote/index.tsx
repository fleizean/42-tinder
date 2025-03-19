"use client";

const Quote = () => {
  return (
    <div className="relative h-screen bg-[#1C1C1E]">
      {/* Gradient Effects */}
      <div className="absolute right-0 top-0 z-[1] opacity-30 lg:opacity-100">
        <div className="h-[500px] w-[500px] rounded-full bg-gradient-to-r from-[#8A2BE2] to-[#00CED1] opacity-20 blur-[120px]"></div>
      </div>
      <div className="absolute bottom-0 left-0 z-[1] opacity-30 lg:opacity-100">
        <div className="h-[500px] w-[500px] rounded-full bg-gradient-to-r from-[#D63384] to-[#FFD700] opacity-20 blur-[120px]"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 h-full flex items-center justify-center">
        <div className="text-center px-4">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Aşk Bir Tık Uzağında
          </h1>
          <p className="text-xl md:text-2xl text-gray-200 max-w-2xl mx-auto italic">
            Gerçek aşk, iki ruhun birbiriyle dans ettiği ve iki kalbin aynı ritimde attığı andır.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Quote;