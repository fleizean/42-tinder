import { FiLoader } from "react-icons/fi";

const LoadingSpinner = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh]">
    <FiLoader className="w-12 h-12 text-[#D63384] animate-spin" />
    <p className="mt-4 text-gray-400">Yükleniyor...</p>
  </div>
);

export default LoadingSpinner;