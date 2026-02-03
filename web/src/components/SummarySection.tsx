"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { getTranslations, Locale, defaultLocale } from "@/lib/i18n";

interface SummarySectionProps {
  summary: string | null;
  topicName: string;
  locale?: Locale;
}

export function SummarySection({
  summary,
  topicName,
  locale = defaultLocale,
}: SummarySectionProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const t = getTranslations(locale);

  if (!summary) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
        <p className="text-yellow-800 dark:text-yellow-200">
          {t.summaryNotAvailable}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-2xl">🤖</span>
          <div className="text-left">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {t.aiSummary}
            </h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {topicName} - {t.poweredBy}
            </p>
          </div>
        </div>

        <span className="text-gray-400 text-xl">{isExpanded ? "▼" : "▶"}</span>
      </button>

      {/* Content */}
      {isExpanded && (
        <div className="px-6 py-4 markdown-content prose dark:prose-invert max-w-none">
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
      )}
    </div>
  );
}
