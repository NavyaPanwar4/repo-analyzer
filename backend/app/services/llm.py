import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.3-70b-versatile"

INTENT_KEYWORDS = {
    "bug": ["bug", "error", "issue", "wrong", "broken", "fail", "crash", "problem"],
    "architecture": ["architecture", "structure", "overview", "explain", "how does", "what does", "purpose"],
    "function": ["function", "method", "where is", "which file", "what does", "how is", "find"],
    "security": ["security", "vulnerability", "secret", "password", "auth", "injection"],
}

def _detect_intent(question: str) -> str:
    q = question.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(k in q for k in keywords):
            return intent
    return "general"


def _build_system_prompt(intent: str, summary: dict = None) -> str:
    base = """You are an expert software engineer doing a deep code review.
You have full context of the repository structure and source code.
Be specific: always mention file names, function names, and line numbers when relevant.
Format your answer clearly. Use bullet points for lists. Use code blocks for code snippets.
Never say "I don't know" — reason from the context provided."""

    if intent == "bug":
        base += "\n\nFocus on identifying root causes, not just symptoms. Suggest concrete fixes with code examples."
    elif intent == "architecture":
        base += "\n\nGive a high-level explanation first, then drill into specifics. Describe how the components interact."
    elif intent == "security":
        base += "\n\nHighlight security risks clearly with severity levels (critical/high/medium/low). Suggest mitigations."
    elif intent == "function":
        base += "\n\nPoint to the exact file and function. Show the relevant code snippet and explain what it does."

    if summary:
        base += f"\n\nRepo stats: {summary.get('total_files', '?')} files, {summary.get('total_edges', '?')} import relationships."
        if summary.get("hub_files"):
            hubs = [f.split("/")[-1] for f in summary["hub_files"][:3]]
            base += f" Most imported files: {', '.join(hubs)}."

    return base


def ask_llm(question: str, context_chunks: list, summary: dict = None) -> str:
    intent = _detect_intent(question)
    system_prompt = _build_system_prompt(intent, summary)

    sorted_chunks = sorted(context_chunks, key=lambda c: c.get("score", 0), reverse=True)

    context_parts = []
    for c in sorted_chunks:
        meta = c["metadata"]
        filename = meta["file"].split("/")[-1]
        chunk_type = meta.get("type", "code")
        line_info = f" (line {meta['start_line']})" if meta.get("start_line") else ""
        header = f"### {filename} — {chunk_type}{line_info}"
        context_parts.append(f"{header}\n```{meta.get('language', '')}\n{c['text']}\n```")

    context = "\n\n".join(context_parts)

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Here is relevant code from the repository:\n\n{context}\n\n---\n\nQuestion: {question}",
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=1500,
    )
    return response.choices[0].message.content


def summarise_bugs(findings: list) -> str:
    """Ask the LLM to explain the bug findings in plain English."""
    if not findings:
        return "No issues found."

    findings_text = "\n".join(
        f"- [{f['severity'].upper()}] {f['file'].split('/')[-1]} line {f['line']}: {f['message']}\n  Code: `{f['snippet']}`"
        for f in findings[:30] 
    )

    messages = [
        {
            "role": "system",
            "content": "You are a senior code reviewer. Summarise the following static analysis findings clearly and concisely. Group by severity. Suggest which issues to fix first.",
        },
        {
            "role": "user",
            "content": f"Static analysis findings:\n\n{findings_text}\n\nProvide a clear summary with priorities.",
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=1000,
    )
    return response.choices[0].message.content