"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";

const LeafletMap = dynamic(() => import("./LeafletMap"), {
  ssr: false,
  loading: () => (
    <div className="h-[400px] bg-[#3C3C3E] flex items-center justify-center">
      <span className="text-white">Harita yükleniyor...</span>
    </div>
  ),
});

interface SimpleMapProps {
  onLocationSelect: (lat: number, lng: number) => void;
  initialLocation?: [number, number];
  height?: string;
}

export function SimpleMap({ 
  onLocationSelect, 
  initialLocation = [39.92077, 32.85411],
  height = "400px"
}: SimpleMapProps) {
  const [isClient, setIsClient] = useState(false);
  
  // Her komponent render edildiğinde yeni bir harita ID'si oluşturalım
  // Bu sayede haritanın tamamen yeniden başlatılmasını sağlayacağız
  const [mapInstanceId] = useState(() => `map-instance-${Date.now()}`);
  
  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return (
      <div 
        style={{ height }}
        className="bg-[#3C3C3E] flex items-center justify-center"
      >
        <span className="text-white">Harita yükleniyor...</span>
      </div>
    );
  }

  return (
    <div style={{ height }} className="relative" key={mapInstanceId}>
      <LeafletMap
        initialLocation={initialLocation}
        onLocationSelect={onLocationSelect}
        height={height}
      />
    </div>
  );
}

export default SimpleMap;