import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Streamlit } from "streamlit-component-lib";
import SpeechRecognition from "react-speech-recognition";
import Dictaphone from "./Dictaphone";
// import Dictaphone_ss from "./Dictaphone_ss";
import * as faceapi from "@vladmandic/face-api";
import DOMPurify from 'dompurify';

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
    self_image,
    api_audio,
    client_user,
    force_db_root,
    before_trigger,
  } = kwargs;
  const [imageSrc, setImageSrc] = useState(kwargs.self_image);
  const [imageSrc_name, setImageSrc_name] = useState(kwargs.self_image);

  const [message, setMessage] = useState("");
  const [answers, setAnswers] = useState([]);
  const [listenAfterReply, setListenAfterReply] = useState(false);

  const [modelsLoaded, setModelsLoaded] = useState(false);
  const [captureVideo, setCaptureVideo] = useState(false);
  const [textString, setTextString] = useState("");
  const [apiInProgress, setApiInProgress] = useState(false); // Added state for API in progress
  const [speaking, setSpeakingInProgress] = useState(false); // Added state for API in progress

  const [listenButton, setlistenButton] = useState(false); // Added state for API in progress
  const [session_listen, setsession_listen] = useState(false);

  const [before_trigger_vars, before_trigger_] = useState(kwargs.before_trigger); 
  const faceData = useRef([]);
  const faceTriggered = useRef(false);
  const videoRef = useRef();
  const videoHeight = 480;
  const videoWidth = 640;
  const canvasRef = useRef();
  const audioRef = useRef(null);
  

  const [isListening, setIsListening] = useState(false);
  const [UserUsedChatWindow, setUserUsedChatWindow] = useState(false);

  const [buttonName, setButtonName] = useState("Click and Ask");
  const [buttonName_listen, setButtonName_listen] = useState("Listening");

  const [showImage, setShowImage] = useState(false); // Step 1: Define showImage state

  const toggleShowImage = () => { // Step 2: Create toggle function
    setShowImage((prevShowImage) => !prevShowImage);
  };

  useEffect(() => {
    const handleResize = () => {
        // Trigger a re-render on resize to adjust layout
        setWindowWidth(window.innerWidth);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
}, []);

  useEffect(() => {
    if (self_image) {
      // Fetch the image data from the API endpoint
      fetchImageData(self_image);
    }
  }, [self_image]);

  const fetchImageData = async (imageUrl) => {
    try {
      const response = await axios.get(`${api_audio}${imageUrl}`, {
        responseType: 'blob', // Set responseType to 'blob' to handle file response
      });
      const objectUrl = URL.createObjectURL(response.data); // Use a different variable name here
      setImageSrc(objectUrl);
      setImageSrc_name(imageUrl)
    } catch (error) {
      console.error('Error fetching image data:', error);
    }
  };

  const checkListeningStatus = () => {
    // Check if continuous listening is active
    if (!SpeechRecognition.browserSupportsContinuousListening()) {
      // If not, restart continuous listening
      startContinuousListening();
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
    setIsListening(true)
  };

  const stopListening = () => {
    SpeechRecognition.stopListening();
    setIsListening(false);
    console.log("Stopping Listening, isListening=", isListening)

    
  }
  
  const startListening = () => {
    SpeechRecognition.startListening();
  };

  const listenContinuously = () =>{
    if (isListening) {
      setIsListening(false)
    }
    else {
    SpeechRecognition.startListening({
      continuous: true,
      language: "en-GB",
    })
    setIsListening(true)
  }
    }

  const listenSession = () =>{
    if (session_listen) {
    setsession_listen(false)
  }
  else{
    setsession_listen(true)
  }
    }

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
      // console.log("faceData.current :>> ", faceData.current);
    }, 3000);
    return () => clearInterval(interval);
  }, []);


  const handleInputText = (event) => {
    // Update the state with the input text
    setTextString(event.target.value);
  
    // Set a variable to indicate that the user used the chat window
    setUserUsedChatWindow(true);
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

  const click_listenButton = () => {
    setlistenButton(true)
    listenContinuously()
    setButtonName("Please Speak")
    console.log("listening button listen click");
    console.log(listenButton);
  };

  function isHTML(str) {
    return /^</.test(str);
  }

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
        self_image: imageSrc_name,
        face_data: faceData.current,
        refresh_ask: refresh_ask,
        client_user: client_user,
        force_db_root:force_db_root,
        session_listen:session_listen,
        before_trigger_vars:before_trigger_vars,
      };
      console.log("api");
      const { data } = await axios.post(api, body);
      console.log("data :>> ", data, body);
      if (data["self_image"] && data["self_image"] !== imageSrc_name) {
        fetchImageData(data["self_image"]); // Fetch image data if it's different
      }
      setAnswers(data["text"]);
      g_anwers = [...data["text"]];
      
      if (audioRef.current) {
        audioRef.current.pause(); // Pause existing playback if any
      }

      if (data["audio_path"]) {
        const apiUrlWithFileName = `${api_audio}${data["audio_path"]}`;
        audioRef.current = new Audio(apiUrlWithFileName);
    
        try {
            await audioRef.current.play();
            
            // Set state to indicate speaking in progress
            setSpeakingInProgress(true);
            setButtonName_listen("Speaking");
    
            // Await playback completion
            await new Promise((resolve) => {
                audioRef.current.onended = () => {
                    console.log("Audio playback finished.");
                    resolve();
                };
            });
    
        } catch (error) {
            console.error("Audio playback error:", error);
        } finally {
            // Cleanup or reset after playback
            audioRef.current = null;
            setSpeakingInProgress(false);
            setButtonName_listen("Listen");
        }
    }

      setButtonName("Click and Ask")
      setButtonName_listen("Listening")
      setSpeakingInProgress(false)
      setApiInProgress(false)

      console.log("Audio ENDED MOVE TO SET VARS .");
      
      setListenAfterReply(data["listen_after_reply"]);
      console.log("listen after reply", data["listen_after_reply"]);



      if (data["page_direct"] !== false && data["page_direct"] !== null) {
        console.log("api has page direct", data["page_direct"]);
        // window.location.reload();
        window.location.href = data["page_direct"];
      }
      
      if (listenAfterReply==true && !listenButton && !UserUsedChatWindow) {
        listenContinuously()
        setButtonName_listen("Awaiting your Answer please speak")
      }
      else if (listenButton) {
      setlistenButton(false)
      }
      else if (UserUsedChatWindow){
        setUserUsedChatWindow(false)
      }
      else {
        listenContinuously()
        setButtonName_listen("listeing for key word")
      }
      
      console.log("listing end", isListening)

    } catch (error) {
      console.log("api call on listen failed!", error);
      setApiInProgress(false); // Set API in progress to false on error
      setlistenButton(false)
    }
  };

  useEffect(() => {
    // Function to resize the window
    const resizeWindow = () => {
      window.resizeBy(0, 1); // Resize the window by 1 pixel vertically
    };

    // Resize the window after the response finishes
    // Replace `RESPONSE_FINISH_EVENT` with the event that indicates the response finished
    window.addEventListener('RESPONSE_FINISH_EVENT', resizeWindow);

    // Cleanup the event listener
    return () => {
      window.removeEventListener('RESPONSE_FINISH_EVENT', resizeWindow);
    };
  }, []); // Run only once after component mounts

  
  const background_color_chat = refresh_ask.color_dict?.background_color_chat || 'transparent';
  const splitImage = self_image.split('.')[0]; // Split by dot
  const placeholder = `Chat with ${splitImage}`;

  return (
    <>
      <div className="p-2">
        <div style={{ display: 'flex', flexDirection: 'row', width: '100%' }}>
          {/* Image or video section */}
          {showImage && (
            <div style={{ flex: 1 }}>
              {imageSrc && (
                imageSrc.toLowerCase().endsWith(".mp4") ? (
                  <video
                    style={{ maxWidth: '100%' }}
                    height={height || 100}
                    width={width || 100}
                    controls
                    autoPlay
                    loop={false}
                    muted
                  >
                    <source src={imageSrc} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <img src={imageSrc} height={height || 100} width={width || 100} style={{ maxWidth: '100%' }} />
                )
              )}
            </div>
          )}
  
          {/* Chat window, taking full width if no image is shown */}
          <div style={{ flex: showImage ? 1 : '100%', overflowY: 'auto', maxHeight: '400px' }}>
          {show_conversation && (
            <div
              style={{
                border: '2px solid #2980b9', // Outer border
                borderRadius: '6px', // Slightly round the corners of the outer border
                overflowY: 'auto', // Enable vertical scrolling
                maxHeight: '400px', // Set maximum height for scrolling
                padding: '10px', // Add padding inside the outer border
              }}
            >
            {answers.map((answer, idx) => (
              <div
                key={idx}
                style={{
                  marginBottom: '5px',
                  padding: '5px',
                  borderRadius: '4px',
                  border: '1px solid #ccc', // Inner border for each message
                  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)', // Optional: add shadow for depth
                  // backgroundColor: answer.resp ? 'lightyellow' : '#f2f2f2' // Background color if needed
                }}
              >
                <div className="chat-user"   style={{
                                                  backgroundColor: '#f2f2f2',
                                                  textAlign: 'right', // Align text to the right
                                                  marginLeft: 'auto', // Push content to the right side
                                                  padding: '5px', // Optional padding for spacing
                                                }}>
                  {client_user}: <span dangerouslySetInnerHTML={{ __html: answer.user }} />
                </div>
                <div className="chat-resp" style={{ display: 'flex', alignItems: 'flex-start', backgroundColor: background_color_chat }}>
                  {/* Displaying image on the left side */}
                  <div className="chat-image" style={{ marginRight: '10px' }}>
                    <img src={imageSrc} alt="response" style={{ width: '50px' }} /> {/* Adjusted width */}
                  </div>
                  {/* Rendering the response text with HTML formatting */}
                  <div style={{ flex: 1 }}> {/* Flex container to allow text wrapping */}
                    <span dangerouslySetInnerHTML={{ __html: answer.resp || "thinking..." }} />
                  </div>
                </div>
              </div>
            ))}
            </div>
          )}
          </div>
        </div>

        {/* Input text section */}
        {input_text && (
          <>
          <hr style={{ margin: '20px 0' }} />
            <div className="form-group">
              <input
                className="form-control"
                type="text"
                placeholder={placeholder}
                value={textString}
                onChange={handleInputText}
                onKeyDown={handleOnKeyDown}
              />
            </div>
            <hr style={{ margin: '20px 0' }} />
          </>
        )}

      {/* Buttons with indicators under each */}
      <div style={{ display: 'flex', marginTop: '10px' }}>
        {/* Button 1 with Listen Indicator */}
        <div style={{ flex: 1, textAlign: 'center' }}>
          <button
            style={{
              fontSize: '12px',
              padding: '5px',
              margin: '5px 0',
              backgroundColor: '#3498db',
              color: 'white',
              border: '1px solid #2980b9',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
            onClick={click_listenButton}
          >
            {buttonName}
          </button>
          {isListening && (
            <div
              style={{
                width: '100%',
                height: '10px',
                backgroundImage: 'linear-gradient(90deg, green, transparent 50%, green)',
                animation: 'flashLine 1s infinite',
                marginTop: '5px',
              }}
            >
              <div style={{ fontSize: '12px', color: 'black' }}>{buttonName_listen}</div>
            </div>
          )}
        </div>

        {/* Button 2 with Conversational Mode Indicator */}
        <div style={{ flex: 1, textAlign: 'center' }}>
          <button
            style={{
              fontSize: '12px',
              padding: '5px',
              margin: '5px 0',
              backgroundColor: '#2980b9',
              color: 'white',
              border: '1px solid #2980b9',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
            onClick={listenContinuously}
          >
            Conversational Mode
          </button>
          {speaking && (
            <div
              style={{
                width: '100%',
                height: '10px',
                background: 'linear-gradient(to right, blue, transparent, purple)',
                animation: 'waveAnimation 1s infinite',
                marginTop: '5px',
                borderRadius: '10px',
              }}
            >
              <div style={{ fontSize: '12px', color: 'black' }}>Speaking</div>
            </div>
          )}
        </div>

        {/* Button 3 with Session Started Indicator */}
        <div style={{ flex: 1, textAlign: 'center' }}>
          <button
            style={{
              fontSize: '12px',
              padding: '5px',
              margin: '5px 0',
              backgroundColor: '#2980b9',
              color: 'white',
              border: '1px solid #2980b9',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
            onClick={listenSession}
          >
            Start A Session
          </button>
          {session_listen && (
            <div
              style={{
                width: '100%',
                height: '10px',
                backgroundImage: 'linear-gradient(90deg, orange, transparent 50%, orange)',
                animation: 'flashLine 1s infinite',
                marginTop: '5px',
              }}
            >
              <div style={{ fontSize: '12px', color: 'black' }}>Session Started</div>
            </div>
          )}
        </div>

        {/* Toggle Image Button */}
        <div style={{ flex: 1, textAlign: 'center' }}>
          <button
            style={{
              fontSize: '12px',
              padding: '5px',
              margin: '5px 0',
              backgroundColor: '#7f8c8d',
              color: 'white',
              border: '1px solid #7f8c8d',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
            onClick={toggleShowImage}
          >
            {showImage ? "Hide Image" : "Show Image"}
          </button>
        </div>
      </div>

        {/* Dictaphone component */}
        <div className="p-2">
          <Dictaphone
            commands={commands}
            myFunc={myFunc}
            listenAfterReply={listenAfterReply}
            no_response_time={no_response_time}
            show_conversation={show_conversation}
            apiInProgress={apiInProgress}
            listenButton={listenButton}
            session_listen={session_listen}
          />
        </div>
  

      </div>
    </>
  );
}

export default CustomVoiceGPT;
