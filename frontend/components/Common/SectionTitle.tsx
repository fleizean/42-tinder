const SectionTitle = ({
  title,
  paragraph,
  width = "570px",
  center,
  mb = "100px",
  className,
}: {
  title: string;
  paragraph: string;
  width?: string;
  center?: boolean;
  mb?: string;
  className?: string;
}) => {
  return (
    <>
      <div
        className={`wow fadeInUp w-full ${center ? "mx-auto text-center" : ""}`}
        data-wow-delay=".1s"
        style={{ maxWidth: width, marginBottom: mb }}
      >
        <h2 className={`mb-4 text-3xl font-bold !leading-tight sm:text-4xl md:text-[45px] ${className}`}>
          {title}
        </h2>
        <p className={`text-base !leading-relaxed md:text-lg ${className}`}>
          {paragraph}
        </p>
      </div>
    </>
  );
};

export default SectionTitle;
