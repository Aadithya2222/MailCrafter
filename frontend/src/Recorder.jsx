import React, { useEffect, useRef, useState } from "react";

/**
 * Simple microphone recorder component for accessibility:
 * - Big toggle button
 * - Keyboard focusable
 * - Announces state via aria-live text
 */
function Recorder({ onTranscribed }) {
  const [recording, setRecording] = useState(false);
  const [supported, setSupported] = useState(true);
  const [message, setMessage] = useState("");
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  useEffect(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setSupported(false);
      setMessage("Microphone access is not supported in this browser.");
    }
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        await sendToBackend(blob);
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setRecording(true);
      setMessage("Recording… press the button again to stop.");
    } catch (err) {
      setMessage("Unable to access microphone. Check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
      setRecording(false);
      setMessage("Uploading audio for transcription…");
    }
  };

  const toggleRecording = () => {
    if (!supported) return;
    if (recording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const sendToBackend = async (blob) => {
    try {
      const formData = new FormData();
      formData.append("audio_file", blob, "recording.webm");

      const res = await fetch("/api/v1/audio/transcribe", {
        method: "POST",
        body: formData
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Transcription failed");
      }
      const data = await res.json();
      onTranscribed && onTranscribed(data);
      setMessage("Transcription complete.");
    } catch (err) {
      setMessage("Failed to transcribe audio.");
    }
  };

  return (
    <div className="recorder">
      <button
        type="button"
        className={recording ? "record-btn recording" : "record-btn"}
        onClick={toggleRecording}
        disabled={!supported}
        aria-pressed={recording}
      >
        {recording ? "Stop Recording" : "Start Recording"}
      </button>
      <p className="hint" aria-live="polite">
        {message}
      </p>
    </div>
  );
}

export default Recorder;

