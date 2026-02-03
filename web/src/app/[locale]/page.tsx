import { notFound } from "next/navigation";
import { Header, TopicNav, SummarySection, ArticleList } from "@/components";
import { getLatestDate, getAllTopicsData, getTopicsForDate } from "@/lib/data";
import { getTranslations, isValidLocale, locales, Locale } from "@/lib/i18n";

interface HomePageProps {
  params: Promise<{
    locale: string;
  }>;
}

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function HomePage({ params }: HomePageProps) {
  const { locale } = await params;

  if (!isValidLocale(locale)) {
    return notFound();
  }

  const t = getTranslations(locale as Locale);
  const latestDate = getLatestDate();

  if (!latestDate) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            {locale === "zh" ? "暂无数据" : "No Data Available"}
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            {locale === "zh"
              ? "运行爬虫以生成每日摘要。"
              : "Run the crawler to generate daily summaries."}
          </p>
        </div>
      </div>
    );
  }

  const topics = getTopicsForDate(latestDate);
  const allTopicsData = getAllTopicsData(latestDate);

  return (
    <div className="min-h-screen">
      <Header currentDate={latestDate} locale={locale as Locale} />
      <TopicNav topics={topics} locale={locale as Locale} />

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t.todaySummary}
          </h1>
          <p className="text-gray-500 dark:text-gray-400">{t.aiCuratedNews}</p>
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

              {topicData.description && (
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {topicData.description}
                </p>
              )}

              <div className="space-y-6">
                <SummarySection
                  summary={topicData.summary}
                  topicName={topicData.topic_name}
                  locale={locale as Locale}
                />

                <ArticleList
                  articles={topicData.articles}
                  title={`${topicData.topic_name} ${t.allArticles}`}
                  locale={locale as Locale}
                />
              </div>
            </section>
          ))}
        </div>

        {allTopicsData.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">
              {latestDate}{" "}
              {locale === "zh" ? "暂无主题数据" : "No topic data available"}
            </p>
          </div>
        )}
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
