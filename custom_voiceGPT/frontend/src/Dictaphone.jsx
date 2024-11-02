import React, { useState, useEffect } from "react";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const Dictaphone = ({
  commands,
  myFunc,
  listenAfterReply = false,
  no_response_time = 3,
  apiInProgress = false, // Receive apiInProgress as a prop
  listenButton = false,
  session_listen = false,
}) => {
  const [transcribing, setTranscribing] = useState(true);
  const [clearTranscriptOnListen, setClearTranscriptOnListen] = useState(true);
  const { finalTranscript, resetTranscript, listening, browserSupportsSpeechRecognition, isMicrophoneAvailable } = useSpeechRecognition({ transcribing, clearTranscriptOnListen });
  const [show_transcript, setshow_transcript] = useState(true); // Added state for API in progress

  const showTranscript_func = () => {
    console.log("set showTranscript", show_transcript)
    if (show_transcript) {
      setshow_transcript(false)
    } else {
      setshow_transcript(true)
    }
  };

  const clearTranscript_func = () => {
    console.log("clear transcript")
    resetTranscript()
  }

  useEffect(() => {
    if (finalTranscript !== "") {
      console.log("Got final result:", finalTranscript);
      console.log("listening?", listening);
      console.log("listenAfterReply:", listenAfterReply);


      // Clear the previous script if a keyword is found or if the transcript exceeds limits
      if (session_listen && finalTranscript.split(" ").length > 500000) {
        console.log("Transcript exceeds X words");
        // Ensure to check if i is defined
        for (let i = 0; i < commands.length; i++) {
          myFunc(finalTranscript, commands[i], 6);
        }
        resetTranscript();
        return;
      }

      if (!session_listen && finalTranscript.split(" ").length > 10000) {
        console.log("Transcript exceeds 10000 words. Clearing.");
        resetTranscript();
        return;
      }

      // Clear any existing timers to prevent multiple triggers
      const timer = setTimeout(() => {
        const lowerCaseTranscript = finalTranscript.toLowerCase();

        for (let i = 0; i < commands.length; i++) {
          const { keywords, api_body } = commands[i];
          for (let j = 0; j < keywords.length; j++) {
            const keyword = new RegExp(keywords[j], "i");
            const isKeywordFound = lowerCaseTranscript.search(keyword) !== -1;

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
      }, no_response_time * 1000);

      return () => clearTimeout(timer); // Clear the timer on component unmount or when useEffect runs again
    }
  }, [finalTranscript, listening, listenAfterReply, commands, no_response_time, resetTranscript, apiInProgress, listenButton]);

  if (!browserSupportsSpeechRecognition) {
    return <span>No browser support</span>;
  }

  if (!isMicrophoneAvailable) {
    return <span>Please allow access to the microphone</span>;
  }

  return (
    <>
      <div style={{ height: "20px" }} /> {/* Adds empty space */}
      {show_transcript && (
        <div style={{ display: "flex", flexDirection: "column", maxHeight: "200px", overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
          <span>You said: {finalTranscript}</span>
          <span>Listening: {listening ? "on" : "off"}</span>
          {/* Add other conversation messages here */}
        </div>
      )}
      {/* Button to clear the transcript */}
      <button onClick={showTranscript_func} style={{ marginTop: "10px" }}>
      {show_transcript ? "Hide Transcript" : "Show Transcript"}
      </button>
      <button onClick={clearTranscript_func} style={{ marginTop: "10px" }}>
      Clear Transscript
      </button>
    </>
  );
}

export default Dictaphone;