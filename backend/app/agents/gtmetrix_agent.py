"""
GTmetrix Agent for performance testing
Uses GTmetrix API v2.0
"""
import asyncio
import httpx
import base64
from typing import Dict, Any
from app.config import settings


class GTMetrixAgent:
    """Agent for running GTmetrix performance analysis"""

    def __init__(self):
        self.api_key = settings.gtmetrix_api_key
        self.api_username = settings.gtmetrix_api_username
        self.base_url = "https://gtmetrix.com/api/2.0"

    async def analyze(self, url: str) -> Dict[str, Any]:
        """
        Run GTmetrix analysis on the given URL

        Args:
            url: The URL to analyze

        Returns:
            Dictionary containing GTmetrix metrics
        """
        print(f"[GTMETRIX] Running GTmetrix analysis for {url}")

        if not self.api_key or not self.api_username:
            print("[WARN] GTmetrix API credentials not configured, using fallback mode")
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
                'suggestions': self._generate_suggestions(results.get('metrics', {}))
            }

        except Exception as e:
            print(f"[ERROR] GTmetrix error for {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'metrics': {},
                'scores': {},
                'suggestions': []
            }

    def _get_auth_header(self) -> str:
        """Get Basic Auth header for GTmetrix API"""
        credentials = f"{self.api_username}:{self.api_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"

    async def _submit_test(self, url: str) -> str:
        """Submit a test to GTmetrix API"""

        headers = {
            'Authorization': self._get_auth_header(),
            'Content-Type': 'application/json'
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/tests",
                headers=headers,
                json={
                    'url': url,
                    'location': 'default',
                    'browser': 'chrome',
                }
            )

            response.raise_for_status()
            data = response.json()

            return data['data']['id']

    async def _wait_for_results(self, test_id: str, max_wait: int = 180) -> Dict[str, Any]:
        """Poll for test results with timeout"""

        headers = {
            'Authorization': self._get_auth_header()
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for _ in range(max_wait // 5):  # Check every 5 seconds
                await asyncio.sleep(5)

                response = await client.get(
                    f"{self.base_url}/tests/{test_id}",
                    headers=headers
                )

                response.raise_for_status()
                data = response.json()

                state = data['data']['attributes']['state']

                if state == 'completed':
                    # Test complete
                    return self._parse_results(data)
                elif state == 'error':
                    raise Exception(f"Test failed: {data['data']['attributes'].get('error')}")

            raise Exception(f"Test timeout after {max_wait} seconds")

    def _parse_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse GTmetrix results"""

        try:
            attrs = data['data']['attributes']

            metrics = {
                'performanceScore': attrs.get('performance_score', 0),
                'structureScore': attrs.get('structure_score', 0),
                'fullyLoadedTime': attrs.get('fully_loaded_time', 0),
                'totalPageSize': attrs.get('page_bytes', 0),
                'requests': attrs.get('page_elements', 0),
                'htmlSize': attrs.get('html_bytes', 0),
                'htmlLoadTime': attrs.get('html_load_time', 0),
                'pagespeedScore': attrs.get('pagespeed_score', 0),
                'yslow_score': attrs.get('yslow_score', 0),
                'ttfb': attrs.get('time_to_first_byte', 0),
                'firstContentfulPaint': attrs.get('first_contentful_paint', 0),
                'largestContentfulPaint': attrs.get('largest_contentful_paint', 0),
                'timeToInteractive': attrs.get('time_to_interactive', 0),
                'totalBlockingTime': attrs.get('total_blocking_time', 0),
                'cumulativeLayoutShift': attrs.get('cumulative_layout_shift', 0),
                'speedIndex': attrs.get('speed_index', 0),
            }

            scores = {
                'performance': attrs.get('performance_score', 0),
                'structure': attrs.get('structure_score', 0),
                'pagespeed': attrs.get('pagespeed_score', 0),
                'yslow': attrs.get('yslow_score', 0),
            }

            return {
                'metrics': metrics,
                'scores': scores
            }

        except Exception as e:
            print(f"Error parsing GTmetrix results: {str(e)}")
            return {'metrics': {}, 'scores': {}}

    def _fallback_analysis(self, url: str) -> Dict[str, Any]:
        """Fallback when API credentials are not available"""
        return {
            'success': True,
            'url': url,
            'fallback': True,
            'message': 'GTmetrix API credentials not configured. Using estimated metrics.',
            'metrics': {
                'performanceScore': 0,
                'structureScore': 0,
                'fullyLoadedTime': 0,
            },
            'scores': {},
            'suggestions': [
                {
                    'metric': 'Configuration',
                    'severity': 'info',
                    'suggestion': 'Configure GTmetrix API credentials for detailed analysis. Sign up at https://gtmetrix.com/api/'
                }
            ]
        }

    def _generate_suggestions(self, metrics: Dict[str, Any]) -> list:
        """Generate performance suggestions based on GTmetrix metrics"""

        suggestions = []

        # Performance Score
        perf_score = metrics.get('performanceScore', 0)
        if perf_score < 50:
            suggestions.append({
                'metric': 'Performance Score',
                'severity': 'high',
                'suggestion': f'Low performance score ({perf_score}%). Focus on Core Web Vitals optimization, reduce JavaScript execution, and improve server response times.'
            })
        elif perf_score < 75:
            suggestions.append({
                'metric': 'Performance Score',
                'severity': 'medium',
                'suggestion': f'Performance score ({perf_score}%) has room for improvement. Review GTmetrix recommendations for specific optimizations.'
            })

        # Structure Score
        struct_score = metrics.get('structureScore', 0)
        if struct_score < 50:
            suggestions.append({
                'metric': 'Structure Score',
                'severity': 'high',
                'suggestion': f'Low structure score ({struct_score}%). Follow web best practices: minify resources, enable compression, leverage browser caching.'
            })
        elif struct_score < 75:
            suggestions.append({
                'metric': 'Structure Score',
                'severity': 'medium',
                'suggestion': f'Structure score ({struct_score}%) could be better. Review technical optimizations and best practices.'
            })

        # Page Size
        page_size = metrics.get('totalPageSize', 0)
        if page_size > 3000000:  # 3MB
            suggestions.append({
                'metric': 'Page Size',
                'severity': 'high',
                'suggestion': f'Large page size ({page_size / 1000000:.2f}MB). Optimize images, implement lazy loading, use modern formats, and enable compression.'
            })

        # Load Time
        load_time = metrics.get('fullyLoadedTime', 0)
        if load_time > 5000:
            suggestions.append({
                'metric': 'Load Time',
                'severity': 'high',
                'suggestion': f'Slow load time ({load_time / 1000:.1f}s). Optimize critical rendering path, reduce third-party scripts, and use CDN.'
            })
        elif load_time > 3000:
            suggestions.append({
                'metric': 'Load Time',
                'severity': 'medium',
                'suggestion': f'Load time ({load_time / 1000:.1f}s) could be improved. Consider caching strategies and resource optimization.'
            })

        # Requests
        requests = metrics.get('requests', 0)
        if requests > 100:
            suggestions.append({
                'metric': 'HTTP Requests',
                'severity': 'medium',
                'suggestion': f'High number of requests ({requests}). Bundle resources, use sprites, implement HTTP/2, and reduce third-party requests.'
            })

        return suggestions
