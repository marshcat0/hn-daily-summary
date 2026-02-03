import { notFound } from "next/navigation";
import { Header, TopicNav, SummarySection, ArticleList } from "@/components";
import {
  getLatestDate,
  getTopicData,
  getTopicsForDate,
  getAllTopicIds,
} from "@/lib/data";
import { getTranslations, isValidLocale, locales, Locale } from "@/lib/i18n";

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
          <SummarySection
            summary={topicData.summary}
            topicName={topicData.topic_name}
            locale={locale as Locale}
          />

          <ArticleList
            articles={topicData.articles}
            title={t.allArticles}
            locale={locale as Locale}
          />
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
