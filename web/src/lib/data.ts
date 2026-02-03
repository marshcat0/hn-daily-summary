/**
 * Data loading utilities for static site generation.
 * 
 * Reads topic JSON files from the data directory at build time.
 */

import fs from 'fs';
import path from 'path';

export interface Article {
  id: string;
  title: string;
  url: string | null;
  source: string;
  score: number;
  comments_count: number;
  comments_url: string | null;
  published_at: string;
  author: string;
  text?: string | null;
}

export interface TopicData {
  topic_id: string;
  topic_name: string;
  description: string;
  date: string;
  crawled_at: string;
  article_count: number;
  articles: Article[];
  summary: string | null;
  summary_language?: string;
}

export interface TopicMeta {
  id: string;
  name: string;
  description: string;
  article_count: number;
}

const DATA_DIR = path.join(process.cwd(), '..', 'data');

/**
 * Get list of available dates (directories in data/)
 */
export function getAvailableDates(): string[] {
  try {
    if (!fs.existsSync(DATA_DIR)) {
      return [];
    }

    const entries = fs.readdirSync(DATA_DIR, { withFileTypes: true });
    const dates = entries
      .filter(e => e.isDirectory() && /^\d{4}-\d{2}-\d{2}$/.test(e.name))
      .map(e => e.name)
      .sort((a, b) => b.localeCompare(a)); // Newest first

    return dates;
  } catch {
    return [];
  }
}

/**
 * Get the latest date with data
 */
export function getLatestDate(): string | null {
  const dates = getAvailableDates();
  return dates[0] || null;
}

/**
 * Get list of topics for a specific date
 */
export function getTopicsForDate(date: string): TopicMeta[] {
  const dateDir = path.join(DATA_DIR, date);

  try {
    if (!fs.existsSync(dateDir)) {
      return [];
    }

    const files = fs.readdirSync(dateDir).filter(f => f.endsWith('.json'));
    const topics: TopicMeta[] = [];

    for (const file of files) {
      const filePath = path.join(dateDir, file);
      const content = fs.readFileSync(filePath, 'utf-8');
      const data: TopicData = JSON.parse(content);

      topics.push({
        id: data.topic_id,
        name: data.topic_name,
        description: data.description,
        article_count: data.article_count,
      });
    }

    return topics;
  } catch {
    return [];
  }
}

/**
 * Get topic data for a specific date and topic
 */
export function getTopicData(date: string, topicId: string): TopicData | null {
  const filePath = path.join(DATA_DIR, date, `${topicId}.json`);

  try {
    if (!fs.existsSync(filePath)) {
      return null;
    }

    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content);
  } catch {
    return null;
  }
}

/**
 * Get all topic data for a specific date
 */
export function getAllTopicsData(date: string): TopicData[] {
  const topics = getTopicsForDate(date);
  const result: TopicData[] = [];

  for (const topic of topics) {
    const data = getTopicData(date, topic.id);
    if (data) {
      result.push(data);
    }
  }

  return result;
}

/**
 * Get all topic IDs across all dates (for static path generation)
 */
export function getAllTopicIds(): string[] {
  const dates = getAvailableDates();
  const topicIds = new Set<string>();

  for (const date of dates) {
    const topics = getTopicsForDate(date);
    for (const topic of topics) {
      topicIds.add(topic.id);
    }
  }

  return Array.from(topicIds);
}
