import { Feature } from "@/types/feature";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHeart, 
  faShieldHeart, 
  faLocationDot, 
  faComments, 
  faUserCheck, 
  faMobileScreen 
} from '@fortawesome/free-solid-svg-icons';

const featuresData: Feature[] = [
  {
    id: 1,
    icon: (
      <FontAwesomeIcon icon={faHeart} className="w-10 h-10 text-[#D63384]" />
    ),
    title: "Akıllı Eşleştirme",
    paragraph:
      "Kişilik analizine dayalı eşleştirme sistemimiz ile size en uygun adayları buluyoruz.",
  },
  {
    id: 2,
    icon: (
      <FontAwesomeIcon icon={faShieldHeart} className="w-10 h-10 text-[#8A2BE2]" />
    ),
    title: "Güvenli Buluşma",
    paragraph:
      "Kullanıcı doğrulama sistemi ve güvenli mesajlaşma ile güvenli bir ortam sağlıyoruz.",
  },
  {
    id: 3,
    icon: (
      <FontAwesomeIcon icon={faLocationDot} className="w-10 h-10 text-[#D63384]" />
    ),
    title: "Yakınınızdaki Kişiler",
    paragraph:
      "Konum bazlı eşleştirme ile yakınınızdaki potansiyel eşlerinizi keşfedin.",
  },
  {
    id: 4,
    icon: (
      <FontAwesomeIcon icon={faComments} className="w-10 h-10 text-[#8A2BE2]" />
    ),
    title: "Gerçek Zamanlı Sohbet",
    paragraph:
      "Anlık mesajlaşma ve görüntülü görüşme özellikleriyle iletişimi kolaylaştırıyoruz.",
  },
  {
    id: 5,
    icon: (
      <FontAwesomeIcon icon={faUserCheck} className="w-10 h-10 text-[#D63384]" />
    ),
    title: "Detaylı Profiller",
    paragraph:
      "İlgi alanları, hobiler ve yaşam tarzı bilgilerini içeren kapsamlı profil oluşturma.",
  },
  {
    id: 6,
    icon: (
      <FontAwesomeIcon icon={faMobileScreen} className="w-10 h-10 text-[#8A2BE2]" />
    ),
    title: "Her Yerde Erişim",
    paragraph:
      "Mobil uyumlu tasarım ile dilediğiniz yerden potansiyel eşlerinize ulaşın.",
  }
];
export default featuresData;