"use client";

import { useEffect, useRef, useState } from "react";

export default function DigitalTwinCard({ contributorId }: { contributorId: number }) {
  const [state, setState] = useState<"idle"|"recording"|"thinking"|"speaking">("idle");
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = "";
      }
    };
  }, []);

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      chunksRef.current = [];

      mr.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      mr.onstart = () => setState("recording");

      mr.onstop = async () => {
        setState("thinking");
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });

        // Prepare form data
        const fd = new FormData();
        // Some servers expect file extension; use webm
        fd.append("audio_file", blob, "recording.webm");

        try {
          const res = await fetch(`http://127.0.0.1:8000/contributors/${contributorId}/voice-chat-audio`, {
            method: "POST",
            body: fd,
          });

          if (!res.ok) {
            const text = await res.text();
            throw new Error(text || `Server returned ${res.status}`);
          }

          const arrayBuffer = await res.arrayBuffer();
          const audioBlob = new Blob([arrayBuffer], { type: "audio/mpeg" });
          const url = URL.createObjectURL(audioBlob);

          const audio = new Audio(url);
          audioRef.current = audio;

          audio.onplaying = () => setState("speaking");
          audio.onended = () => {
            setState("idle");
            // revoke url after short delay
            setTimeout(() => URL.revokeObjectURL(url), 2000);
          };

          audio.play().catch((e) => {
            console.error("Playback failed", e);
            setState("idle");
          });

        } catch (e) {
          console.error(e);
          alert(e instanceof Error ? e.message : String(e));
          setState("idle");
        }
      };

      mr.start();
      setMediaRecorder(mr);
    } catch (e) {
      alert("Microphone access denied or unavailable.");
    }
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      // stop tracks
      const tracks = (mediaRecorder as any).stream?.getTracks?.();
      if (tracks) tracks.forEach((t: MediaStreamTrack) => t.stop());
      setMediaRecorder(null);
    }
  }

  function toggleRecording() {
    if (state === "idle") {
      startRecording();
    } else if (state === "recording") {
      stopRecording();
    }
  }

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6">
      <h3 className="text-lg font-semibold mb-3">Talk to Contributor Digital Twin</h3>

      <div className="flex items-center gap-4">
        <button
          onClick={toggleRecording}
          className={`px-4 py-3 rounded-full text-white font-medium transition ${state === "recording" ? "bg-red-600" : "bg-indigo-600"}`}
        >
          {state === "recording" ? "Recording…" : "🎤 Start Conversation"}
        </button>

        <div>
          <div className="text-sm text-slate-600">State:</div>
          <div className="font-medium">{state.toUpperCase()}</div>
        </div>

        <div className="ml-auto">
          {state === "recording" && (
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
              <span className="text-sm text-slate-500">Recording</span>
            </div>
          )}

          {state === "thinking" && (
            <div className="flex items-center gap-2">
              <svg className="animate-spin h-5 w-5 text-slate-500" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" strokeOpacity="0.2"/><path d="M22 12a10 10 0 00-10-10" stroke="currentColor" strokeWidth="4"/></svg>
              <span className="text-sm text-slate-500">Thinking...</span>
            </div>
          )}

          {state === "speaking" && (
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-green-500" viewBox="0 0 24 24" fill="currentColor"><path d="M12 3v18c-4 0-7-3-7-7s3-7 7-7z"/></svg>
              <span className="text-sm text-slate-500">Playing response</span>
            </div>
          )}
        </div>
      </div>

      <div className="mt-4 text-sm text-slate-500">Your voice is sent securely to the server for transcription and answer generation.</div>
    </div>
  );
}
