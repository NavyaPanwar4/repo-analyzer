import { useState } from "react"
import { useNavigate } from "react-router-dom"
import client from "../api/client"
import styles from "./Home.module.css"

export default function Home() {
  const [tab, setTab] = useState("url")
  const [url, setUrl] = useState("")
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [status, setStatus] = useState("")
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      let res
      if (tab === "url") {
        setStatus("Cloning repo...")
        res = await client.post("/ingest/url", { url })
      } else {
        setStatus("Uploading ZIP...")
        const form = new FormData()
        form.append("file", file)
        res = await client.post("/ingest/zip", form)
      }
      setStatus(`Indexed ${res.data.chunks_stored} chunks. Redirecting...`)
      setTimeout(() => navigate(`/chat/${res.data.repo_id}`, {
        state: {
          summary: res.data.summary,
          graph: res.data.graph,
          bugs: res.data.bugs,
        }
      }), 800)
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <div className={styles.badge}>AI Code Explorer</div>
        <h1 className={styles.title}>Understand any<br /><span>codebase instantly</span></h1>
        <p className={styles.sub}>Drop in a GitHub repo. Ask questions like a senior dev.</p>
      </div>

      <div className={styles.card}>
        <div className={styles.tabs}>
          <button className={tab === "url" ? styles.active : ""} onClick={() => setTab("url")}>GitHub URL</button>
          <button className={tab === "zip" ? styles.active : ""} onClick={() => setTab("zip")}>Upload ZIP</button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {tab === "url" ? (
            <input
              className={styles.input}
              type="text"
              placeholder="https://github.com/user/repo"
              value={url}
              onChange={e => setUrl(e.target.value)}
              required
            />
          ) : (
            <label className={styles.fileLabel}>
              <input type="file" accept=".zip" onChange={e => setFile(e.target.files[0])} required />
              {file ? file.name : "Click to select a ZIP file"}
            </label>
          )}

          <button className={styles.btn} type="submit" disabled={loading}>
            {loading ? status || "Processing..." : "Analyze Repo"}
          </button>
        </form>

        {error && <p className={styles.error}>{error}</p>}
      </div>
    </div>
  )
}