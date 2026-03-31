import { useEffect, useState, useCallback } from "react"
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "reactflow"
import "reactflow/dist/style.css"
import styles from "./GraphView.module.css"

function buildLayout(graphData) {
  if (!graphData?.nodes?.length) return { nodes: [], edges: [] }

  const nodeCount = graphData.nodes.length
  const cols = Math.ceil(Math.sqrt(nodeCount))
  const spacing = 220

  const nodes = graphData.nodes.map((n, i) => {
    const col = i % cols
    const row = Math.floor(i / cols)
    const filename = n.id.split("/").pop()
    const ext = filename.split(".").pop()

    return {
      id: n.id,
      position: { x: col * spacing, y: row * spacing },
      data: {
        label: filename,
        language: n.language,
        num_functions: n.num_functions,
        num_classes: n.num_classes,
        in_degree: n.in_degree,
        ext,
      },
      type: "codeNode",
    }
  })

  const edges = graphData.edges.map((e, i) => ({
    id: `e${i}`,
    source: e.source,
    target: e.target,
    label: e.label?.length > 30 ? e.label.slice(0, 30) + "…" : e.label,
    markerEnd: { type: MarkerType.ArrowClosed, color: "#7c6dfa" },
    style: { stroke: "#7c6dfa", strokeWidth: 1.5 },
    labelStyle: { fill: "#888", fontSize: 10 },
    labelBgStyle: { fill: "#1a1a1a" },
  }))

  return { nodes, edges }
}

const EXT_COLORS = {
  py: "#4ade80",
  js: "#facc15",
  jsx: "#facc15",
  ts: "#60a5fa",
  tsx: "#60a5fa",
  html: "#fb923c",
  css: "#e879f9",
  md: "#94a3b8",
  json: "#f87171",
}

function CodeNode({ data, selected }) {
  const color = EXT_COLORS[data.ext] || "#888"
  return (
    <div
      style={{
        background: selected ? "#2a2a3a" : "#1a1a1a",
        border: `1.5px solid ${selected ? "#7c6dfa" : color + "66"}`,
        borderLeft: `4px solid ${color}`,
        borderRadius: 8,
        padding: "10px 14px",
        minWidth: 160,
        fontFamily: "IBM Plex Mono, monospace",
        cursor: "pointer",
        transition: "all 0.15s",
      }}
    >
      <div style={{ fontSize: 13, fontWeight: 600, color: "#f0f0f0", marginBottom: 4 }}>
        {data.label}
      </div>
      <div style={{ fontSize: 11, color: "#888", display: "flex", gap: 10 }}>
        <span style={{ color }}>.{data.ext}</span>
        {data.num_functions > 0 && <span>{data.num_functions} fn</span>}
        {data.num_classes > 0 && <span>{data.num_classes} cls</span>}
        {data.in_degree > 0 && <span>{data.in_degree} imports</span>}
      </div>
    </div>
  )
}

const nodeTypes = { codeNode: CodeNode }

export default function GraphView({ graphData, onNodeClick }) {
  const { nodes: initialNodes, edges: initialEdges } = buildLayout(graphData)
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)
  const [selected, setSelected] = useState(null)

  useEffect(() => {
    const { nodes: n, edges: e } = buildLayout(graphData)
    setNodes(n)
    setEdges(e)
  }, [graphData])

  const handleNodeClick = useCallback((_, node) => {
    setSelected(node.id)
    onNodeClick?.(node.data)
  }, [onNodeClick])

  if (!graphData?.nodes?.length) return null

  return (
    <div className={styles.wrapper}>
      <ReactFlow
        nodes={nodes.map(n => ({ ...n, type: "codeNode", selected: n.id === selected }))}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={2}
      >
        <MiniMap
          nodeColor={n => EXT_COLORS[n.data?.ext] || "#888"}
          maskColor="rgba(0,0,0,0.6)"
          style={{ background: "#111" }}
        />
        <Controls style={{ background: "#1a1a1a", border: "1px solid #2a2a2a" }} />
        <Background color="#2a2a2a" gap={24} />
      </ReactFlow>

      <div className={styles.legend}>
        {Object.entries(EXT_COLORS).map(([ext, color]) => (
          <span key={ext} className={styles.legendItem}>
            <span style={{ background: color, width: 8, height: 8, borderRadius: 2, display: "inline-block" }} />
            .{ext}
          </span>
        ))}
      </div>
    </div>
  )
}