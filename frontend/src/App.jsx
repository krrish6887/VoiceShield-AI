import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldCheck,
  Mic2,
  Upload,
  Activity,
  LockKeyhole,
  AudioWaveform,
  ScanSearch,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  LoaderCircle,
  RotateCcw,
  FileAudio,
} from "lucide-react";

import "./App.css";

function App() {
  const fileInputRef = useRef(null);

  const [selectedFile, setSelectedFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // ==========================================
  // LIVE CALL STATE
  // ==========================================

  const [liveMode, setLiveMode] = useState(false);
  const [liveAnalyzing, setLiveAnalyzing] = useState(false);
  const [liveResult, setLiveResult] = useState(null);

  const mediaRecorderRef = useRef(null);
  const liveStreamRef = useRef(null);

  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
  if (!result) {
    setAnimatedScore(0);
    return;
  }

  const target = Number(result.ai_score) || 0;
  const duration = 1200;
  const startTime = performance.now();

  let animationFrame;

  const animate = (currentTime) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    const easedProgress = 1 - Math.pow(1 - progress, 3);

    setAnimatedScore(target * easedProgress);

    if (progress < 1) {
      animationFrame = requestAnimationFrame(animate);
    }
  };

  animationFrame = requestAnimationFrame(animate);

  return () => {
    cancelAnimationFrame(animationFrame);
  };
}, [result]);

// ==========================================
// START LIVE MICROPHONE
// ==========================================

const startLiveAnalysis = async () => {

  try {

    const stream =
      await navigator.mediaDevices.getUserMedia({
        audio: true
      });

    liveStreamRef.current = stream;

    const mimeType =
      MediaRecorder.isTypeSupported(
        "audio/webm;codecs=opus"
      )
        ? "audio/webm;codecs=opus"
        : "audio/webm";

    const recorder = new MediaRecorder(
      stream,
      {
        mimeType
      }
    );

    mediaRecorderRef.current = recorder;

    setLiveMode(true);
    setLiveAnalyzing(true);
    setLiveResult(null);


    recorder.ondataavailable = async (event) => {

      if (
        event.data &&
        event.data.size > 0
      ) {

        await analyzeLiveChunk(
          event.data
        );
      }
    };


    recorder.onstop = () => {

      if (liveStreamRef.current) {

        liveStreamRef.current
          .getTracks()
          .forEach(
            (track) => track.stop()
          );
      }

      setLiveAnalyzing(false);
    };


    // Record in 8-second intervals
    recorder.start(8000);

  } catch (error) {

    console.error(
      "Microphone access error:",
      error
    );

    alert(
      "Unable to access microphone. Please allow microphone permission."
    );
  }
};
// ==========================================
// SEND LIVE CHUNK TO BACKEND
// ==========================================

const analyzeLiveChunk = async (audioBlob) => {

  try {

    const formData = new FormData();

    formData.append(
      "file",
      audioBlob,
      "live_chunk.webm"
    );

    formData.append(
      "transaction_sensitivity",
      "HIGH"
    );

    formData.append(
      "caller_verified",
      "false"
    );


    const response = await fetch(
      "http://127.0.0.1:8000/analyze-chunk",
      {
        method: "POST",
        body: formData
      }
    );


    if (!response.ok) {

      throw new Error(
        `Live analysis failed: ${response.status}`
      );
    }


    const data =
      await response.json();


    console.log(
      "Live chunk result:",
      data
    );


    if (data.error) {

      console.error(
        data.error
      );

      return;
    }


    setLiveResult(data);

  } catch (error) {

    console.error(
      "Live chunk analysis error:",
      error
    );
  }
};

// ==========================================
// STOP LIVE MICROPHONE
// ==========================================

const stopLiveAnalysis = () => {

  if (
    mediaRecorderRef.current &&
    mediaRecorderRef.current.state !== "inactive"
  ) {

    mediaRecorderRef.current.stop();
  }

  if (liveStreamRef.current) {

    liveStreamRef.current
      .getTracks()
      .forEach(
        (track) => track.stop()
      );
  }

  setLiveMode(false);
  setLiveAnalyzing(false);
};


  // ==========================================
  // File Selection
  // ==========================================

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setSelectedFile(file);
    setResult(null);
    setError("");
  }

  // ==========================================
  // Open File Picker
  // ==========================================

  function selectAudio() {
    fileInputRef.current?.click();
  }

  // ==========================================
  // Analyze Audio
  // ==========================================

  async function analyzeAudio() {
    if (!selectedFile) {
      return;
    }

    setAnalyzing(true);
    setAnalysisProgress(10);
    setResult(null);
    setError("");

    const formData = new FormData();

formData.append("file", selectedFile);

formData.append(
  "transaction_sensitivity",
  "HIGH"
);

formData.append(
  "transaction_type",
  "Fund Transfer"
);

formData.append(
  "transaction_amount",
  "250000"
);

formData.append(
  "caller_verified",
  "false"
);

formData.append(
  "caller_name",
  "Rahul Sharma"
);

    setAnalysisProgress(25);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          `Server returned HTTP ${response.status}`
        );
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setAnalysisProgress(90);

      setResult(data);

      setAnalysisProgress(100);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to analyze the audio. Make sure the VoiceShield-AI backend is running."
      );
    } finally {
      setAnalyzing(false);
    }
  }

  // ==========================================
  // Reset
  // ==========================================

  function resetAnalysis() {
    setSelectedFile(null);
    setResult(null);
    setError("");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  // ==========================================
  // Result Icon
  // ==========================================

  function getResultIcon() {
    if (!result) {
      return null;
    }

    if (result.prediction === "AI-GENERATED") {
      return <AlertTriangle size={28} />;
    }

    if (result.prediction === "SUSPICIOUS") {
      return <AlertTriangle size={28} />;
    }

    return <CheckCircle2 size={28} />;
  }

  return (
    <div className="app">

      {/* Background effects */}

      <div className="bg-glow glow-one"></div>
      <div className="bg-glow glow-two"></div>


      {/* ======================================
          NAVBAR
      ====================================== */}

      <motion.nav
        className="navbar"
        initial={{
          opacity: 0,
          y: -20,
        }}
        animate={{
          opacity: 1,
          y: 0,
        }}
        transition={{
          duration: 0.6,
        }}
      >

        <div className="brand">

          <div className="brand-icon">
            <ShieldCheck size={22} />
          </div>

          <div>

            <div className="brand-name">
              VoiceShield<span>-AI</span>
            </div>

            <div className="brand-subtitle">
              VOICE AUTHENTICITY INTELLIGENCE
            </div>

          </div>

        </div>


        <div className="system-status">

          <span className="status-dot"></span>

          SYSTEM ONLINE

        </div>

      </motion.nav>


      {/* ======================================
          MAIN
      ====================================== */}

      <main className="main">


        {/* ====================================
            HERO
        ==================================== */}

        <motion.section
          className="hero"
          initial={{
            opacity: 0,
            y: 25,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            duration: 0.7,
          }}
        >

          <div className="eyebrow">

            <ScanSearch size={16} />

            AI-POWERED AUDIO FORENSICS

          </div>


          <h1>
            Detect the voice.
            <br />
            <span>
              Protect the conversation.
            </span>
          </h1>


          <p>
            VoiceShield-AI analyzes speech patterns using
            deep-learning models to identify synthetic and
            AI-generated voices.
          </p>

        </motion.section>


        {/* ====================================
            ANALYSIS CARD
        ==================================== */}

        <motion.section
          className="upload-card"
          initial={{
            opacity: 0,
            scale: 0.97,
          }}
          animate={{
            opacity: 1,
            scale: 1,
          }}
          transition={{
            duration: 0.7,
            delay: 0.15,
          }}
        >

          <div className="card-header">

            <div>

              <div className="card-label">
                AUDIO ANALYSIS
              </div>

              <h2>
                Verify a voice recording
              </h2>

            </div>


            <div className="secure-badge">

              <LockKeyhole size={15} />

              PRIVATE ANALYSIS

            </div>

          </div>


          {/* ==================================
              FILE INPUT
          ================================== */}

          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*"
            onChange={handleFileChange}
            style={{ display: "none" }}
          />


          {/* ==================================
              UPLOAD AREA
          ================================== */}

          <motion.div
            className="upload-zone"
            whileHover={{
              scale: 1.005,
            }}
          >

            <motion.div
              className="mic-circle"
              animate={
                analyzing
                  ? {
                      scale: [1, 1.08, 1],
                      rotate: [0, 5, -5, 0],
                    }
                  : {
                      scale: [1, 1.04, 1],
                    }
              }
              transition={{
                duration: analyzing ? 1 : 2.2,
                repeat: Infinity,
              }}
            >

              {analyzing ? (
                <LoaderCircle
                  size={30}
                  className="spin"
                />
              ) : selectedFile ? (
                <FileAudio size={30} />
              ) : (
                <Mic2 size={30} />
              )}

            </motion.div>


            <AnimatePresence mode="wait">

              {analyzing ? (

                <motion.div
  key="analyzing"
  className="analysis-panel"

  initial={{
    opacity: 0,
    scale: 0.96,
    y: 15,
  }}

  animate={{
    opacity: 1,
    scale: 1,
    y: 0,
  }}

  exit={{
    opacity: 0,
    scale: 0.96,
  }}

  transition={{
    duration: 0.45,
  }}
>

  {/* ANALYSIS ICON */}

  <motion.div
    className="analysis-orb"

    animate={{
      scale: [1, 1.08, 1],
      boxShadow: [
        "0 0 20px rgba(34,211,238,0.15)",
        "0 0 45px rgba(34,211,238,0.35)",
        "0 0 20px rgba(34,211,238,0.15)",
      ],
    }}

    transition={{
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
    }}
  >

    <LoaderCircle
      size={34}
      className="analysis-spinner"
    />

  </motion.div>


  {/* TITLE */}

  <div className="analysis-content">

    <div className="analysis-label">
      AI FORENSIC ANALYSIS
    </div>

    <h3>
      Analyzing voice...
    </h3>

    <p>
      Running Wav2Vec2 deep-learning detection
    </p>


    {/* WAVEFORM */}

    <div className="analysis-waveform">

      {[...Array(28)].map((_, index) => (

        <motion.span
          key={index}

         animate={{
  height: [
    `${8 + (index % 5) * 4}px`,
    `${22 + (index % 4) * 5}px`,
    `${10 + (index % 3) * 4}px`,
  ],
}}

transition={{
  duration: 0.8 + (index % 4) * 0.12,
  repeat: Infinity,
  delay: index * 0.035,
}}
        />

      ))}

    </div>


    {/* PROGRESS */}

    <div className="analysis-progress-header">

      <span>
        Processing audio signal
      </span>

      <span>
        {analysisProgress}%
      </span>

    </div>


    <div className="analysis-progress-track">

      <motion.div
        className="analysis-progress-bar"

        animate={{
          width: `${analysisProgress}%`,
        }}

        transition={{
          duration: 0.5,
          ease: "easeOut",
        }}
      />

    </div>


    {/* STATUS */}

    <div className="analysis-status">

      <motion.span
        animate={{
          opacity: [0.4, 1, 0.4],
        }}

        transition={{
          duration: 1.2,
          repeat: Infinity,
        }}
      />

      Secure local analysis in progress

    </div>

  </div>

</motion.div>

              ) : selectedFile ? (

                <motion.div
                  key="selected"
                  initial={{
                    opacity: 0,
                    y: 10,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                >

                  <h3>
                    {selectedFile.name}
                  </h3>

                  <p>
                    {(selectedFile.size / 1024 / 1024).toFixed(2)}
                    {" MB"} • Ready for analysis
                  </p>

                </motion.div>

              ) : (

                <motion.div
                  key="empty"
                  initial={{
                    opacity: 0,
                  }}
                  animate={{
                    opacity: 1,
                  }}
                >

                  <h3>
                    Drop an audio recording here
                  </h3>

                  <p>
                    or browse files from your device
                  </p>

                </motion.div>

              )}

            </AnimatePresence>


            {!analyzing && !selectedFile && (

              <button
                className="upload-button"
                onClick={selectAudio}
              >

                <Upload size={18} />

                Select Audio

              </button>

            )}


            {selectedFile && !analyzing && !result && (

              <button
                className="upload-button"
                onClick={analyzeAudio}
              >

                <ScanSearch size={18} />

                Analyze Voice

              </button>

            )}


            {selectedFile && !analyzing && (

              <button
                className="secondary-button"
                onClick={selectAudio}
              >

                Choose Different File

              </button>

            )}


            <div className="supported">
              WAV • MP3 • M4A • FLAC
            </div>

          </motion.div>


          {/* ==================================
              ERROR
          ================================== */}

          <AnimatePresence>

            {error && (

              <motion.div
                className="error-message"
                initial={{
                  opacity: 0,
                  y: 10,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                exit={{
                  opacity: 0,
                }}
              >

                <XCircle size={18} />

                {error}

              </motion.div>

            )}

          </AnimatePresence>


          {/* ==================================
              PIPELINE
          ================================== */}

          <div className="pipeline">

            <div
              className={`pipeline-item ${
                selectedFile ? "active" : ""
              }`}
            >

              <div className="pipeline-icon">

                <AudioWaveform size={18} />

              </div>

              <div>

                <strong>
                  Audio Input
                </strong>

                <span>
                  {selectedFile ? "Loaded" : "Ready"}
                </span>

              </div>

            </div>


            <div className="pipeline-line"></div>


            <div
              className={`pipeline-item ${
                analyzing ? "active analyzing" : ""
              }`}
            >

              <div className="pipeline-icon">

                <Activity size={18} />

              </div>

              <div>

                <strong>
                  Voice Analysis
                </strong>

                <span>
                  Wav2Vec2
                </span>

              </div>

            </div>


            <div className="pipeline-line"></div>


            <div
              className={`pipeline-item ${
                result ? "active" : ""
              }`}
            >

              <div className="pipeline-icon">

                <ShieldCheck size={18} />

              </div>

              <div>

                <strong>
                  Authenticity
                </strong>

                <span>
                  {result ? "Complete" : "AI Detection"}
                </span>

              </div>

            </div>

          </div>

        </motion.section>


        {/* ====================================
            RESULT
        ==================================== */}

        {/* ==========================================
              LIVE CALL ANALYSIS
          ========================================== */}

          <motion.div
            className="live-call-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="live-call-header">

              <div>

                <span className="section-eyebrow">
                  REAL-TIME SECURITY
                </span>

                <h3>
                  Live Call Analysis
                </h3>

                <p>
                  Analyze microphone audio in real time
                  for possible AI voice impersonation.
                </p>

              </div>

              <span className="demo-badge">
                LIVE
              </span>

            </div>


            {!liveMode ? (

              <button
                className="live-start-btn"
                onClick={startLiveAnalysis}
              >
                🎙 START LIVE ANALYSIS
              </button>

            ) : (

              <button
                className="live-stop-btn"
                onClick={stopLiveAnalysis}
              >
                ■ STOP LIVE ANALYSIS
              </button>

            )}


            {liveMode && (

              <div className="live-status">

                <div className="live-indicator">

                  <span className="live-dot"></span>

                  MICROPHONE ACTIVE

                </div>


                {!liveResult ? (

                  <div className="live-waiting">
                    Listening for voice...
                  </div>

                ) : (

                  <div className="live-result">

                    <div className="live-metric">

                      <span>
                        AI SCORE
                      </span>

                      <strong>
                        {liveResult.chunk_score}%
                      </strong>

                    </div>


                    <div className="live-metric">

                      <span>
                        VOICE STATUS
                      </span>

                      <strong>
                        {liveResult.chunk_status}
                      </strong>

                    </div>


                    <div className="live-metric">

                      <span>
                        RISK LEVEL
                      </span>

                      <strong
                        className={
                          liveResult.risk_level === "HIGH"
                            ? "risk-high"
                            : ""
                        }
                      >
                        {liveResult.risk_level}
                      </strong>

                    </div>


                    <div className="live-action">

                      <span>
                        RECOMMENDED ACTION
                      </span>

                      <strong>
                        {liveResult.action}
                      </strong>

                    </div>

                  </div>

                )}

              </div>

            )}

          </motion.div>

        <AnimatePresence>

          {result && (

            <motion.section
              className="result-card"
              initial={{
                opacity: 0,
                y: 35,
                scale: 0.97,
              }}
              animate={{
                opacity: 1,
                y: 0,
                scale: 1,
              }}
              transition={{
                duration: 0.6,
              }}
            >

              <div className="result-header">

                <div>

                  <div className="card-label">
                    ANALYSIS COMPLETE
                  </div>

                  <h2>
                    Voice authenticity report
                  </h2>

                </div>

                <div className="result-file">
                  {result.filename}
                </div>

              </div>


              <div className="result-main">

                <div
  className="score-ring"
  style={{
    "--score-angle": `${result.ai_score * 3.6}deg`,
  }}
>

                  <div className="score-ring-inner">

                    <motion.div
                      className="score-number"
                      initial={{
                        opacity: 0,
                        scale: 0.5,
                      }}
                      animate={{
                        opacity: 1,
                        scale: 1,
                      }}
                      transition={{
                        duration: 0.7,
                        delay: 0.2,
                      }}
                    >
                      {animatedScore.toFixed(2)}%
                    </motion.div>

                    <div className="score-caption">
                      AI SCORE
                    </div>

                  </div>

                </div>


                <div className="result-status">

                  <div
                    className={`result-icon ${
                      result.prediction === "REAL"
                        ? "real"
                        : "danger"
                    }`}
                  >
                    {getResultIcon()}
                  </div>


                  <div>

                    <div className="result-prediction">
                      {result.prediction}
                    </div>

                    <div className="result-risk">
                      Risk Level: {result.risk_level}
                    </div>

                  </div>

                </div>

              </div>
              
              {/* ==================================
                  FORENSIC TIMELINE
              ================================== */}

              <div className="forensic-section">

                <div className="forensic-header">

                  <div>
                    <div className="forensic-label">
                      VOICE FORENSIC TIMELINE
                    </div>

                    <h3>
                      Chunk-level detection
                    </h3>
                  </div>

                  <div className="forensic-count">
                    {result.fake_chunks}/{result.total_chunks} AI
                  </div>

                </div>


                <div className="chunk-list">

                  {result.chunk_scores?.map((score, index) => {
  const isAI = score >= 50;

  return (
    <motion.div
      className="chunk-row"
      key={index}
      initial={{
        opacity: 0,
        x: -20,
      }}
      animate={{
        opacity: 1,
        x: 0,
      }}
      transition={{
        duration: 0.45,
        delay: index * 0.1,
        ease: "easeOut",
      }}
    >
      {/* Chunk number */}
      <div className="chunk-number">
        {String(index + 1).padStart(2, "0")}
      </div>

      {/* Detection bar */}
      <div className="chunk-track">
        <motion.div
          className={`chunk-bar ${
            isAI ? "chunk-ai" : "chunk-real"
          }`}
          initial={{
            width: 0,
          }}
          animate={{
            width: `${Math.max(score, 1)}%`,
          }}
          transition={{
            duration: 0.9,
            delay: index * 0.1 + 0.15,
            ease: "easeOut",
          }}
        />
      </div>

      {/* Score */}
      <motion.div
        className="chunk-score"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{
          delay: index * 0.1 + 0.5,
          duration: 0.3,
        }}
      >
        {score.toFixed(2)}%
      </motion.div>

      {/* Status */}
      <motion.div
        className={`chunk-status ${
          isAI ? "status-ai" : "status-real"
        }`}
        initial={{
          opacity: 0,
          scale: 0.8,
        }}
        animate={{
          opacity: 1,
          scale: 1,
        }}
        transition={{
          delay: index * 0.1 + 0.55,
          duration: 0.3,
        }}
      >
        {isAI ? "AI" : "REAL"}
      </motion.div>
    </motion.div>
  );
})}

                </div>

              </div>


              {/* ==================================
                  RESULT STATS
              ================================== */}

              <div className="result-stats">

                <div className="result-stat">

                  <div className="result-stat-value">
                    {result.fake_chunks}/
                    {result.total_chunks}
                  </div>

                  <div className="result-stat-label">
                    AI CHUNKS
                  </div>

                </div>


                <div className="result-stat">

                  <div className="result-stat-value">
                    {result.fake_chunk_percentage}%
                  </div>

                  <div className="result-stat-label">
                    SUSPICIOUS CHUNKS
                  </div>

                </div>


                <div className="result-stat">

                  <div className="result-stat-value">
                    {result.duration_seconds}s
                  </div>

                  <div className="result-stat-label">
                    AUDIO DURATION
                  </div>

                </div>


                <div className="result-stat">

                  <div className="result-stat-value">
                    {result.median_ai_score}%
                  </div>

                  <div className="result-stat-label">
                    MEDIAN SCORE
                  </div>

                </div>

              </div>


              {/* ==================================
                  ACTION
              ================================== */}

              <button
                className="reset-button"
                onClick={resetAnalysis}
              >

                <RotateCcw size={17} />

                Analyze Another Recording

              </button>

            </motion.section>

          )}

        </AnimatePresence>

        {/* ==========================================
            TRANSACTION SECURITY CONTEXT
        ========================================== */}

{result?.transaction_context && (
  <motion.div
    className="transaction-card"
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <div className="transaction-header">

      <div>
        <span className="section-eyebrow">
          SECURITY CONTEXT
        </span>

        <h3>Transaction Context</h3>
      </div>

      <span className="demo-badge">
        DEMO
      </span>

    </div>


    <div className="transaction-grid">

      <div className="transaction-item">
        <span>Caller</span>

        <strong>
          {result.transaction_context.caller_name ||
            "Unknown Caller"}
        </strong>
      </div>


      <div className="transaction-item">
        <span>Requested Action</span>

        <strong>
          {result.transaction_context.transaction_type ||
            "None"}
        </strong>
      </div>


      <div className="transaction-item">
        <span>Amount</span>

        <strong>
          ₹
          {Number(
            result.transaction_context.transaction_amount || 0
          ).toLocaleString("en-IN")}
        </strong>
      </div>


      <div className="transaction-item">
        <span>Sensitivity</span>

        <strong
          className={
            result.transaction_context
              .transaction_sensitivity === "HIGH"
              ? "risk-high"
              : ""
          }
        >
          {result.transaction_context
            .transaction_sensitivity || "LOW"}
        </strong>
      </div>


      <div className="transaction-item">
        <span>Caller Verification</span>

        <strong
          className={
            result.transaction_context.caller_verified
              ? "verification-good"
              : "risk-high"
          }
        >
          {result.transaction_context.caller_verified
            ? "VERIFIED"
            : "NOT VERIFIED"}
        </strong>
      </div>

    </div>
  </motion.div>
)}
        {/* ==========================================
              SECURITY PREVENTION ENGINE
          ========================================== */}

        {result?.risk_level === "HIGH" && (
          <motion.div
            className="security-action-card"
            initial={{
              opacity: 0,
              scale: 0.97
            }}
            animate={{
              opacity: 1,
              scale: 1
            }}
            transition={{
              duration: 0.45
            }}
          >

            <div className="security-alert-icon">
              🚨
            </div>


            <div className="security-action-content">

              <span className="section-eyebrow">
                SECURITY RESPONSE
              </span>

              <h3>
                Possible Voice Impersonation
              </h3>

              <p>
                Voice authenticity signals and transaction
                context indicate a high-risk interaction.
              </p>


              {/* Risk summary */}

              <div className="security-risk-summary">

                <div>
                  <span>RISK SCORE</span>

                  <strong>
                    {result.risk_score}
                  </strong>
                </div>


                <div>
                  <span>RISK LEVEL</span>

                  <strong className="risk-high">
                    {result.risk_level}
                  </strong>
                </div>


                <div>
                  <span>RECOMMENDED ACTION</span>

                  <strong>
                    {result.recommended_action
                      ?.replaceAll("_", " ")}
                  </strong>
                </div>

              </div>


              {/* Security actions */}

              <div className="security-actions">

                <button
                  className="security-btn danger"
                  onClick={() =>
                    alert(
                      "Transaction placed on security hold."
                    )
                  }
                >
                  HOLD TRANSACTION
                </button>


                <button
                  className="security-btn"
                  onClick={() =>
                    alert(
                      "Independent caller verification requested."
                    )
                  }
                >
                  VERIFY CALLER
                </button>


                <button
                  className="security-btn"
                  onClick={() =>
                    alert(
                      "MFA verification initiated."
                    )
                  }
                >
                  REQUEST MFA
                </button>

              </div>


              <div className="security-note">
                Prototype action layer — connected to the
                VoiceShield-AI risk engine.
              </div>

            </div>

          </motion.div>
        )}


        {/* ====================================
            FEATURES
        ==================================== */}

        {!result && (

          <motion.section
            className="features"
            initial={{
              opacity: 0,
              y: 25,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            transition={{
              duration: 0.7,
              delay: 0.3,
            }}
          >

            <div className="feature-card">

              <div className="feature-icon">
                <AudioWaveform size={21} />
              </div>

              <div>

                <h3>
                  Chunk-Level Analysis
                </h3>

                <p>
                  Speech is analyzed in focused
                  8-second segments for consistent
                  detection.
                </p>

              </div>

            </div>


            <div className="feature-card">

              <div className="feature-icon">
                <ShieldCheck size={21} />
              </div>

              <div>

                <h3>
                  Deep Learning Detection
                </h3>

                <p>
                  Wav2Vec2-based analysis identifies
                  patterns associated with synthetic speech.
                </p>

              </div>

            </div>


            <div className="feature-card">

              <div className="feature-icon">
                <LockKeyhole size={21} />
              </div>

              <div>

                <h3>
                  Privacy First
                </h3>

                <p>
                  Audio is processed by the VoiceShield-AI
                  prototype backend for analysis.
                </p>

              </div>

            </div>

          </motion.section>

        )}

        {/* ====================================
            FOOTER
        ==================================== */}

        <footer>

          <span>
            VoiceShield-AI
          </span>

          <span>
            AI Voice Deepfake Detection • Prototype
          </span>

        </footer>

      </main>

    </div>
  );
}

export default App;