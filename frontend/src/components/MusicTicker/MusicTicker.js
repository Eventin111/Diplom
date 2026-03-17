import React, { useEffect, useRef, useState } from 'react';

const MusicTicker = ({
  title = 'Original audio',
  source = 'Swipelt',
  audioUrl = '',
  isActive = false
}) => {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(true);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) {
      return;
    }

    audio.loop = true;
    audio.muted = isMuted;

    if (!isActive || !isPlaying) {
      audio.pause();
      return;
    }

    const tryPlay = async () => {
      try {
        await audio.play();
      } catch (error) {
        // autoplay may be blocked by browser policy
      }
    };

    void tryPlay();
  }, [isActive, isMuted, isPlaying]);

  const togglePlay = () => {
    setIsPlaying((prev) => !prev);
  };

  const toggleMute = () => {
    setIsMuted((prev) => !prev);
  };

  return (
    <div className="music-info-tiktok" role="group" aria-label={`Трек ${title}`}>
      <button
        type="button"
        className={`music-disc ${isPlaying && isActive ? 'is-playing' : ''}`}
        onClick={togglePlay}
        title={isPlaying ? 'Пауза' : 'Воспроизвести'}
      >
        <span className="disc-icon">{isPlaying && isActive ? '♪' : '▶'}</span>
        <span className="disc-spinner" />
      </button>

      <div className="music-details">
        <div className="music-title">{title}</div>
        <div className="music-source">{source}</div>
      </div>

      <button
        type="button"
        className="music-audio-btn"
        onClick={toggleMute}
        title={isMuted ? 'Включить звук' : 'Выключить звук'}
      >
        {isMuted ? '🔇' : '🔊'}
      </button>

      {audioUrl ? <audio ref={audioRef} src={audioUrl} preload="none" /> : null}
    </div>
  );
};

export default MusicTicker;
