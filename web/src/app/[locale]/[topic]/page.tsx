import { notFound } from "next/navigation";
import { Header, TopicNav, SummarySection, SourceCard } from "@/components";
import {
  getLatestDate,
  getTopicData,
  getTopicsForDate,
  getAllTopicIds,
} from "@/lib/data";
import { getTranslations, isValidLocale, locales, Locale } from "@/lib/i18n";

// Helper function to group articles by source
function groupArticlesBySource(articles: any[]) {
  const groups: Record<string, any[]> = {};
  
  for (const article of articles) {
    const source = article.source || "Other";
    if (!groups[source]) {
      groups[source] = [];
    }
    groups[source].push(article);
  }
  
  // Sort groups by total score (sum of article scores in each group)
  const sortedEntries = Object.entries(groups).sort(([, a], [, b]) => {
    const scoreA = a.reduce((sum, article) => sum + (article.score || 0), 0);
    const scoreB = b.reduce((sum, article) => sum + (article.score || 0), 0);
    return scoreB - scoreA;
  });
  
  return sortedEntries;
}

interface TopicPageProps {
  params: Promise<{
    locale: string;
    topic: string;
  }>;
}

// Generate static paths for all locale + topic combinations
export function generateStaticParams() {
  const topicIds = getAllTopicIds();
  const paths: { locale: string; topic: string }[] = [];

  for (const locale of locales) {
    for (const topic of topicIds) {
      paths.push({ locale, topic });
    }
  }

  return paths;
}

export default async function TopicPage({ params }: TopicPageProps) {
  const { locale, topic: topicId } = await params;

  if (!isValidLocale(locale)) {
    return notFound();
  }

  const t = getTranslations(locale as Locale);
  const latestDate = getLatestDate();

  if (!latestDate) {
    return notFound();
  }

  const topicData = getTopicData(latestDate, topicId);

  if (!topicData) {
    return notFound();
  }

  const allTopics = getTopicsForDate(latestDate);

  return (
    <div className="min-h-screen">
      <Header currentDate={latestDate} locale={locale as Locale} />
      <TopicNav
        topics={allTopics}
        currentTopicId={topicId}
        locale={locale as Locale}
      />

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {topicData.topic_name}
          </h1>
          {topicData.description && (
            <p className="text-gray-500 dark:text-gray-400">
              {topicData.description}
            </p>
          )}
          <p className="text-sm text-gray-400 mt-2">
            {topicData.article_count} {t.articles} • {latestDate}
          </p>
        </div>

        <div className="space-y-8">
          {/* Topic-level AI Summary */}
          <SummarySection
            summary={topicData.summary}
            topicName={topicData.topic_name}
            locale={locale as Locale}
          />

          {/* Articles grouped by source - responsive grid */}
          <section>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <span>📰</span>
              {t.allArticles}
              <span className="text-sm font-normal text-gray-500">
                ({topicData.article_count})
              </span>
            </h2>
            
            {/* Responsive grid: 1 column on mobile, 2 columns on desktop */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {groupArticlesBySource(topicData.articles).map(([sourceName, articles]) => (
                <SourceCard
                  key={sourceName}
                  sourceName={sourceName}
                  articles={articles}
                  locale={locale as Locale}
                />
              ))}
            </div>
          </section>
        </div>
      </main>

      <footer className="border-t border-gray-200 dark:border-gray-700 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>
            {t.generatedBy}{" "}
            <a
              href="https://github.com/marshcat0/hn-daily-summary"
              className="text-hn-orange hover:underline"
            >
              {t.projectName}
            </a>{" "}
            • {t.poweredBy}
          </p>
        </div>
      </footer>
    </div>
  );
}
