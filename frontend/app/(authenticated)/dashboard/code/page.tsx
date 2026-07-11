"use client";

import dynamic from "next/dynamic";

// Monaco doesn't support server-side rendering.
const CodeEditor = dynamic(() => import("@/components/CodeEditor"), { ssr: false });

export default function CodeEditorPage() {
  return <CodeEditor />;
}
