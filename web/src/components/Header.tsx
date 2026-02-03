"use client";

import Link from "next/link";
import { getTranslations, Locale, defaultLocale } from "@/lib/i18n";
import { LanguageSwitcher } from "./LanguageSwitcher";

interface HeaderProps {
  currentDate?: string;
  locale?: Locale;
}

export function Header({ currentDate, locale = defaultLocale }: HeaderProps) {
  const t = getTranslations(locale);

  return (
    <header className="bg-hn-orange text-white shadow-md">
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href={`/${locale}`} className="flex items-center space-x-3">
            <span className="text-2xl">📰</span>
            <div>
              <h1 className="text-xl font-bold">{t.siteName}</h1>
              <p className="text-sm opacity-90">{t.siteDescription}</p>
            </div>
          </Link>

          <div className="flex items-center gap-4">
            <LanguageSwitcher currentLocale={locale} />

            {currentDate && (
              <div className="text-right border-l border-white/30 pl-4">
                <p className="text-sm opacity-75">{t.latest}</p>
                <p className="font-mono">{currentDate}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
