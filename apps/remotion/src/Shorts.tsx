import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

type Props = {
  hook: string;
  scenes: string[];
  cta: string;
  brand: string;
  accent: string;
  primary: string;
  captions: { word: string; start: number; end: number }[];
};

const Card = ({ title, body, accent, primary }: { title: string; body: string; accent: string; primary: string }) => {
  const frame = useCurrentFrame();
  const zoom = interpolate(frame, [0, 80], [1, 1.08], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: primary, justifyContent: "center", padding: 80, transform: `scale(${zoom})` }}>
      <div style={{ color: accent, letterSpacing: 4, fontSize: 28, marginBottom: 24 }}>{title}</div>
      <div style={{ color: "#F4F1E8", fontSize: 64, lineHeight: 1.15, fontWeight: 700 }}>{body}</div>
    </AbsoluteFill>
  );
};

export const Shorts = ({ hook, scenes, cta, brand, accent, primary, captions }: Props) => {
  const { fps, durationInFrames } = useVideoConfig();
  const frame = useCurrentFrame();
  const blocks = [hook, ...scenes.slice(0, 3), cta];
  const slice = Math.floor(durationInFrames / blocks.length);
  const t = frame / fps;
  const active = captions.filter((item) => t >= item.start && t <= item.end).map((item) => item.word).slice(0, 4);

  return (
    <AbsoluteFill style={{ background: primary }}>
      {blocks.map((text, index) => (
        <Sequence key={index} from={index * slice} durationInFrames={slice}>
          <Card
            title={index === 0 ? `${brand} · HOOK` : index === blocks.length - 1 ? "CTA" : `SAHNE ${index}`}
            body={text}
            accent={accent}
            primary={primary}
          />
        </Sequence>
      ))}
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 420 }}>
        <div style={{ color: "#fff", fontSize: 54, fontWeight: 700, textAlign: "center", maxWidth: 900 }}>
          {active.join(" ")}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
