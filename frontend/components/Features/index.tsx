import SectionTitle from "../Common/SectionTitle";
import SingleFeature from "./SingleFeature";
import featuresData from "./featuresData";

const Features = () => {
  return (
    <>
      <section 
        id="features" 
        className="py-16 md:py-20 lg:py-28 bg-[#1C1C1E]"
      >
        <div className="container">
          <SectionTitle
            title="Öne Çıkan Özellikler"
            paragraph="Modern dünyada aşkı bulmanın en akıllı yolu. İşte size sunduğumuz özellikler."
            center
            className="text-white"
          />

          <div className="grid grid-cols-1 gap-x-8 gap-y-14 md:grid-cols-2 lg:grid-cols-3">
            {featuresData.map((feature) => (
              <SingleFeature key={feature.id} feature={feature} />
            ))}
          </div>
        </div>
      </section>
    </>
  );
};

export default Features;
