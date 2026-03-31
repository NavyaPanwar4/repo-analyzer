import { useState, useRef, useEffect } from "react"
import { useParams, useLocation, useNavigate } from "react-router-dom"
import client from "../api/client"
import ChatMessage from "../components/ChatMessage"
import GraphView from "../components/GraphView"
import BugPanel from "../components/BugPanel"
import styles from "./Chat.module.css"

export default function Chat() {
  const { repoId } = useParams()
  const { state } = useLocation()
  const navigate = useNavigate()
  const summary = state?.summary
  const graphData = state?.graph
  const bugs = state?.bugs

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: `Repo loaded. ${summary ? `Found ${summary.total_files} files and ${summary.total_edges} relationships.` : ""} ${bugs?.total ? `Detected ${bugs.errors} errors and ${bugs.warnings} warnings.` : ""} Ask me anything about this codebase.`,
    },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState("chat")
  const [selectedNode, setSelectedNode] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput("")
    setMessages(prev => [...prev, { role: "user", text: question }])
    setLoading(true)

    try {
      const res = await client.post("/ask", {
        repo_id: repoId,
        question,
        summary,
      })
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          text: res.data.answer,
          chunks: res.data.context_chunks,
        },
      ])
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          text: "Error: " + (err.response?.data?.detail || "Something went wrong"),
          isError: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleNodeClick(nodeData) {
    setSelectedNode(nodeData)
    setActiveTab("chat")
    setInput(`Tell me about the file ${nodeData.label}`)
  }

  function handleAskAboutBug(finding) {
    setActiveTab("chat")
    setInput(`Explain this issue and how to fix it: [${finding.rule}] in ${finding.file.split("/").pop()} line ${finding.line}: ${finding.message}`)
  }

  const suggestions = [
    "What does this project do?",
    "Where is the main entry point?",
    "What are the most important files?",
    "Are there any potential bugs?",
  ]

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <button className={styles.back} onClick={() => navigate("/")}>← Back</button>
        <div className={styles.tabs}>
          <button
            className={activeTab === "chat" ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab("chat")}
          >
            Chat
          </button>
          <button
            className={activeTab === "graph" ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab("graph")}
          >
            Graph
            {graphData?.nodes?.length > 0 && (
              <span className={styles.badge}>{graphData.nodes.length}</span>
            )}
          </button>
          <button
            className={activeTab === "bugs" ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab("bugs")}
          >
            Bugs
            {bugs?.errors > 0 && (
              <span className={styles.badgeRed}>{bugs.errors}</span>
            )}
            {bugs?.warnings > 0 && !bugs?.errors && (
              <span className={styles.badgeYellow}>{bugs.warnings}</span>
            )}
          </button>
        </div>
        <div className={styles.repoTag}>repo: {repoId}</div>
      </header>

      {activeTab === "chat" && (
        <div className={styles.chatPane}>
          {selectedNode && (
            <div className={styles.nodeCtx}>
              Asking about: <span>{selectedNode.label}</span>
              <button onClick={() => setSelectedNode(null)}>×</button>
            </div>
          )}

          <div className={styles.messages}>
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} />
            ))}
            {loading && (
              <div className={styles.thinking}>
                <span /><span /><span />
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {messages.length === 1 && (
            <div className={styles.suggestions}>
              {suggestions.map(s => (
                <button key={s} className={styles.suggestion} onClick={() => setInput(s)}>
                  {s}
                </button>
              ))}
            </div>
          )}

          <form className={styles.inputRow} onSubmit={handleSend}>
            <input
              className={styles.input}
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask about this codebase..."
              disabled={loading}
            />
            <button className={styles.send} type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      )}

      {activeTab === "graph" && (
        <div className={styles.graphPane}>
          <GraphView graphData={graphData} onNodeClick={handleNodeClick} />
        </div>
      )}

      {activeTab === "bugs" && (
        <div className={styles.bugsPane}>
          <BugPanel bugs={bugs} onAskAboutBug={handleAskAboutBug} />
        </div>
      )}
    </div>
  )
}