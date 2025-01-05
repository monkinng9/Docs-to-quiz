import asyncio
import nest_asyncio
from crawl4ai import AsyncWebCrawler, CacheMode, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def clean_content():
    async with AsyncWebCrawler(verbose=True) as crawler:
        config = CrawlerRunConfig(
            cache_mode=CacheMode.ENABLED,
            excluded_tags=['nav', 'footer', 'aside'],
            remove_overlay_elements=True,
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0),
                options={
                    "ignore_links": True
                }
            ),
        )
        result = await crawler.arun(
            url="https://docs.crewai.com/concepts/flows",
            config=config,
        )
        full_markdown_length = len(result.markdown_v2.raw_markdown)
        fit_markdown_length = len(result.markdown_v2.fit_markdown)
        print(f"Full Markdown Length: {full_markdown_length}")
        print(f"Fit Markdown Length: {fit_markdown_length}")

        # Print the clean Fit Markdown content directly
        # Write the clean Fit Markdown content to a file
        with open('clean_content.md', 'w', encoding='utf-8') as f:
            f.write(result.markdown_v2.fit_markdown)
        print(f"Clean content written to clean_content.md")



asyncio.run(clean_content())