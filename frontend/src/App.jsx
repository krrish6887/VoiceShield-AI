import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShieldCheck,
  Mic,
  MicOff,
  Upload,
  ArrowRight,
  Activity,
  Lock,
  Fingerprint,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Sparkles,
  Radio,
  ScanLine,
  Clock3,
  CircleDollarSign,
  UserCheck,
  KeyRound,
  Ban,
} from "lucide-react";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // -----------------------------
  // FILE ANALYSIS
  // -----------------------------
  const [selectedFile, setSelectedFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // -----------------------------
  // TRANSACTION CONTEXT
  // -----------------------------
  const [callerName, setCallerName] = useState("Rahul Sharma");
  const [transactionType, setTransactionType] =
    useState("Fund Transfer");
  const [transactionAmount, setTransactionAmount] =
    useState("250000");
  const [transactionSensitivity, setTransactionSensitivity] =
    useState("HIGH");
  const [callerVerified, setCallerVerified] =
    useState(false);

  // -----------------------------
  // LIVE ANALYSIS
  // -----------------------------
  const [liveMode, setLiveMode] = useState(false);
  const [liveAnalyzing, setLiveAnalyzing] = useState(false);
  const [liveResult, setLiveResult] = useState(null);
  const [liveChunks, setLiveChunks] = useState([]);

  const mediaRecorderRef = useRef(null);
  const liveStreamRef = useRef(null);
  const liveTimerRef = useRef(null);
  const liveActiveRef = useRef(false);

  // -----------------------------
  // AUDIT EVENTS
  // -----------------------------
  const [auditEvents, setAuditEvents] = useState([]);

  const addAuditEvent = (title, description, type = "normal") => {
    setAuditEvents((previous) => [
      ...previous,
      {
        id: Date.now() + Math.random(),
        time: new Date().toLocaleTimeString(),
        title,
        description,
        type,
      },
    ]);
  };

  // -----------------------------
  // CLEANUP
  // -----------------------------
  useEffect(() => {
    return () => {
      liveActiveRef.current = false;

      if (liveTimerRef.current) {
        clearTimeout(liveTimerRef.current);
      }

      if (mediaRecorderRef.current?.state === "recording") {
        mediaRecorderRef.current.stop();
      }

      if (liveStreamRef.current) {
        liveStreamRef.current
          .getTracks()
          .forEach((track) => track.stop());
      }
    };
  }, []);

  // ============================================================
  // NORMAL AUDIO ANALYSIS
  // ============================================================

  const analyzeAudio = async () => {
    if (!selectedFile) {
      setError("Please select an audio file first.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setAnalysis(null);

      addAuditEvent(
        "VOICE ANALYSIS STARTED",
        `Analyzing ${selectedFile.name}`,
        "normal"
      );

      const formData = new FormData();

      formData.append("file", selectedFile);
      formData.append(
        "transaction_sensitivity",
        transactionSensitivity
      );
      formData.append(
        "transaction_type",
        transactionType
      );
      formData.append(
        "transaction_amount",
        transactionAmount
      );
      formData.append(
        "caller_verified",
        String(callerVerified)
      );
      formData.append(
        "caller_name",
        callerName
      );

      const response = await fetch(
        `${API_URL}/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(
          `Analysis failed: HTTP ${response.status}`
        );
      }

      const data = await response.json();

      setAnalysis(data);

      addAuditEvent(
        "VOICE ANALYSIS COMPLETE",
        `${data.ai_score}% AI likelihood detected`,
        data.risk_level === "HIGH"
          ? "danger"
          : data.risk_level === "MEDIUM"
          ? "warning"
          : "success"
      );

      if (data.risk_level === "HIGH") {
        addAuditEvent(
          "HIGH SECURITY RISK DETECTED",
          data.recommended_action,
          "danger"
        );

        addAuditEvent(
          "TRANSACTION PROTECTION ACTIVATED",
          "Verification required before authorization",
          "danger"
        );
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "Audio analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // LIVE MICROPHONE
  // ============================================================

  const analyzeLiveChunk = async (audioBlob) => {
    try {
      console.log(
        "🚀 Sending live chunk to backend...",
        audioBlob.size,
        "bytes"
      );

      const formData = new FormData();

      formData.append(
        "file",
        audioBlob,
        "live_chunk.webm"
      );

      formData.append(
        "transaction_sensitivity",
        transactionSensitivity
      );

      formData.append(
        "caller_verified",
        String(callerVerified)
      );

      const response = await fetch(
        `${API_URL}/analyze-chunk`,
        {
          method: "POST",
          body: formData,
        }
      );

      console.log(
        "📥 Backend response:",
        response.status
      );

      if (!response.ok) {
        throw new Error(
          `Live analysis failed: HTTP ${response.status}`
        );
      }

      const data = await response.json();

      console.log("✅ LIVE RESULT:", data);

      if (data.error) {
        throw new Error(data.error);
      }

      setLiveResult(data);

      setLiveChunks((previousChunks) => [
        ...previousChunks,
        {
          ...data,
          chunk_number:
            previousChunks.length + 1,
          timestamp:
            new Date().toLocaleTimeString(),
        },
      ].slice(-12));

      addAuditEvent(
        `LIVE CHUNK ${
          liveChunks.length + 1
        } ANALYZED`,
        `AI likelihood: ${data.chunk_score}%`,
        data.risk_level === "HIGH"
          ? "danger"
          : data.risk_level === "MEDIUM"
          ? "warning"
          : "success"
      );

      if (data.risk_level === "HIGH") {
        addAuditEvent(
          "HIGH-RISK VOICE PATTERN",
          "Protection response recommended",
          "danger"
        );
      }

      return data;
    } catch (err) {
      console.error(
        "❌ Live chunk analysis error:",
        err
      );

      setError(
        `Live analysis error: ${err.message}`
      );

      return null;
    }
  };

  const startLiveAnalysis = async () => {
    try {
      setError("");

      console.log(
        "🎙 Starting live microphone..."
      );

      const stream =
        await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

      console.log(
        "✅ Microphone permission granted"
      );

      liveStreamRef.current = stream;
      liveActiveRef.current = true;

      const mimeType =
        MediaRecorder.isTypeSupported(
          "audio/webm;codecs=opus"
        )
          ? "audio/webm;codecs=opus"
          : "audio/webm";

      setLiveMode(true);
      setLiveAnalyzing(true);
      setLiveResult(null);
      setLiveChunks([]);

      addAuditEvent(
        "CALL RECEIVED",
        "Microphone stream initialized",
        "normal"
      );

      addAuditEvent(
        "REAL-TIME MONITORING ACTIVE",
        "Voice authenticity monitoring started",
        "normal"
      );

      const recordNextChunk = () => {
        if (!liveActiveRef.current) {
          return;
        }

        console.log(
          "🔴 Starting new 8-second recording..."
        );

        const recorder = new MediaRecorder(
          stream,
          {
            mimeType,
          }
        );

        mediaRecorderRef.current = recorder;

        const audioChunks = [];

        recorder.ondataavailable = (event) => {
          if (
            event.data &&
            event.data.size > 0
          ) {
            audioChunks.push(event.data);
          }
        };

        recorder.onstop = async () => {
          console.log(
            "🛑 8-second recording stopped"
          );

          if (!audioChunks.length) {
            console.warn(
              "⚠️ No audio data received"
            );
            return;
          }

          const audioBlob = new Blob(
            audioChunks,
            {
              type: mimeType,
            }
          );

          console.log(
            "🎧 Complete audio chunk created:",
            audioBlob.size,
            "bytes"
          );

          await analyzeLiveChunk(audioBlob);

          if (liveActiveRef.current) {
            setTimeout(() => {
              recordNextChunk();
            }, 200);
          }
        };

        recorder.onerror = (event) => {
          console.error(
            "❌ MediaRecorder error:",
            event
          );
        };

        recorder.start();

        liveTimerRef.current =
          setTimeout(() => {
            if (
              recorder.state === "recording" &&
              liveActiveRef.current
            ) {
              recorder.stop();
            }
          }, 8000);
      };

      recordNextChunk();
    } catch (err) {
      console.error(err);

      setError(
        "Unable to access microphone. Please allow microphone permission."
      );

      setLiveMode(false);
      setLiveAnalyzing(false);
    }
  };

  const stopLiveAnalysis = () => {
    console.log(
      "🛑 Stopping live analysis..."
    );

    liveActiveRef.current = false;

    if (liveTimerRef.current) {
      clearTimeout(liveTimerRef.current);
      liveTimerRef.current = null;
    }

    const recorder =
      mediaRecorderRef.current;

    if (
      recorder &&
      recorder.state === "recording"
    ) {
      recorder.stop();
    }

    if (liveStreamRef.current) {
      liveStreamRef.current
        .getTracks()
        .forEach((track) => track.stop());

      liveStreamRef.current = null;
    }

    mediaRecorderRef.current = null;

    setLiveMode(false);
    setLiveAnalyzing(false);

    addAuditEvent(
      "LIVE MONITORING STOPPED",
      "Voice stream closed",
      "normal"
    );
  };

  // ============================================================
  // UI HELPERS
  // ============================================================

  const currentResult =
    liveResult || analysis;

  const score =
    currentResult?.chunk_score ??
    currentResult?.ai_score ??
    0;

  const riskLevel =
    currentResult?.risk_level ||
    "LOW";

  const isHighRisk =
    riskLevel === "HIGH";

  const isMediumRisk =
    riskLevel === "MEDIUM";

  const status =
    currentResult?.chunk_status ||
    currentResult?.prediction ||
    "WAITING";

  const riskClass = isHighRisk
    ? "danger"
    : isMediumRisk
    ? "warning"
    : "success";

  return (
    <div className="kwach-app">

      {/* ===================================================== */}
      {/* NAVBAR */}
      {/* ===================================================== */}

      <nav className="kwach-nav">

        <div className="brand">
          <div className="brand-mark">
            <ShieldCheck size={20} />
          </div>

          <span>KWACH</span>
        </div>

        <div className="nav-links">
          <a href="#product">
            Product
          </a>

          <a href="#detection">
            Detection
          </a>

          <a href="#protection">
            Protection
          </a>

          <a href="#technology">
            Technology
          </a>
        </div>

        <button
          className="nav-launch"
          onClick={() =>
            document
              .getElementById("console")
              ?.scrollIntoView({
                behavior: "smooth",
              })
          }
        >
          Launch Console
          <ArrowRight size={15} />
        </button>
      </nav>

      {/* ===================================================== */}
      {/* ERROR */}
      {/* ===================================================== */}

      <AnimatePresence>
        {error && (
          <motion.div
            className="error-banner"
            initial={{
              opacity: 0,
              y: -15,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            exit={{
              opacity: 0,
              y: -15,
            }}
          >
            <XCircle size={18} />
            <span>{error}</span>

            <button
              onClick={() => setError("")}
            >
              ×
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ===================================================== */}
      {/* HERO */}
      {/* ===================================================== */}

      <section
        id="product"
        className="hero-section"
      >

        <div className="hero-content">

          <div className="eyebrow">
            <Sparkles size={13} />
            AI VOICE SECURITY
          </div>

          <h1>
            Know the voice.
            <br />
            <em>Trust the conversation.</em>
          </h1>

          <p className="hero-description">
            KWACH analyzes voice signals in real
            time to identify possible AI
            impersonation and trigger adaptive
            security responses.
          </p>

          <div className="hero-actions">

            <button
              className="primary-button"
              onClick={() =>
                document
                  .getElementById("console")
                  ?.scrollIntoView({
                    behavior: "smooth",
                  })
              }
            >
              Open Security Console
              <ArrowRight size={17} />
            </button>

            <button
              className="secondary-button"
              onClick={startLiveAnalysis}
            >
              <Mic size={17} />
              Try Live Analysis
            </button>

          </div>

          <div className="hero-trust">

            <span>
              <CheckCircle2 size={14} />
              Real-time analysis
            </span>

            <span>
              <CheckCircle2 size={14} />
              Chunk-level forensics
            </span>

            <span>
              <CheckCircle2 size={14} />
              Context-aware protection
            </span>

          </div>

        </div>

        {/* AI ORB */}

        <motion.div
          className="hero-orb-container"
          animate={{
            y: [0, -12, 0],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >

          <div className="orb-ring ring-one" />
          <div className="orb-ring ring-two" />
          <div className="orb-ring ring-three" />

          <motion.div
            className="ai-orb"
            animate={{
              scale: [
                1,
                1.04,
                1,
              ],
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
            }}
          >
            <div className="orb-core">
              <ShieldCheck size={38} />
            </div>
          </motion.div>

          <div className="orb-label">
            <span>KWACH</span>
            <small>
              VOICE INTELLIGENCE ENGINE
            </small>
          </div>

        </motion.div>

      </section>

      {/* ===================================================== */}
      {/* FEATURE STRIP */}
      {/* ===================================================== */}

      <section
        id="detection"
        className="section"
      >

        <div className="section-heading">

          <div className="eyebrow">
            WHAT KWACH DOES
          </div>

          <h2>
            Voice security,
            <br />
            built for real conversations.
          </h2>

        </div>

        <div className="feature-grid">

          <FeatureCard
            icon={<Radio size={20} />}
            title="Live Voice Guard"
            text="Analyze microphone audio continuously while a conversation is happening."
          />

          <FeatureCard
            icon={<ScanLine size={20} />}
            title="Voice Forensics"
            text="Break conversations into focused audio windows for consistent analysis."
          />

          <FeatureCard
            icon={<ShieldAlert size={20} />}
            title="Adaptive Protection"
            text="Combine voice signals with security context to determine the appropriate response."
          />

        </div>

      </section>

      {/* ===================================================== */}
      {/* LIVE SECURITY CONSOLE */}
      {/* ===================================================== */}

      <section
        id="console"
        className="console-section"
      >

        <div className="console-header">

          <div>
            <div className="eyebrow">
              SECURITY CONSOLE
            </div>

            <h2>
              Live Voice Guard
            </h2>

            <p>
              Monitor voice authenticity as the
              conversation unfolds.
            </p>
          </div>

          <div className="online-pill">
            <span />
            SYSTEM ONLINE
          </div>

        </div>

        <div className="console-grid">

          {/* MAIN LIVE CARD */}

          <div className="live-card">

            <div className="live-card-top">

              <div className="live-label">
                <Activity size={15} />
                REAL-TIME ANALYSIS
              </div>

              <div
                className={
                  liveMode
                    ? "status-pill active"
                    : "status-pill"
                }
              >
                <span />
                {liveMode
                  ? "LISTENING"
                  : "READY"}
              </div>

            </div>

            <div className="console-orb-wrapper">

              <motion.div
                className={
                  liveMode
                    ? "console-orb listening"
                    : "console-orb"
                }
                animate={
                  liveMode
                    ? {
                        scale: [
                          1,
                          1.06,
                          1,
                        ],
                      }
                    : {}
                }
                transition={{
                  duration: 2,
                  repeat: Infinity,
                }}
              >

                <div>
                  {liveMode ? (
                    <Mic size={32} />
                  ) : (
                    <ShieldCheck size={32} />
                  )}
                </div>

              </motion.div>

              <div className="orb-status">
                {liveMode
                  ? "LISTENING TO VOICE"
                  : "READY FOR ANALYSIS"}
              </div>

            </div>

            <div className="live-score">

              <span>
                VOICE AUTHENTICITY
              </span>

              <strong>
                {currentResult
                  ? `${Number(score).toFixed(2)}%`
                  : "—"}
              </strong>

              <div className="score-line">
                <motion.div
                  animate={{
                    width: `${Math.min(
                      Number(score) || 0,
                      100
                    )}%`,
                  }}
                />
              </div>

              <div className="score-caption">
                {status}
              </div>

            </div>

            <div className="live-controls">

              {!liveMode ? (
                <button
                  className="primary-button wide"
                  onClick={
                    startLiveAnalysis
                  }
                >
                  <Mic size={17} />
                  Start Live Analysis
                </button>
              ) : (
                <button
                  className="danger-button wide"
                  onClick={
                    stopLiveAnalysis
                  }
                >
                  <MicOff size={17} />
                  Stop Live Analysis
                </button>
              )}

            </div>

          </div>

          {/* LIVE RESULT */}

          <div className="result-card">

            <div className="card-eyebrow">
              CURRENT SECURITY STATE
            </div>

            <div
              className={`state-icon ${riskClass}`}
            >
              {isHighRisk ? (
                <ShieldAlert />
              ) : isMediumRisk ? (
                <AlertTriangle />
              ) : (
                <CheckCircle2 />
              )}
            </div>

            <h3>
              {currentResult
                ? status
                : "Waiting for voice"}
            </h3>

            <p>
              {currentResult
                ? isHighRisk
                  ? "Possible AI voice impersonation detected."
                  : isMediumRisk
                  ? "Voice authenticity requires additional verification."
                  : "Voice currently appears authentic."
                : "Start live analysis or upload a recording to begin."}
            </p>

            <div className="result-metrics">

              <Metric
                label="AI SCORE"
                value={
                  currentResult
                    ? `${Number(score).toFixed(2)}%`
                    : "—"
                }
              />

              <Metric
                label="RISK"
                value={
                  currentResult
                    ? riskLevel
                    : "—"
                }
              />

              <Metric
                label="CHUNKS"
                value={
                  liveChunks.length ||
                  analysis?.total_chunks ||
                  "—"
                }
              />

            </div>

          </div>

        </div>

        {/* ================================================= */}
        {/* LIVE FORENSICS */}
        {/* ================================================= */}

        <div className="forensics-card">

          <div className="forensics-header">

            <div>
              <div className="eyebrow">
                VOICE FORENSICS
              </div>

              <h3>
                Voice Signal Timeline
              </h3>
            </div>

            <div className="chunk-count">
              {liveChunks.length} CHUNKS
            </div>

          </div>

          {liveChunks.length === 0 ? (
            <div className="empty-state">
              <Activity size={22} />
              <span>
                Start live analysis to populate
                the forensic timeline.
              </span>
            </div>
          ) : (
            <div className="chunk-list">

              {liveChunks.map(
                (chunk) => {

                  const chunkAI =
                    chunk.chunk_status ===
                    "AI";

                  const chunkSuspicious =
                    chunk.chunk_status ===
                    "SUSPICIOUS";

                  return (
                    <motion.div
                      className="chunk-row"
                      key={chunk.chunk_number}
                      initial={{
                        opacity: 0,
                        y: 8,
                      }}
                      animate={{
                        opacity: 1,
                        y: 0,
                      }}
                    >

                      <div className="chunk-number">
                        {String(
                          chunk.chunk_number
                        ).padStart(2, "0")}
                      </div>

                      <div className="chunk-time">
                        {chunk.timestamp}
                      </div>

                      <div className="chunk-bar">
                        <motion.div
                          className={
                            chunkAI
                              ? "ai"
                              : chunkSuspicious
                              ? "suspicious"
                              : "real"
                          }
                          initial={{
                            width: 0,
                          }}
                          animate={{
                            width: `${Math.max(
                              Number(
                                chunk.chunk_score
                              ),
                              1
                            )}%`,
                          }}
                        />
                      </div>

                      <strong>
                        {chunk.chunk_score}%
                      </strong>

                      <span
                        className={
                          chunkAI
                            ? "chunk-status ai"
                            : chunkSuspicious
                            ? "chunk-status suspicious"
                            : "chunk-status real"
                        }
                      >
                        {chunk.chunk_status}
                      </span>

                      <span className="chunk-risk">
                        {chunk.risk_level}
                      </span>

                    </motion.div>
                  );
                }
              )}

            </div>
          )}

        </div>

      </section>

      {/* ===================================================== */}
      {/* UPLOAD ANALYSIS */}
      {/* ===================================================== */}

      <section className="section upload-section">

        <div className="section-heading centered">

          <div className="eyebrow">
            FORENSIC ANALYSIS
          </div>

          <h2>
            Analyze a recording.
          </h2>

          <p>
            Upload an audio file and let KWACH
            perform chunk-level voice analysis.
          </p>

        </div>

        <div className="upload-card">

          <div className="upload-icon">
            <Upload size={25} />
          </div>

          <h3>
            {selectedFile
              ? selectedFile.name
              : "Choose an audio recording"}
          </h3>

          <p>
            WAV, MP3 and browser-recorded
            audio supported by the prototype.
          </p>

          <label className="file-button">
            <Upload size={15} />
            Select Audio

            <input
              type="file"
              accept="audio/*"
              onChange={(event) => {
                const file =
                  event.target.files?.[0];

                setSelectedFile(file || null);
                setError("");
              }}
            />
          </label>

          <button
            className="primary-button"
            disabled={
              !selectedFile || loading
            }
            onClick={analyzeAudio}
          >
            {loading
              ? "Analyzing..."
              : "Analyze Recording"}

            {!loading && (
              <ArrowRight size={16} />
            )}
          </button>

        </div>

      </section>

      {/* ===================================================== */}
      {/* SECURITY CONTEXT */}
      {/* ===================================================== */}

      <section
        id="protection"
        className="section"
      >

        <div className="section-heading">

          <div className="eyebrow">
            SECURITY CONTEXT
          </div>

          <h2>
            Detection becomes
            <br />
            protection.
          </h2>

          <p>
            Voice authenticity is only one part of
            the decision. KWACH combines the signal
            with caller and transaction context.
          </p>

        </div>

        <div className="context-grid">

          <div className="context-card">

            <div className="context-icon">
              <UserCheck />
            </div>

            <span>
              CALLER
            </span>

            <strong>
              {callerName}
            </strong>

            <button
              className={
                callerVerified
                  ? "verification verified"
                  : "verification"
              }
              onClick={() =>
                setCallerVerified(
                  !callerVerified
                )
              }
            >
              {callerVerified
                ? "✓ VERIFIED"
                : "MARK VERIFIED"}
            </button>

          </div>

          <div className="context-card">

            <div className="context-icon">
              <CircleDollarSign />
            </div>

            <span>
              TRANSACTION
            </span>

            <strong>
              {transactionType}
            </strong>

            <small>
              ₹
              {Number(
                transactionAmount
              ).toLocaleString("en-IN")}
            </small>

          </div>

          <div className="context-card">

            <div className="context-icon">
              <ShieldAlert />
            </div>

            <span>
              SENSITIVITY
            </span>

            <strong>
              {transactionSensitivity}
            </strong>

            <small>
              Transaction risk context
            </small>

          </div>

        </div>

      </section>

      {/* ===================================================== */}
      {/* PROTECTION RESPONSE */}
      {/* ===================================================== */}

      <section className="protection-section">

        <div className="protection-content">

          <div className="eyebrow">
            ADAPTIVE SECURITY
          </div>

          <h2>
            When the voice becomes
            <br />
            suspicious, KWACH responds.
          </h2>

          <p>
            The prototype translates detection
            signals into an adaptive security
            response instead of simply displaying
            a classification.
          </p>

          <div className="protection-actions">

            <button
              onClick={() =>
                addAuditEvent(
                  "TRANSACTION HOLD",
                  "Demo security action activated",
                  "danger"
                )
              }
            >
              <Ban size={16} />
              Hold Transaction
            </button>

            <button
              onClick={() =>
                addAuditEvent(
                  "CALLER VERIFICATION",
                  "Additional verification requested",
                  "warning"
                )
              }
            >
              <UserCheck size={16} />
              Verify Caller
            </button>

            <button
              onClick={() =>
                addAuditEvent(
                  "MFA REQUEST",
                  "Additional authentication requested",
                  "warning"
                )
              }
            >
              <KeyRound size={16} />
              Request MFA
            </button>

          </div>

        </div>

        <div className="protection-visual">

          <div className="protection-orb">
            <ShieldAlert size={35} />
          </div>

          <div className="protection-line">
            <span />
            RISK FUSION
            <span />
          </div>

          <div className="protection-flow">

            <div>VOICE</div>
            <ArrowRight />
            <div>CONTEXT</div>
            <ArrowRight />
            <div>PROTECT</div>

          </div>

        </div>

      </section>

      {/* ===================================================== */}
      {/* AUDIT TIMELINE */}
      {/* ===================================================== */}

      <section className="section">

        <div className="section-heading">

          <div className="eyebrow">
            AUDIT TRAIL
          </div>

          <h2>
            Every security decision,
            <br />
            visible.
          </h2>

        </div>

        <div className="audit-card">

          {auditEvents.length === 0 ? (
            <div className="empty-audit">
              <Clock3 size={20} />
              Security events will appear here
              during analysis.
            </div>
          ) : (
            auditEvents
              .slice()
              .reverse()
              .map((event) => (
                <motion.div
                  className="audit-row"
                  key={event.id}
                  initial={{
                    opacity: 0,
                    x: -10,
                  }}
                  animate={{
                    opacity: 1,
                    x: 0,
                  }}
                >

                  <div
                    className={`audit-dot ${event.type}`}
                  />

                  <div className="audit-time">
                    {event.time}
                  </div>

                  <div>
                    <strong>
                      {event.title}
                    </strong>

                    <p>
                      {event.description}
                    </p>
                  </div>

                </motion.div>
              ))
          )}

        </div>

      </section>

      {/* ===================================================== */}
      {/* TECHNOLOGY */}
      {/* ===================================================== */}

      <section
        id="technology"
        className="technology-section"
      >

        <div className="section-heading centered">

          <div className="eyebrow">
            TECHNOLOGY
          </div>

          <h2>
            Built for real-time
            <br />
            voice security.
          </h2>

        </div>

        <div className="tech-grid">

          <TechCard
            title="Wav2Vec2"
            text="Deep-learning speech representation used for voice authenticity analysis."
          />

          <TechCard
            title="8-Second Forensics"
            text="Continuous chunk-level analysis makes live monitoring practical."
          />

          <TechCard
            title="Risk Fusion Engine"
            text="Combines voice signals, transaction sensitivity and verification context."
          />

          <TechCard
            title="FastAPI + React"
            text="Real-time inference backend connected to an interactive security console."
          />

        </div>

      </section>

      {/* ===================================================== */}
      {/* FOOTER */}
      {/* ===================================================== */}

      <footer className="kwach-footer">

        <div className="brand">

          <div className="brand-mark">
            <ShieldCheck size={19} />
          </div>

          <span>
            KWACH
          </span>

        </div>

        <p>
          Know the voice. Trust the conversation.
        </p>

        <span className="footer-note">
          AI Voice Security Prototype
        </span>

      </footer>

    </div>
  );
}

// ============================================================
// COMPONENTS
// ============================================================

function FeatureCard({
  icon,
  title,
  text,
}) {
  return (
    <motion.div
      className="feature-card"
      whileHover={{
        y: -5,
      }}
    >
      <div className="feature-icon">
        {icon}
      </div>

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>

      <ArrowRight
        className="feature-arrow"
        size={17}
      />
    </motion.div>
  );
}

function Metric({
  label,
  value,
}) {
  return (
    <div className="metric">
      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>
    </div>
  );
}

function TechCard({
  title,
  text,
}) {
  return (
    <motion.div
      className="tech-card"
      whileHover={{
        y: -4,
      }}
    >
      <div className="tech-dot" />

      <h3>
        {title}
      </h3>

      <p>
        {text}
      </p>
    </motion.div>
  );
}

export default App;