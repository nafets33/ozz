import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Streamlit } from "streamlit-component-lib";
import SpeechRecognition from "react-speech-recognition";
import Dictaphone from "./Dictaphone";
import * as faceapi from "@vladmandic/face-api";

let timer = null;
let faceTimer = null;
let g_anwers = [];
let firstFace = false;

const CustomVoiceGPT = (props) => {
  const { api, kwargs = {} } = props;
  const {
    commands,
    height,
    width,
    show_conversation,
    show_video,
    input_text,
    no_response_time,
    face_recon,
    api_key,
    refresh_ask,
    before_trigger,
    api_audio,
    client_user,
  } = kwargs;
  const [imageSrc, setImageSrc] = useState(kwargs.self_image);
  const [message, setMessage] = useState("");
  const [answers, setAnswers] = useState([]);
  const [listenAfterReply, setListenAfterReply] = useState(false);
  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [captureVideo, setCaptureVideo] = useState(false);
  const [textString, setTextString] = useState("");
  const [apiInProgress, setApiInProgress] = useState(false); // Added state for API in progress

  const faceData = useRef([]);
  const faceTriggered = useRef(false);
  const videoRef = useRef();
  const videoHeight = 480;
  const videoWidth = 640;
  const canvasRef = useRef();
  const audioRef = useRef(null);

  const [isListening, setIsListening] = useState(true);
  const [isGreenLightOn, setIsGreenLightOn] = useState(false);


  // ... (other code)

  const checkListeningStatus = () => {
    // Check if continuous listening is active
    if (!SpeechRecognition.browserSupportsContinuousListening()) {
      // If not, restart continuous listening
      startContinuousListening();
    }
  };


  const handleInputText = (e) => {
    const { value } = e.target;
    setTextString(value);
  };

  const handleOnKeyDown = (e) => {
    if (e.key === "Enter") {
      console.log("textString :>> ", textString);
      myFunc(textString, { api_body: { keyword: "" } }, 4);
      setTextString("");
    }
  };

  const startVideo = () => {
    setCaptureVideo(true);
    navigator.mediaDevices
      .getUserMedia({ video: { width: 300 } })
      .then((stream) => {
        let video = videoRef.current;
        video.srcObject = stream;
        video.play();
      })
      .catch((err) => {
        console.error("error:", err);
      });
  };

  const handleVideoOnPlay = () => {
    setInterval(async () => {
      if (canvasRef && canvasRef.current) {
        canvasRef.current.innerHTML = faceapi.createCanvasFromMedia(
          videoRef.current
        );
        const displaySize = {
          width: videoWidth,
          height: videoHeight,
        };

        faceapi.matchDimensions(canvasRef.current, displaySize);

        const detections = await faceapi
          .detectAllFaces(
            videoRef.current,
            new faceapi.TinyFaceDetectorOptions()
          )
          .withFaceLandmarks()
          .withFaceExpressions();

        const resizedDetections = faceapi.resizeResults(detections, displaySize);

        if (resizedDetections.length > 0) {
          faceData.current = resizedDetections;
          if (!faceTriggered.current && face_recon) {
            myFunc("", { api_body: { keyword: "" } }, 2);
            faceTriggered.current = true;
          }
        } else {
          faceTimer && clearTimeout(faceTimer);
          setTimeout(() => {
            faceData.current = [];
          }, 1000);
        }

        if (resizedDetections.length > 0 && !firstFace) {
          firstFace = true;
          if (kwargs.hello_audio) {
            const audio = new Audio(kwargs.hello_audio);
            audio.play();
          }
        }

        canvasRef &&
          canvasRef.current &&
          canvasRef.current
            .getContext("2d")
            .clearRect(0, 0, videoWidth, videoHeight);
        canvasRef &&
          canvasRef.current &&
          faceapi.draw.drawDetections(canvasRef.current, resizedDetections);
        canvasRef &&
          canvasRef.current &&
          faceapi.draw.drawFaceLandmarks(canvasRef.current, resizedDetections);
        canvasRef &&
          canvasRef.current &&
          faceapi.draw.drawFaceExpressions(
            canvasRef.current,
            resizedDetections
          );
      }
    }, 300);
  };

  const closeWebcam = () => {
    videoRef.current.pause();
    videoRef.current.srcObject.getTracks()[0].stop();
    setCaptureVideo(false);
  };

  const myFunc = async (ret, command, type) => {
    setMessage(` (${command["api_body"]["keyword"]}) ${ret},`);
    const text = [...g_anwers, { user: ret }];
    setAnswers([...text]);
    try {
      console.log("api call on listen...", command);
      setApiInProgress(true); // Set API in progress to true
      stopListening()

      const body = {
        tigger_type: type,
        api_key: api_key,
        text: text,
        self_image: imageSrc,
        face_data: faceData.current,
        refresh_ask: refresh_ask,
        client_user: client_user,
      };
      console.log("api");
      const { data } = await axios.post(api, body);
      console.log("data :>> ", data, body);
      data["self_image"] && setImageSrc(data["self_image"]);
      if (audioRef.current) {
        audioRef.current.pause(); // Pause existing playback if any
      }

      // audioRef.current = new Audio(data["audio_path"]);
      const apiUrlWithFileName = `${api_audio}${data["audio_path"]}`;
      audioRef.current = new Audio(apiUrlWithFileName);
      audioRef.current.play();

      // Wait for the onended callback to complete before continuing
      await new Promise((resolve) => {
        audioRef.current.onended = () => {
          console.log("Audio playback finished.");
          resolve();
        };
      });

      console.log("Audio ENDED MOVE TO SET VARS .");
      setAnswers(data["text"]);
      g_anwers = [...data["text"]];
      
      setListenAfterReply(data["listen_after_reply"]);
      console.log("listen after reply", data["listen_after_reply"]);

      if (data["page_direct"] !== false && data["page_direct"] !== null) {
        console.log("api has page direct", data["page_direct"]);
        // window.location.reload();
        window.location.href = data["page_direct"];
      }
      
      listenContinuously();
      setApiInProgress(false); // Set API in progress to false after completion

    } catch (error) {
      console.log("api call on listen failed!", error);
      setApiInProgress(false); // Set API in progress to false on error
    }
  };

  useEffect(() => {
    Streamlit.setFrameHeight();

    // Check listening status every minute
    const intervalId = setInterval(() => {
      if (!SpeechRecognition.browserSupportsContinuousListening()) {
        // If continuous listening is not active, start it
        console.log("LISTEN STOPPED TURNING BACK ON", error);
        listenContinuously();
      }
    }, 60000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  const startContinuousListening = () => {
    // Start continuous listening
    SpeechRecognition.startListening({
      continuous: true,
      language: "en-GB",
    });
    setIsListening(true);
  };

  const stopListening = () => {
    SpeechRecognition.stopListening();
  };
  const startListening = () => {
    SpeechRecognition.startListening();
  };

  const listenContinuously = () =>
    SpeechRecognition.startListening({
      continuous: true,
      language: "en-GB",
    });
  const listenContinuouslyInChinese = () =>
    SpeechRecognition.startListening({
      continuous: true,
      language: "zh-CN",
    });
  const listenOnce = () =>
    SpeechRecognition.startListening({ continuous: false });

  
  useEffect(() => {
    const loadModels = async () => {
      const MODEL_URL = process.env.PUBLIC_URL + "/models";

      Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
        faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
        faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL),
        faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL),
        faceapi.nets.ageGenderNet.loadFromUri(MODEL_URL),
      ]).then(() => setModelsLoaded(true));
    };
    loadModels();
    const interval = setInterval(() => {
      console.log("faceData.current :>> ", faceData.current);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      <div className="p-2">
      <div>
          {imageSrc && imageSrc.toLowerCase().endsWith(".mp4") ? (
            <video
              height={height || 100}
              width={width || 100}
              controls
              autoPlay={true} // Use a variable to control autoplay shouldAutoplay
              loop={false}
              muted
            >
              <source src={imageSrc} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          ) : (
            <img src={imageSrc} height={height || 100} width={width || 100} />
          )}
          {/* Flashing green line indicator */}
          {apiInProgress && (
            <div
              style={{
                position: 'absolute',
                top: '10px',
                left: '0',
                width: '100%',
                height: '4px',
                background: 'linear-gradient(90deg, green, transparent 50%, green)',
                animation: 'flashLine 1s infinite',
              }}
            />
          )}
        </div>
        <div className="p-2">
          <Dictaphone
            commands={commands}
            myFunc={myFunc}
            listenAfterReply={listenAfterReply}
            noResponseTime={no_response_time}
            show_conversation={show_conversation}
            apiInProgress={apiInProgress} // Pass down API in progress
          />
        </div>
        <div className="form-group">
          <button className="btn btn-primary" onClick={listenContinuously}>
            Listen continuously
          </button>
        </div>
        {input_text && (
          <div className="form-group">
            <input
              className="form-control"
              type="text"
              placeholder="Chat with Hoots"
              value={textString}
              onChange={handleInputText}
              onKeyDown={handleOnKeyDown}
            />
          </div>
        )}
        {show_conversation === true && (
          <>
            <div> You: {message}</div>
            {answers.map((answer, idx) => (
              <div key={idx}>
                <div>-user: {answer.user}</div>
                <div>
                  -resp: {answer.resp ? answer.resp : "thinking..."}
                </div>
              </div>
            ))}
          </>
        )}
      </div>
      <div>
        {/* ... (rest of your code) */}
      </div>
      <div>
        {face_recon && (
          <div style={{ textAlign: "center", padding: "10px" }}>
            {captureVideo && modelsLoaded ? (
              <button
                onClick={closeWebcam}
                style={{
                  cursor: "pointer",
                  backgroundColor: "green",
                  color: "white",
                  padding: "15px",
                  fontSize: "25px",
                  border: "none",
                  borderRadius: "10px",
                }}
              >
                Close Webcam
              </button>
            ) : (
              <button
                onClick={startVideo}
                style={{
                  cursor: "pointer",
                  backgroundColor: "green",
                  color: "white",
                  padding: "15px",
                  fontSize: "25px",
                  border: "none",
                  borderRadius: "10px",
                }}
              >
                Open Webcam
              </button>
            )}
          </div>
        )}
        {captureVideo ? (
          modelsLoaded ? (
            <div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "center",
                  padding: "10px",
                  position: show_video ? "" : "absolute",
                  opacity: show_video ? 1 : 0.3,
                }}
              >
                <video
                  ref={videoRef}
                  height={videoHeight}
                  width={videoWidth}
                  onPlay={handleVideoOnPlay}
                  style={{ borderRadius: "10px" }}
                />
                <canvas ref={canvasRef} style={{ position: "absolute" }} />
              </div>
            </div>
          ) : (
            <div>loading...</div>
          )
        ) : (
          <></>
        )}
      </div>
    </>
  );
};

export default CustomVoiceGPT;
