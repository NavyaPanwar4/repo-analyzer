import { useState } from "react"
import client from "../api/client"
import styles from "./BugPanel.module.css"

const SEVERITY_COLOR = {
  error: "#f87171",
  warning: "#facc15",
  info: "#60a5fa",
}

const SEVERITY_LABEL = {
  error: "Error",
  warning: "Warning",
  info: "Info",
}

export default function BugPanel({ bugs, onAskAboutBug }) {
  const [explanation, setExplanation] = useState("")
  const [loadingExplain, setLoadingExplain] = useState(false)
  const [filter, setFilter] = useState("all")

  if (!bugs || bugs.total === 0) {
    return (
      <div className={styles.empty}>
        No issues detected.
      </div>
    )
  }

  const filtered = filter === "all"
    ? bugs.findings
    : bugs.findings.filter(f => f.severity === filter)

  async function handleExplain() {
    setLoadingExplain(true)
    try {
      const res = await client.post("/bugs/explain", { findings: bugs.findings })
      setExplanation(res.data.explanation)
    } catch (e) {
      setExplanation("Failed to get explanation.")
    } finally {
      setLoadingExplain(false)
    }
  }

  return (
    <div className={styles.panel}>
      <div className={styles.statsRow}>
        <div className={styles.stat} style={{ color: "#f87171" }}>
          <span className={styles.statNum}>{bugs.errors}</span>
          <span>Errors</span>
        </div>
        <div className={styles.stat} style={{ color: "#facc15" }}>
          <span className={styles.statNum}>{bugs.warnings}</span>
          <span>Warnings</span>
        </div>
        <div className={styles.stat} style={{ color: "#60a5fa" }}>
          <span className={styles.statNum}>{bugs.info}</span>
          <span>Info</span>
        </div>
        <button
          className={styles.explainBtn}
          onClick={handleExplain}
          disabled={loadingExplain}
        >
          {loadingExplain ? "Analysing..." : "AI summary"}
        </button>
      </div>

      {explanation && (
        <div className={styles.explanation}>
          <pre className={styles.explanationText}>{explanation}</pre>
        </div>
      )}

      <div className={styles.filters}>
        {["all", "error", "warning", "info"].map(f => (
          <button
            key={f}
            className={filter === f ? styles.filterActive : styles.filter}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      <div className={styles.list}>
        {filtered.map((finding, i) => (
          <div key={i} className={styles.finding}>
            <div className={styles.findingHeader}>
              <span
                className={styles.severity}
                style={{ color: SEVERITY_COLOR[finding.severity], borderColor: SEVERITY_COLOR[finding.severity] + "44" }}
              >
                {SEVERITY_LABEL[finding.severity]}
              </span>
              <span className={styles.rule}>{finding.rule}</span>
              <span className={styles.location}>
                {finding.file.split("/").pop()}:{finding.line}
              </span>
              <button
                className={styles.askBtn}
                onClick={() => onAskAboutBug(finding)}
              >
                Ask AI
              </button>
            </div>
            <p className={styles.message}>{finding.message}</p>
            {finding.snippet && (
              <pre className={styles.snippet}>{finding.snippet}</pre>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}