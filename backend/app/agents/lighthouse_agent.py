"""
Lighthouse Agent for performance testing
Uses Chrome DevTools Protocol via Playwright
"""
import asyncio
import json
from typing import Dict, Any
from playwright.async_api import async_playwright
import tempfile
from pathlib import Path


class LighthouseAgent:
    """Agent for running Lighthouse performance tests"""

    def __init__(self):
        self.metrics_to_extract = [
            'first-contentful-paint',
            'largest-contentful-paint',
            'total-blocking-time',
            'cumulative-layout-shift',
            'speed-index',
            'interactive',
            'performance-score'
        ]

    async def analyze(self, url: str) -> Dict[str, Any]:
        """
        Run Lighthouse analysis on the given URL

        Args:
            url: The URL to analyze

        Returns:
            Dictionary containing Lighthouse metrics and scores
        """
        print(f"[LIGHTHOUSE] Running Lighthouse analysis for {url}")

        try:
            async with async_playwright() as p:
                # Launch browser with specific settings for performance testing
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage'
                    ]
                )

                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )

                page = await context.new_page()

                # Collect performance metrics
                metrics = await self._collect_metrics(page, url)

                await browser.close()

                return {
                    'success': True,
                    'url': url,
                    'metrics': metrics,
                    'scores': self._calculate_scores(metrics),
                    'suggestions': self._generate_suggestions(metrics)
                }

        except Exception as e:
            print(f"[ERROR] Lighthouse error for {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'metrics': {},
                'scores': {},
                'suggestions': []
            }

    async def _collect_metrics(self, page, url: str) -> Dict[str, Any]:
        """Collect performance metrics using Playwright"""

        # Navigate and wait for load
        # Using 'domcontentloaded' instead of 'networkidle' for better reliability on cloud
        # Increased timeout to 90s for slower cloud infrastructure
        response = await page.goto(url, wait_until='domcontentloaded', timeout=90000)

        # Wait for additional content to load
        await asyncio.sleep(3)

        # Wait a bit more to ensure all metrics are collected
        await asyncio.sleep(2)

        # Get Web Vitals using JavaScript
        metrics_js = await page.evaluate("""
            () => {
                return new Promise((resolve) => {
                    let metrics = {};

                    // FCP - First Contentful Paint
                    const fcpEntry = performance.getEntriesByName('first-contentful-paint')[0];
                    if (fcpEntry) {
                        metrics.fcp = fcpEntry.startTime;
                    }

                    // LCP - Largest Contentful Paint
                    new PerformanceObserver((list) => {
                        const entries = list.getEntries();
                        const lastEntry = entries[entries.length - 1];
                        metrics.lcp = lastEntry.startTime;
                    }).observe({type: 'largest-contentful-paint', buffered: true});

                    // CLS - Cumulative Layout Shift
                    let clsValue = 0;
                    new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            if (!entry.hadRecentInput) {
                                clsValue += entry.value;
                            }
                        }
                        metrics.cls = clsValue;
                    }).observe({type: 'layout-shift', buffered: true});

                    // FID would require user interaction, so we'll skip it

                    // Navigation Timing
                    const navTiming = performance.getEntriesByType('navigation')[0];
                    if (navTiming) {
                        metrics.domContentLoaded = navTiming.domContentLoadedEventEnd - navTiming.domContentLoadedEventStart;
                        metrics.loadComplete = navTiming.loadEventEnd - navTiming.loadEventStart;
                        metrics.ttfb = navTiming.responseStart - navTiming.requestStart;
                        metrics.domInteractive = navTiming.domInteractive - navTiming.fetchStart;
                    }

                    // Resource timing
                    const resources = performance.getEntriesByType('resource');
                    metrics.resourceCount = resources.length;
                    metrics.totalResourceSize = resources.reduce((acc, r) => acc + (r.transferSize || 0), 0);

                    setTimeout(() => resolve(metrics), 3000);
                });
            }
        """)

        # Get additional page info
        page_info = await page.evaluate("""
            () => ({
                title: document.title,
                url: window.location.href,
                images: document.querySelectorAll('img').length,
                scripts: document.querySelectorAll('script').length,
                stylesheets: document.querySelectorAll('link[rel="stylesheet"]').length
            })
        """)

        return {
            'fcp': metrics_js.get('fcp', 0),
            'lcp': metrics_js.get('lcp', 0),
            'cls': metrics_js.get('cls', 0),
            'ttfb': metrics_js.get('ttfb', 0),
            'domContentLoaded': metrics_js.get('domContentLoaded', 0),
            'loadComplete': metrics_js.get('loadComplete', 0),
            'domInteractive': metrics_js.get('domInteractive', 0),
            'resourceCount': metrics_js.get('resourceCount', 0),
            'totalResourceSize': metrics_js.get('totalResourceSize', 0),
            'pageInfo': page_info,
            'statusCode': response.status if response else None
        }

    def _calculate_scores(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate performance scores based on metrics"""

        scores = {}

        # FCP Score (0-100)
        fcp = metrics.get('fcp', 0)
        if fcp < 1800:
            scores['fcp_score'] = 100
        elif fcp < 3000:
            scores['fcp_score'] = 100 - ((fcp - 1800) / 1200 * 50)
        else:
            scores['fcp_score'] = max(0, 50 - ((fcp - 3000) / 3000 * 50))

        # LCP Score (0-100)
        lcp = metrics.get('lcp', 0)
        if lcp < 2500:
            scores['lcp_score'] = 100
        elif lcp < 4000:
            scores['lcp_score'] = 100 - ((lcp - 2500) / 1500 * 50)
        else:
            scores['lcp_score'] = max(0, 50 - ((lcp - 4000) / 4000 * 50))

        # CLS Score (0-100)
        cls = metrics.get('cls', 0)
        if cls < 0.1:
            scores['cls_score'] = 100
        elif cls < 0.25:
            scores['cls_score'] = 100 - ((cls - 0.1) / 0.15 * 50)
        else:
            scores['cls_score'] = max(0, 50 - ((cls - 0.25) / 0.25 * 50))

        # TTFB Score (0-100)
        ttfb = metrics.get('ttfb', 0)
        if ttfb < 800:
            scores['ttfb_score'] = 100
        elif ttfb < 1800:
            scores['ttfb_score'] = 100 - ((ttfb - 800) / 1000 * 50)
        else:
            scores['ttfb_score'] = max(0, 50 - ((ttfb - 1800) / 1800 * 50))

        # Overall Performance Score
        scores['performance_score'] = sum([
            scores.get('fcp_score', 0) * 0.1,
            scores.get('lcp_score', 0) * 0.25,
            scores.get('cls_score', 0) * 0.15,
            scores.get('ttfb_score', 0) * 0.1,
            50 * 0.4  # Placeholder for other metrics
        ])

        return scores

    def _generate_suggestions(self, metrics: Dict[str, Any]) -> list:
        """Generate performance improvement suggestions"""

        suggestions = []

        # FCP suggestions
        fcp = metrics.get('fcp', 0)
        if fcp > 3000:
            suggestions.append({
                'metric': 'FCP',
                'severity': 'high',
                'suggestion': 'First Contentful Paint is slow. Consider reducing server response times, eliminating render-blocking resources, and optimizing critical rendering path.'
            })
        elif fcp > 1800:
            suggestions.append({
                'metric': 'FCP',
                'severity': 'medium',
                'suggestion': 'First Contentful Paint could be improved. Look into preloading critical assets and reducing JavaScript execution time.'
            })

        # LCP suggestions
        lcp = metrics.get('lcp', 0)
        if lcp > 4000:
            suggestions.append({
                'metric': 'LCP',
                'severity': 'high',
                'suggestion': 'Largest Contentful Paint is poor. Optimize your largest content element, use CDN for images, implement lazy loading, and consider using modern image formats like WebP.'
            })
        elif lcp > 2500:
            suggestions.append({
                'metric': 'LCP',
                'severity': 'medium',
                'suggestion': 'Largest Contentful Paint needs optimization. Consider image optimization and faster server response times.'
            })

        # CLS suggestions
        cls = metrics.get('cls', 0)
        if cls > 0.25:
            suggestions.append({
                'metric': 'CLS',
                'severity': 'high',
                'suggestion': 'High Cumulative Layout Shift detected. Set explicit dimensions for images and embeds, avoid inserting content above existing content, and use CSS transforms for animations.'
            })
        elif cls > 0.1:
            suggestions.append({
                'metric': 'CLS',
                'severity': 'medium',
                'suggestion': 'Cumulative Layout Shift could be better. Ensure all images and iframes have explicit width and height attributes.'
            })

        # TTFB suggestions
        ttfb = metrics.get('ttfb', 0)
        if ttfb > 1800:
            suggestions.append({
                'metric': 'TTFB',
                'severity': 'high',
                'suggestion': 'Time to First Byte is very slow. Optimize server performance, use CDN, implement caching strategies, and consider upgrading hosting.'
            })
        elif ttfb > 800:
            suggestions.append({
                'metric': 'TTFB',
                'severity': 'medium',
                'suggestion': 'Time to First Byte could be improved with better caching and CDN usage.'
            })

        # Resource size suggestions
        total_size = metrics.get('totalResourceSize', 0)
        if total_size > 3000000:  # 3MB
            suggestions.append({
                'metric': 'Resource Size',
                'severity': 'medium',
                'suggestion': f'Total resource size is {total_size / 1000000:.2f}MB. Consider code splitting, lazy loading, and asset optimization.'
            })

        return suggestions
