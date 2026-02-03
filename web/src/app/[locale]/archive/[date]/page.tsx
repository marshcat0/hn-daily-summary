import { notFound } from "next/navigation";
import Link from "next/link";
import { Header, TopicNav, SummarySection, SourceCard } from "@/components";
import {
  getAvailableDates,
  getAllTopicsData,
  getTopicsForDate,
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
  
  // Sort groups by total score
  const sortedEntries = Object.entries(groups).sort(([, a], [, b]) => {
    const scoreA = a.reduce((sum, article) => sum + (article.score || 0), 0);
    const scoreB = b.reduce((sum, article) => sum + (article.score || 0), 0);
    return scoreB - scoreA;
  });
  
  return sortedEntries;
}

interface ArchivePageProps {
  params: Promise<{
    locale: string;
    date: string;
  }>;
}

// Generate static paths for all locale + date combinations
export function generateStaticParams() {
  const dates = getAvailableDates();
  const paths: { locale: string; date: string }[] = [];

  for (const locale of locales) {
    for (const date of dates) {
      paths.push({ locale, date });
    }
  }

  return paths;
}

export default async function ArchivePage({ params }: ArchivePageProps) {
  const { locale, date } = await params;

  if (!isValidLocale(locale)) {
    return notFound();
  }

  const t = getTranslations(locale as Locale);
  const topics = getTopicsForDate(date);

  if (topics.length === 0) {
    return notFound();
  }

  const allTopicsData = getAllTopicsData(date);
  const availableDates = getAvailableDates();

  return (
    <div className="min-h-screen">
      <Header currentDate={date} locale={locale as Locale} />
      <TopicNav topics={topics} locale={locale as Locale} />

      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Archive navigation */}
        <div className="mb-8 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
            {t.archive}
          </h2>
          <div className="flex flex-wrap gap-2">
            {availableDates.map((d) => (
              <Link
                key={d}
                href={`/${locale}/archive/${d}`}
                className={`px-3 py-1 rounded text-sm ${
                  d === date
                    ? "bg-hn-orange text-white"
                    : "bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600"
                }`}
              >
                {d}
              </Link>
            ))}
          </div>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t.archive}: {date}
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            {t.historicalSummaries}
          </p>
        </div>

        {/* Show all topics */}
        <div className="space-y-12">
          {allTopicsData.map((topicData) => (
            <section key={topicData.topic_id} id={topicData.topic_id}>
              <div className="flex items-center gap-3 mb-6">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {topicData.topic_name}
                </h2>
                <span className="text-sm text-gray-500 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                  {topicData.article_count} {t.articles}
                </span>
              </div>

              <div className="space-y-6">
                <SummarySection
                  summary={topicData.summary}
                  topicName={topicData.topic_name}
                  locale={locale as Locale}
                />

                {/* Articles grouped by source */}
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
              </div>
            </section>
          ))}
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
