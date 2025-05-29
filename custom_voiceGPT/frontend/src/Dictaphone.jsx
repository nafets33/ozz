import React, { useState, useEffect, useRef } from "react";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const Dictaphone = ({
  commands = [],
  myFunc,
  listenAfterReply = false,
  no_response_time = 3,
  apiInProgress = false,
  listenButton = false,
  session_listen = false,
}) => {
  const {
    finalTranscript,
    interimTranscript,
    resetTranscript,
    listening,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable,
  } = useSpeechRecognition();

  const [showTranscript, setShowTranscript] = useState(true);
  const [fullTranscript, setFullTranscript] = useState("");
  const lastSpokenTimeRef = useRef(Date.now());
  const silenceTimeoutRef = useRef(null);

  const showTranscript_func = () => setShowTranscript((prev) => !prev);
  const clearTranscript_func = () => {
    resetTranscript();
    setFullTranscript("");
  };

  // Accumulate final transcripts
  useEffect(() => {
    if (finalTranscript) {
      setFullTranscript(prev => `${prev} ${finalTranscript}`.trim());
      resetTranscript();
      lastSpokenTimeRef.current = Date.now(); // Update last spoken time
    }
  }, [finalTranscript]);

  // Detect silence
  useEffect(() => {
    if (interimTranscript) {
      lastSpokenTimeRef.current = Date.now();
      clearTimeout(silenceTimeoutRef.current);
    } else if (fullTranscript) {
      silenceTimeoutRef.current = setTimeout(() => {
        const now = Date.now();
        if (now - lastSpokenTimeRef.current >= no_response_time * 1000) {
          console.log("Processing full transcript after silence:", fullTranscript);

          // Ensure transcript is not reset prematurely
          if (fullTranscript.trim() === "") return;

          // Process based on session mode
          if (session_listen && fullTranscript.split(" ").length > 500000) {
            commands.forEach(cmd => myFunc(fullTranscript, cmd, 6));
            setFullTranscript("");
            return;
          }

          // if (!session_listen && fullTranscript.split(" ").length > 10000) {
          //   setFullTranscript("");
          //   return;
          // }

          // Match keywords
          for (const cmd of commands) {
            const { keywords, api_body } = cmd;
            for (const kw of keywords) {
              const keywordRegex = new RegExp(kw, "i");
              const found = fullTranscript.search(keywordRegex) !== -1;

              if ((found || listenAfterReply || listenButton) && !apiInProgress) {
                if (listenAfterReply) {
                  myFunc(fullTranscript, { api_body: { keyword: "" } }, 3);
                } else if (found) {
                  myFunc(fullTranscript, cmd, 1);
                } else if (listenButton) {
                  myFunc(fullTranscript, cmd, 5);
                }
                setFullTranscript("");
                return;
              }
            }
          }

          console.log("No keyword matched.");
        }
      }, no_response_time * 1000);
    }

    return () => clearTimeout(silenceTimeoutRef.current);
  }, [interimTranscript, fullTranscript, no_response_time, commands, listenAfterReply, listenButton, apiInProgress, myFunc, session_listen]);


  // Start listening on mount if needed
  useEffect(() => {
    if ((session_listen || listenButton || listenAfterReply) && !listening) {
      SpeechRecognition.startListening({ continuous: true, interimResults: true });
    }
  }, [session_listen, listenButton, listenAfterReply, listening]);

  if (!browserSupportsSpeechRecognition) {
    return <span>Your browser does not support speech recognition.</span>;
  }

  if (!isMicrophoneAvailable) {
    return <span>Please enable microphone access.</span>;
  }

  return (
    <>
      {showTranscript && (
        <div style={{ display: "flex", flexDirection: "column", maxHeight: "250px", height: '250px', overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
          <span><strong>You said:</strong></span>
          <span>
            {fullTranscript}{" "}
            <span style={{ color: "gray" }}>{interimTranscript}</span>
          </span>
          <span><strong>Listening:</strong> {listening ? "on" : "off"}</span>
        </div>
      )}
      <button onClick={showTranscript_func} style={{ marginTop: "10px" }}>
        {showTranscript ? "Hide Transcript" : "Show Transcript"}
      </button>
      <button onClick={clearTranscript_func} style={{ marginTop: "10px" }}>
        Clear Transcript
      </button>
    </>
  );
};

export default Dictaphone;