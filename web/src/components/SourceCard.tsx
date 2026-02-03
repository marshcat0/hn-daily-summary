"use client";

import { useState } from "react";
import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import { getTranslations, Locale, defaultLocale } from "@/lib/i18n";

interface Article {
  id: string;
  title: string;
  url: string | null;
  source: string;
  score: number;
  comments_count: number;
  comments_url: string | null;
  published_at: string;
  author: string;
  summary?: string;
}

interface SourceCardProps {
  sourceName: string;
  articles: Article[];
  locale?: Locale;
}

// Source icons/colors mapping
const sourceStyles: Record<string, { icon: string; color: string }> = {
  "Hacker News": { icon: "🔶", color: "bg-orange-100 dark:bg-orange-900/30 border-orange-200 dark:border-orange-800" },
  "r/LocalLLaMA": { icon: "🤖", color: "bg-purple-100 dark:bg-purple-900/30 border-purple-200 dark:border-purple-800" },
  "r/MachineLearning": { icon: "🧠", color: "bg-blue-100 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800" },
  "r/programming": { icon: "💻", color: "bg-green-100 dark:bg-green-900/30 border-green-200 dark:border-green-800" },
  "r/webdev": { icon: "🌐", color: "bg-cyan-100 dark:bg-cyan-900/30 border-cyan-200 dark:border-cyan-800" },
  "r/design": { icon: "🎨", color: "bg-pink-100 dark:bg-pink-900/30 border-pink-200 dark:border-pink-800" },
};

const defaultStyle = { icon: "📰", color: "bg-gray-100 dark:bg-gray-800 border-gray-200 dark:border-gray-700" };

export function SourceCard({
  sourceName,
  articles,
  locale = defaultLocale,
}: SourceCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const t = getTranslations(locale);
  const style = sourceStyles[sourceName] || defaultStyle;

  return (
    <div className={`rounded-lg border overflow-hidden ${style.color}`}>
      {/* Header - clickable to collapse/expand */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-xl">{style.icon}</span>
          <h3 className="font-semibold text-gray-900 dark:text-white">
            {sourceName}
          </h3>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            ({articles.length})
          </span>
        </div>
        <span className="text-gray-400 text-sm">{isExpanded ? "▼" : "▶"}</span>
      </button>

      {/* Articles list */}
      {isExpanded && (
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {articles.map((article) => (
            <SourceArticleItem
              key={article.id}
              article={article}
              locale={locale}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface SourceArticleItemProps {
  article: Article;
  locale: Locale;
}

function SourceArticleItem({ article, locale }: SourceArticleItemProps) {
  const t = getTranslations(locale);
  const publishedDate = new Date(article.published_at);
  const dateLocale = locale === "zh" ? { locale: zhCN } : {};
  const timeAgo = formatDistanceToNow(publishedDate, {
    addSuffix: true,
    ...dateLocale,
  });

  return (
    <article className="px-4 py-3 bg-white/50 dark:bg-gray-800/50 hover:bg-white dark:hover:bg-gray-800 transition-colors">
      {/* Title */}
      <h4 className="font-medium text-gray-900 dark:text-white leading-snug">
        {article.url ? (
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-hn-orange transition-colors"
          >
            {article.title}
          </a>
        ) : (
          article.title
        )}
      </h4>

      {/* Summary (if available) */}
      {article.summary && (
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
          {article.summary}
        </p>
      )}

      {/* Metadata row */}
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-2 text-xs text-gray-500 dark:text-gray-400">
        {/* Score */}
        {article.score > 0 && (
          <span className="flex items-center">
            <span className="text-hn-orange mr-0.5">▲</span>
            {article.score}
          </span>
        )}

        {/* Comments */}
        {article.comments_url && (
          <a
            href={article.comments_url}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-hn-orange transition-colors"
          >
            💬 {article.comments_count}
          </a>
        )}

        {/* Author */}
        <span>
          {t.by} {article.author}
        </span>

        {/* Time */}
        <span>{timeAgo}</span>
      </div>
    </article>
  );
}
