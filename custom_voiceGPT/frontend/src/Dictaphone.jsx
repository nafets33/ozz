import React, { useState, useEffect } from "react";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const Dictaphone = ({
  commands,
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
  
  const [show_transcript, setShowTranscript] = useState(true);

  const showTranscript_func = () => setShowTranscript((prev) => !prev);
  const clearTranscript_func = () => resetTranscript();

  const processTranscript = () => {
    if (finalTranscript !== "") {
      console.log("Got final result:", finalTranscript);
      console.log("Listening?", listening);
      console.log("listenAfterReply:", listenAfterReply);

      if (session_listen && finalTranscript.split(" ").length > 500000) {
        console.log("Transcript exceeds X words");
        for (let i = 0; i < commands.length; i++) {
          myFunc(finalTranscript, commands[i], 6);
        }
        resetTranscript();
        return;
      }

      for (let i = 0; i < commands.length; i++) {
        const { keywords, api_body } = commands[i];
        for (let j = 0; j < keywords.length; j++) {
          const keyword = new RegExp(keywords[j], "i");
          const isKeywordFound = finalTranscript.search(keyword) !== -1;

          if ((isKeywordFound || listenAfterReply || listenButton) && !apiInProgress) {
            if (listenAfterReply) {
              myFunc(finalTranscript, { api_body: { keyword: "" } }, 3);
            } else if (isKeywordFound) {
              myFunc(finalTranscript, commands[i], 1);
            } else if (listenButton) {
              myFunc(finalTranscript, commands[i], 5);
            }
            resetTranscript();
            return;
          }
        }
      }
      console.log("Waiting for a keyword");
    }
  };

  useEffect(() => {
    processTranscript();
  }, [finalTranscript]);

  if (!browserSupportsSpeechRecognition) {
    return <span>No browser support</span>;
  }

  if (!isMicrophoneAvailable) {
    return <span>Please allow access to the microphone</span>;
  }

  return (
    <>
      {show_transcript && (
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            maxHeight: "250px",
            height: "250px",
            overflowY: "auto",
            border: "1px solid #ccc",
            padding: "10px",
          }}
        >
          <span>
            <strong>Listening:</strong> {listening ? "on" : "off"}
          </span>
          <span>
            <strong>Transcript:</strong>{" "}
            <span>
              {finalTranscript}
              <span style={{ color: "gray" }}>{interimTranscript}</span>
            </span>
          </span>
        </div>
      )}
      <button onClick={showTranscript_func} style={{ marginTop: "10px" }}>
        {show_transcript ? "Hide Transcript" : "Show Transcript"}
      </button>
      <button onClick={clearTranscript_func} style={{ marginTop: "10px" }}>
        Clear Transcript
      </button>
    </>
  );
}

export default Dictaphone;