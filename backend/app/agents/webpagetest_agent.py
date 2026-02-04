"""
WebPageTest Agent for comprehensive performance testing
Uses WebPageTest API
"""
import asyncio
import httpx
from typing import Dict, Any
from app.config import settings


class WebPageTestAgent:
    """Agent for running WebPageTest performance analysis"""

    def __init__(self):
        self.api_key = settings.webpagetest_api_key
        self.base_url = "https://www.webpagetest.org"

    async def analyze(self, url: str) -> Dict[str, Any]:
        """
        Run WebPageTest analysis on the given URL

        Args:
            url: The URL to analyze

        Returns:
            Dictionary containing WebPageTest metrics
        """
        print(f"🌐 Running WebPageTest analysis for {url}")

        if not self.api_key:
            print("⚠️  WebPageTest API key not configured, using fallback mode")
            return self._fallback_analysis(url)

        try:
            # Submit test
            test_id = await self._submit_test(url)

            # Poll for results (with timeout)
            results = await self._wait_for_results(test_id, max_wait=180)

            return {
                'success': True,
                'url': url,
                'test_id': test_id,
                'metrics': results.get('metrics', {}),
                'scores': results.get('scores', {}),
                'waterfall': results.get('waterfall', {}),
                'suggestions': self._generate_suggestions(results.get('metrics', {}))
            }

        except Exception as e:
            print(f"❌ WebPageTest error for {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'metrics': {},
                'scores': {},
                'suggestions': []
            }

    async def _submit_test(self, url: str) -> str:
        """Submit a test to WebPageTest API"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/runtest.php",
                params={
                    'url': url,
                    'k': self.api_key,
                    'f': 'json',
                    'location': 'Dulles:Chrome',
                    'runs': 1,
                    'fvonly': 1,  # First view only
                    'lighthouse': 1,  # Include Lighthouse
                }
            )

            response.raise_for_status()
            data = response.json()

            if data.get('statusCode') != 200:
                raise Exception(f"Test submission failed: {data.get('statusText')}")

            return data['data']['testId']

    async def _wait_for_results(self, test_id: str, max_wait: int = 180) -> Dict[str, Any]:
        """Poll for test results with timeout"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            for _ in range(max_wait // 5):  # Check every 5 seconds
                await asyncio.sleep(5)

                response = await client.get(
                    f"{self.base_url}/jsonResult.php",
                    params={
                        'test': test_id,
                        'k': self.api_key
                    }
                )

                response.raise_for_status()
                data = response.json()

                status_code = data.get('statusCode')

                if status_code == 200:
                    # Test complete
                    return self._parse_results(data)
                elif status_code >= 400:
                    raise Exception(f"Test failed: {data.get('statusText')}")

            raise Exception(f"Test timeout after {max_wait} seconds")

    def _parse_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse WebPageTest results"""

        try:
            run_data = data['data']['runs']['1']['firstView']

            metrics = {
                'loadTime': run_data.get('loadTime', 0),
                'TTFB': run_data.get('TTFB', 0),
                'startRender': run_data.get('render', 0),
                'fullyLoaded': run_data.get('fullyLoaded', 0),
                'speedIndex': run_data.get('SpeedIndex', 0),
                'firstContentfulPaint': run_data.get('firstContentfulPaint', 0),
                'largestContentfulPaint': run_data.get('chromeUserTiming.LargestContentfulPaint', 0),
                'cumulativeLayoutShift': run_data.get('chromeUserTiming.CumulativeLayoutShift', 0),
                'totalBlockingTime': run_data.get('TotalBlockingTime', 0),
                'bytesIn': run_data.get('bytesIn', 0),
                'requests': run_data.get('requests', 0),
            }

            scores = {
                'performance': run_data.get('lighthouse', {}).get('Performance', 0),
                'accessibility': run_data.get('lighthouse', {}).get('Accessibility', 0),
                'bestPractices': run_data.get('lighthouse', {}).get('Best Practices', 0),
                'seo': run_data.get('lighthouse', {}).get('SEO', 0),
            }

            return {
                'metrics': metrics,
                'scores': scores,
                'waterfall': {
                    'url': run_data.get('images', {}).get('waterfall', '')
                }
            }

        except Exception as e:
            print(f"Error parsing WebPageTest results: {str(e)}")
            return {'metrics': {}, 'scores': {}, 'waterfall': {}}

    def _fallback_analysis(self, url: str) -> Dict[str, Any]:
        """Fallback when API key is not available"""
        return {
            'success': True,
            'url': url,
            'fallback': True,
            'message': 'WebPageTest API key not configured. Using estimated metrics.',
            'metrics': {
                'loadTime': 0,
                'TTFB': 0,
                'speedIndex': 0,
            },
            'scores': {},
            'suggestions': [
                {
                    'metric': 'Configuration',
                    'severity': 'info',
                    'suggestion': 'Configure WebPageTest API key for detailed analysis. Get one at https://www.webpagetest.org/getkey.php'
                }
            ]
        }

    def _generate_suggestions(self, metrics: Dict[str, Any]) -> list:
        """Generate performance suggestions based on WebPageTest metrics"""

        suggestions = []

        # Speed Index suggestions
        speed_index = metrics.get('speedIndex', 0)
        if speed_index > 4000:
            suggestions.append({
                'metric': 'Speed Index',
                'severity': 'high',
                'suggestion': 'Speed Index is high. Focus on optimizing above-the-fold content, reducing render-blocking resources, and implementing progressive rendering.'
            })
        elif speed_index > 2500:
            suggestions.append({
                'metric': 'Speed Index',
                'severity': 'medium',
                'suggestion': 'Speed Index could be improved. Consider optimizing critical rendering path and reducing JavaScript execution.'
            })

        # Total Blocking Time
        tbt = metrics.get('totalBlockingTime', 0)
        if tbt > 300:
            suggestions.append({
                'metric': 'Total Blocking Time',
                'severity': 'high',
                'suggestion': 'High Total Blocking Time detected. Reduce JavaScript execution time, code split large bundles, and defer non-critical scripts.'
            })

        # Bytes In
        bytes_in = metrics.get('bytesIn', 0)
        if bytes_in > 2000000:  # 2MB
            suggestions.append({
                'metric': 'Page Weight',
                'severity': 'medium',
                'suggestion': f'Page size is {bytes_in / 1000000:.2f}MB. Implement compression, optimize images, and consider lazy loading.'
            })

        # Requests
        requests = metrics.get('requests', 0)
        if requests > 100:
            suggestions.append({
                'metric': 'HTTP Requests',
                'severity': 'medium',
                'suggestion': f'{requests} HTTP requests detected. Consider bundling assets, using sprites, and implementing resource hints.'
            })

        return suggestions
