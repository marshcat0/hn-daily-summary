"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { locales, localeNames, Locale } from "@/lib/i18n";

interface LanguageSwitcherProps {
  currentLocale: Locale;
}

export function LanguageSwitcher({ currentLocale }: LanguageSwitcherProps) {
  const pathname = usePathname();

  // Get the path without the locale prefix
  const getPathWithoutLocale = () => {
    const segments = pathname.split("/").filter(Boolean);
    if (locales.includes(segments[0] as Locale)) {
      segments.shift();
    }
    return "/" + segments.join("/");
  };

  const pathWithoutLocale = getPathWithoutLocale();

  return (
    <div className="flex items-center gap-1">
      {locales.map((locale) => (
        <Link
          key={locale}
          href={`/${locale}${pathWithoutLocale}`}
          className={`px-2 py-1 text-sm rounded transition-colors ${
            locale === currentLocale
              ? "bg-white/20 font-medium"
              : "hover:bg-white/10 opacity-75 hover:opacity-100"
          }`}
        >
          {localeNames[locale]}
        </Link>
      ))}
    </div>
  );
}
