import { useState, useEffect, useRef } from "react";

const DEFAULT_MUSIC_URL = "/audio/04_Out_Again.mp3";

const TRACK_INFO = {
  title: "Out Again",
  artist: "诺基亚",
};

// ─── Waveform ────────────────────────────────────────────────
function Waveform({ analyser, isPlaying }: { analyser: AnalyserNode | null; isPlaying: boolean }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !analyser) return;
    const a = analyser;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const bufLen = a.frequencyBinCount;
    const data = new Uint8Array(bufLen);

    function draw() {
      if (!canvas || !ctx) return;
      a.getByteTimeDomainData(data);
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.beginPath();
      ctx.strokeStyle = "rgba(0, 255, 65, 0.12)";
      ctx.lineWidth = 1;
      ctx.moveTo(0, canvas.height / 2);
      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();

      ctx.beginPath();
      ctx.strokeStyle = "rgba(0, 255, 65, 0.7)";
      ctx.lineWidth = 1.5;
      ctx.shadowColor = "#00ff41";
      ctx.shadowBlur = 3;

      const sw = canvas.width / bufLen;
      let x = 0;
      for (let i = 0; i < bufLen; i++) {
        const v = data[i] / 128.0;
        const y = (v * canvas.height) / 2;
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
        x += sw;
      }
      ctx.stroke();
      ctx.shadowBlur = 0;
      animRef.current = requestAnimationFrame(draw);
    }
    animRef.current = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animRef.current);
  }, [analyser, isPlaying]);

  return <canvas ref={canvasRef} width={160} height={32} className="rounded opacity-70" />;
}

// ─── Main Component ──────────────────────────────────────────
export default function MusicPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [volume, setVolume] = useState(0.3);
  const [error, setError] = useState(false);
  const [showVolume, setShowVolume] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const ctxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const audioCtxReady = useRef(false);

  // ── Init & autoplay ──
  useEffect(() => {
    const audio = new Audio();
    audio.loop = true;
    audio.volume = volume;
    audio.preload = "auto";
    audio.muted = true;
    audioRef.current = audio;

    let isCancelled = false;

    const tryPlay = () => {
      if (isCancelled) return;
      setIsLoaded(true);
      setError(false);

      audio.play().then(() => {
        if (isCancelled) return;
        setIsPlaying(true);
        // Unmute after audio is actually flowing
        setTimeout(() => { if (!isCancelled) audio.muted = false; }, 200);
      }).catch(() => {
        if (isCancelled) return;
        // Muted play blocked (very rare — some strict policies)
        // Wait for a real user gesture
        audio.muted = false;
        const onGesture = () => {
          document.removeEventListener("click", onGesture);
          document.removeEventListener("touchstart", onGesture);
          audio.play().then(() => { if (!isCancelled) setIsPlaying(true); }).catch(() => {});
        };
        document.addEventListener("click", onGesture, { once: true });
        document.addEventListener("touchstart", onGesture, { once: true });
      });
    };

    audio.addEventListener("canplaythrough", tryPlay, { once: true });
    audio.addEventListener("error", () => { if (!isCancelled) setError(true); setIsLoaded(false); }, { once: true });

    audio.src = DEFAULT_MUSIC_URL;
    audio.load();

    return () => {
      isCancelled = true;
      audio.pause();
      audio.src = "";
      audioCtxReady.current = false;
      ctxRef.current?.close();
    };
  }, []);

  // ── Connect AudioContext on first user gesture on the PLAYER button ──
  const connectAudioCtx = async () => {
    if (audioCtxReady.current) return;
    const audio = audioRef.current;
    if (!audio) return;

    try {
      const ctx = new AudioContext();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 128;
      const source = ctx.createMediaElementSource(audio);
      source.connect(analyser);
      analyser.connect(ctx.destination);
      ctxRef.current = ctx;
      analyserRef.current = analyser;
      audioCtxReady.current = true;
    } catch {
      // OK — playback without waveform
    }
  };

  // ── Toggle play/pause ──
  const togglePlay = async () => {
    const audio = audioRef.current;
    if (!audio || !isLoaded) return;

    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
      return;
    }

    await connectAudioCtx();
    if (ctxRef.current?.state === "suspended") {
      await ctxRef.current.resume();
    }
    audio.muted = false;
    try {
      await audio.play();
      setIsPlaying(true);
    } catch { /* ignore */ }
  };

  // ── Volume ──
  useEffect(() => {
    if (audioRef.current) audioRef.current.volume = volume;
  }, [volume]);

  // ── Error ──
  if (error) {
    return (
      <div className="fixed top-16 right-4 z-40">
        <button
          onClick={() => {
            setError(false);
            if (audioRef.current) {
              audioRef.current.src = DEFAULT_MUSIC_URL;
              audioRef.current.load();
            }
          }}
          className="px-3 py-2 rounded-lg border border-cyber-red/30 bg-dark-900/80 backdrop-blur-md text-cyber-red text-xs font-mono hover:bg-dark-800 transition-all"
        >
          ! music_error (retry)
        </button>
      </div>
    );
  }

  // ── Render ──
  return (
    <div
      className="fixed top-16 right-4 z-40"
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => { setIsExpanded(false); setShowVolume(false); }}
    >
      <div
        className={`overflow-hidden transition-all duration-300 ease-out rounded-xl border ${
          isPlaying ? "border-accent/30" : "border-dark-700"
        } bg-dark-900/80 backdrop-blur-md shadow-lg`}
        style={{ width: isExpanded ? 228 : 44 }}
      >
        <div className="flex items-center">
          <button
            onClick={togglePlay}
            disabled={!isLoaded}
            className={`shrink-0 w-11 h-11 flex items-center justify-center transition-all duration-200 ${
              isPlaying ? "text-accent hover:text-accent-dim" : "text-gray-500 hover:text-gray-300"
            } disabled:opacity-30`}
          >
            {!isLoaded ? (
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" strokeDasharray="31.4 31.4" />
              </svg>
            ) : isPlaying ? (
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <rect x="6" y="4" width="4" height="16" rx="1" />
                <rect x="14" y="4" width="4" height="16" rx="1" />
              </svg>
            ) : (
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z" />
              </svg>
            )}
          </button>

          <div className={`flex flex-col justify-center overflow-hidden transition-all duration-300 ${
            isExpanded ? "opacity-100 w-[184px]" : "opacity-0 w-0"
          }`}>
            <div className="px-2 py-1.5">
              <div className="flex items-center justify-between mb-1">
                <div className="min-w-0 flex-1">
                  <p className="text-[11px] font-mono text-gray-300 truncate">
                    {isPlaying ? "♫ " + TRACK_INFO.title : "■ paused"}
                  </p>
                  <p className="text-[9px] font-mono text-gray-600 truncate">{TRACK_INFO.artist}</p>
                </div>
                <button onClick={(e) => { e.stopPropagation(); setShowVolume(!showVolume); }}
                  className="shrink-0 ml-1 p-1 text-gray-500 hover:text-gray-300 transition-colors">
                  <svg className="w-3 h-3" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0014 8.5v7a4.5 4.5 0 002.5-3.5z" />
                  </svg>
                </button>
              </div>

              {isLoaded && <div className="h-[20px]">
                <Waveform analyser={analyserRef.current} isPlaying={isPlaying} />
              </div>}

              {showVolume && <div className="mt-1.5 flex items-center gap-2">
                <span className="text-[9px] text-gray-600 font-mono">VOL</span>
                <div className="flex-1 h-1.5 bg-dark-700 rounded-full cursor-pointer relative"
                  onClick={(e) => {
                    const rect = e.currentTarget.getBoundingClientRect();
                    setVolume(Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width)));
                  }}>
                  <div className="h-full bg-accent/50 rounded-full transition-all duration-100"
                    style={{ width: volume * 100 + "%" }} />
                  <div className="absolute top-1/2 -translate-y-1/2 w-2 h-2 bg-accent rounded-full shadow-[0_0_6px_rgba(0,255,65,0.5)]"
                    style={{ left: "calc(" + (volume * 100) + "% - 4px)" }} />
                </div>
              </div>}
            </div>
          </div>
        </div>

        {isPlaying && !isExpanded && (
          <div className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
        )}
      </div>

      {isLoaded && !isPlaying && (
        <div className="absolute -bottom-8 right-0 animate-pulse text-[10px] font-mono text-accent/60 whitespace-nowrap pointer-events-none">
          ♫ click to play
        </div>
      )}
    </div>
  );
}
