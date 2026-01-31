"use client";

import { useState } from "react";

interface Change {
  type: "spelling" | "grammar" | "punctuation";
  original: string;
  replacement: string;
}

interface CorrectionResponse {
  corrected: string;
  variant: "uk" | "us";
  changes: Change[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function TextCorrector() {
  const [text, setText] = useState("");
  const [variant, setVariant] = useState<"uk" | "us">("uk");
  const [result, setResult] = useState<CorrectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [keepFormatting, setKeepFormatting] = useState(true);

  const handleCorrect = async () => {
    setError(null);
    setResult(null);
    setCopied(false);

    const trimmed = text.trim();
    if (!trimmed) {
      setError("Please enter some text to correct.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/correct`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: keepFormatting ? text : text.replace(/\n+/g, " "),
          variant,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(
          body?.detail?.[0]?.msg ?? body?.detail ?? `Server error ${res.status}`
        );
      }

      const data: CorrectionResponse = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message ?? "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result) return;
    await navigator.clipboard.writeText(result.corrected);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const badgeColor = (type: string) => {
    switch (type) {
      case "spelling":
        return "bg-blue-100 text-blue-800";
      case "grammar":
        return "bg-amber-100 text-amber-800";
      case "punctuation":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="space-y-6">
      {/* Input */}
      <div>
        <label
          htmlFor="input-text"
          className="mb-1 block text-sm font-medium text-gray-700"
        >
          Input text
        </label>
        <textarea
          id="input-text"
          rows={6}
          className="w-full rounded-lg border border-gray-300 p-3 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          placeholder="Type or paste your text here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        <div>
          <label
            htmlFor="variant"
            className="mb-1 block text-sm font-medium text-gray-700"
          >
            English variant
          </label>
          <select
            id="variant"
            value={variant}
            onChange={(e) => setVariant(e.target.value as "uk" | "us")}
            className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="uk">British (UK)</option>
            <option value="us">American (US)</option>
          </select>
        </div>

        <label className="flex items-center gap-2 text-sm text-gray-600 pt-5">
          <input
            type="checkbox"
            checked={keepFormatting}
            onChange={(e) => setKeepFormatting(e.target.checked)}
            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          Keep original formatting
        </label>

        <div className="pt-5">
          <button
            onClick={handleCorrect}
            disabled={loading}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 disabled:opacity-50"
          >
            {loading ? "Correcting..." : "Correct text"}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <>
          <div>
            <div className="mb-1 flex items-center justify-between">
              <label className="block text-sm font-medium text-gray-700">
                Corrected text
              </label>
              <button
                onClick={handleCopy}
                className="rounded-md border border-gray-300 bg-white px-3 py-1 text-xs font-medium text-gray-600 hover:bg-gray-50"
              >
                {copied ? "Copied!" : "Copy to clipboard"}
              </button>
            </div>
            <div className="w-full whitespace-pre-wrap rounded-lg border border-gray-300 bg-white p-3 text-base shadow-sm">
              {result.corrected}
            </div>
          </div>

          {/* Changes panel */}
          {result.changes.length > 0 && (
            <div>
              <h3 className="mb-2 text-sm font-medium text-gray-700">
                Changes ({result.changes.length})
              </h3>
              <div className="divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
                {result.changes.map((c, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 px-3 py-2 text-sm"
                  >
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${badgeColor(
                        c.type
                      )}`}
                    >
                      {c.type}
                    </span>
                    <span className="text-red-600 line-through">
                      {c.original}
                    </span>
                    <span className="text-gray-400">&rarr;</span>
                    <span className="font-medium text-green-700">
                      {c.replacement}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.changes.length === 0 && (
            <p className="text-sm text-gray-500">
              No changes needed &mdash; your text looks good!
            </p>
          )}
        </>
      )}
    </div>
  );
}
