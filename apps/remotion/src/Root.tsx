import { Composition } from "remotion";
import { Shorts } from "./Shorts";

export const RemotionRoot = () => {
  return (
    <Composition
      id="Shorts"
      component={Shorts}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        hook: "HOOK",
        scenes: ["Sahne 1", "Sahne 2", "Sahne 3"],
        cta: "Takip et",
        brand: "Bilim Dakikası",
        accent: "#F4B942",
        primary: "#0A0E17",
        captions: [],
      }}
    />
  );
};
