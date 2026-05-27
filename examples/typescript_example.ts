/** Example: Instrumenting a TypeScript agent with Beacon. */
import { trace } from 'beacon-agent';

const summarizeArticle = trace('article-summarizer', 'http://localhost:8000')(
  async (url: string): Promise<string> => {
    await new Promise((r) => setTimeout(r, 800 + Math.random() * 1000));
    if (Math.random() < 0.15) {
      throw new Error('Rate limit exceeded');
    }
    return `Summary of ${url}`;
  }
);

async function main() {
  const urls = [
    'https://example.com/article-1',
    'https://example.com/article-2',
    'https://example.com/article-3',
  ];
  for (const url of urls) {
    try {
      const result = await summarizeArticle(url);
      console.log(`  ${url} -> ${result}`);
    } catch (e) {
      console.log(`  ${url} -> ERROR: ${e}`);
    }
  }
  console.log('\nDone. Check http://localhost:3000 for traces.');
}

main();
