"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { getTranslations, Locale, defaultLocale } from "@/lib/i18n";

interface TopicNavProps {
  topics: {
    id: string;
    name: string;
    article_count: number;
  }[];
  currentTopicId?: string;
  locale?: Locale;
}

export function TopicNav({
  topics,
  currentTopicId,
  locale = defaultLocale,
}: TopicNavProps) {
  const pathname = usePathname();
  const t = getTranslations(locale);

  // Check if we're on the home page for this locale
  const isHome = pathname === `/${locale}` || pathname === `/${locale}/`;

  return (
    <nav className="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center space-x-1 overflow-x-auto py-2">
          <Link
            href={`/${locale}`}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              isHome && !currentTopicId
                ? "bg-hn-orange text-white"
                : "text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
            }`}
          >
            {t.allTopics}
          </Link>

          {topics.map((topic) => (
            <Link
              key={topic.id}
              href={`/${locale}/${topic.id}`}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                currentTopicId === topic.id
                  ? "bg-hn-orange text-white"
                  : "text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
              }`}
            >
              {topic.name}
              <span className="ml-2 text-xs opacity-75">
                ({topic.article_count})
              </span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}
