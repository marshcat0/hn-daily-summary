import { formatDistanceToNow } from "date-fns";
import { zhCN } from "date-fns/locale";
import { getTranslations, Locale, defaultLocale } from "@/lib/i18n";

interface ArticleCardProps {
  article: {
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
  };
  index: number;
  locale?: Locale;
}

export function ArticleCard({
  article,
  index,
  locale = defaultLocale,
}: ArticleCardProps) {
  const t = getTranslations(locale);
  const publishedDate = new Date(article.published_at);

  // Use Chinese locale for date formatting when locale is zh
  const dateLocale = locale === "zh" ? { locale: zhCN } : {};
  const timeAgo = formatDistanceToNow(publishedDate, {
    addSuffix: true,
    ...dateLocale,
  });

  return (
    <article className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        {/* Rank number */}
        <span className="text-2xl font-bold text-gray-300 dark:text-gray-600 w-8 text-right shrink-0">
          {index + 1}
        </span>

        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">
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
          </h3>

          {/* URL domain */}
          {article.url && (
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
              {new URL(article.url).hostname.replace("www.", "")}
            </p>
          )}

          {/* Summary (if available) */}
          {article.summary && (
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
              {article.summary}
            </p>
          )}

          {/* Metadata row */}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-gray-500 dark:text-gray-400">
            {/* Source badge */}
            <span className="inline-flex items-center px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
              {article.source}
            </span>

            {/* Score */}
            {article.score > 0 && (
              <span className="flex items-center">
                <span className="text-hn-orange mr-1">▲</span>
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
                💬 {article.comments_count} {t.comments}
              </a>
            )}

            {/* Author */}
            <span>
              {t.by} {article.author}
            </span>

            {/* Time */}
            <span>{timeAgo}</span>
          </div>
        </div>
      </div>
    </article>
  );
}
