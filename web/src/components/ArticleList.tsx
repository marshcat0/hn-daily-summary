import { ArticleCard } from "./ArticleCard";
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
}

interface ArticleListProps {
  articles: Article[];
  title?: string;
  locale?: Locale;
}

export function ArticleList({
  articles,
  title,
  locale = defaultLocale,
}: ArticleListProps) {
  const t = getTranslations(locale);

  if (articles.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        <p>{t.noArticles}</p>
      </div>
    );
  }

  return (
    <section>
      {title && (
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <span>📋</span>
          {title}
          <span className="text-sm font-normal text-gray-500">
            ({articles.length})
          </span>
        </h2>
      )}

      <div className="space-y-3">
        {articles.map((article, index) => (
          <ArticleCard
            key={article.id}
            article={article}
            index={index}
            locale={locale}
          />
        ))}
      </div>
    </section>
  );
}
