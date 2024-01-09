import React, { useState, useEffect } from "react";
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';

const Dictaphone_ss = ({
  commands,
  myFunc,
  listenAfterReply = false,
  noResponseTime = 3,
  show_conversation = true,
  apiInProgress = false, // Receive apiInProgress as a prop
}) => {
  const [transcribing, setTranscribing] = useState(true);
  const [clearTranscriptOnListen, setClearTranscriptOnListen] = useState(true);
  const { finalTranscript, resetTranscript, listening, browserSupportsSpeechRecognition, isMicrophoneAvailable } = useSpeechRecognition({ transcribing, clearTranscriptOnListen });
  const [prevScript, setPrevScript] = useState("");

  useEffect(() => {
    if (finalTranscript !== "") {

      // Set the previous script
      setPrevScript(finalTranscript);

      // Start the timer to check for keywords after a pause
      const timer = setTimeout(() => {
        for (let i = 0; i < commands.length; i++) {
          const { keywords, api_body } = commands[i];
          for (let j = 0; j < keywords.length; j++) {
            const keyword = new RegExp(keywords[j], "i");
            const isKeywordFound = finalTranscript.search(keyword) !== -1;
            console.log("listenAfterReply:", listenAfterReply);
            if (!apiInProgress) {{
                myFunc(finalTranscript, commands[i], 4);
              }
              resetTranscript();
              return;
            }
          }
        }
        // Waiting for a keyword or API is in progress
        console.log("Waiting for a keyword or API is in progress");
      }, noResponseTime * 1000);

      return () => clearTimeout(timer); // Clear the timer on component unmount or when useEffect runs again
    }
  }, [finalTranscript, listenAfterReply, commands, noResponseTime, resetTranscript, apiInProgress]);


  if (!browserSupportsSpeechRecognition) {
    return <span>No browser support</span>;
  }

  if (!isMicrophoneAvailable) {
    return <span>Please allow access to the microphone</span>;
  }

  return (
    <>
      {show_conversation && (
        <div style={{ display: "flex", flexDirection: "column" }}>
          <span>You said: {prevScript}</span>
          <span>Listening: {listening ? "on" : "off"}</span>
          <span>Clear Transcript On Listen: {clearTranscriptOnListen ? "on" : "off"}</span>
        </div>
      )}
    </>
  );
};

export default Dictaphone_ss;