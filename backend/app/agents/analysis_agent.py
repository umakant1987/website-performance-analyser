"""
Analysis Agent for aggregating metrics and generating AI-powered recommendations
Uses LangChain and OpenAI/Anthropic for intelligent analysis
"""
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
import json
from app.config import settings


class AnalysisAgent:
    """Agent for analyzing performance metrics and generating recommendations"""

    def __init__(self):
        # Use OpenAI for analysis (prioritized due to reliability)
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4-turbo",
                openai_api_key=settings.openai_api_key,
                temperature=0.3
            )
            print("[AI] Using OpenAI GPT-4 for recommendations")
        elif settings.anthropic_api_key:
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                anthropic_api_key=settings.anthropic_api_key,
                temperature=0.3
            )
            print("[AI] Using Anthropic Claude for recommendations")
        else:
            self.llm = None
            print("[WARN] No AI API key configured. Using rule-based analysis.")

    async def aggregate_metrics(
        self,
        lighthouse: List[Dict[str, Any]],
        webpagetest: List[Dict[str, Any]],
        gtmetrix: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate metrics from all performance testing tools

        Args:
            lighthouse: Lighthouse results
            webpagetest: WebPageTest results
            gtmetrix: GTmetrix results

        Returns:
            Aggregated metrics with comparisons
        """
        print(f"[AI] Aggregating performance metrics...")

        aggregated = {
            'main_site': {},
            'competitors': [],
            'comparisons': {},
            'summary': {}
        }

        # Process main site metrics
        main_lighthouse = next((r for r in lighthouse if r.get('is_main')), None)
        main_webpagetest = next((r for r in webpagetest if r.get('is_main')), None)
        main_gtmetrix = next((r for r in gtmetrix if r.get('is_main')), None)

        if main_lighthouse:
            aggregated['main_site'] = self._aggregate_single_site(
                main_lighthouse, main_webpagetest, main_gtmetrix
            )

        # Process competitor sites
        competitor_urls = [r['url'] for r in lighthouse if not r.get('is_main')]
        for url in competitor_urls:
            comp_lighthouse = next((r for r in lighthouse if r['url'] == url), None)
            comp_webpagetest = next((r for r in webpagetest if r['url'] == url), None)
            comp_gtmetrix = next((r for r in gtmetrix if r['url'] == url), None)

            competitor_data = self._aggregate_single_site(
                comp_lighthouse, comp_webpagetest, comp_gtmetrix
            )
            competitor_data['url'] = url
            aggregated['competitors'].append(competitor_data)

        # Generate comparisons
        aggregated['comparisons'] = self._generate_comparisons(
            aggregated['main_site'],
            aggregated['competitors']
        )

        # Generate summary
        aggregated['summary'] = self._generate_summary(
            aggregated['main_site'],
            aggregated['comparisons']
        )

        return aggregated

    def _aggregate_single_site(
        self,
        lighthouse: Dict[str, Any],
        webpagetest: Dict[str, Any],
        gtmetrix: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Aggregate metrics from a single site"""

        metrics = {}

        # Extract from Lighthouse
        if lighthouse and lighthouse.get('data', {}).get('success'):
            lh_metrics = lighthouse.get('data', {}).get('metrics', {})
            lh_scores = lighthouse.get('data', {}).get('scores', {})

            metrics['lighthouse'] = {
                'fcp': lh_metrics.get('fcp', 0),
                'lcp': lh_metrics.get('lcp', 0),
                'cls': lh_metrics.get('cls', 0),
                'ttfb': lh_metrics.get('ttfb', 0),
                'performance_score': lh_scores.get('performance_score', 0)
            }

        # Extract from WebPageTest
        if webpagetest and webpagetest.get('data', {}).get('success') and not webpagetest.get('data', {}).get('fallback'):
            wpt_metrics = webpagetest.get('data', {}).get('metrics', {})
            wpt_scores = webpagetest.get('data', {}).get('scores', {})

            metrics['webpagetest'] = {
                'loadTime': wpt_metrics.get('loadTime', 0),
                'TTFB': wpt_metrics.get('TTFB', 0),
                'speedIndex': wpt_metrics.get('speedIndex', 0),
                'firstContentfulPaint': wpt_metrics.get('firstContentfulPaint', 0),
                'performance_score': wpt_scores.get('performance', 0)
            }

        # Extract from GTmetrix
        if gtmetrix and gtmetrix.get('data', {}).get('success') and not gtmetrix.get('data', {}).get('fallback'):
            gtm_metrics = gtmetrix.get('data', {}).get('metrics', {})
            gtm_scores = gtmetrix.get('data', {}).get('scores', {})

            metrics['gtmetrix'] = {
                'performanceScore': gtm_metrics.get('performanceScore', 0),
                'fullyLoadedTime': gtm_metrics.get('fullyLoadedTime', 0),
                'totalPageSize': gtm_metrics.get('totalPageSize', 0),
                'requests': gtm_metrics.get('requests', 0),
                'speedIndex': gtm_metrics.get('speedIndex', 0)
            }

        # Calculate averages
        metrics['averages'] = self._calculate_averages(metrics)

        return metrics

    def _calculate_averages(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calculate average metrics across tools"""

        averages = {}

        # FCP average
        fcp_values = []
        if 'lighthouse' in metrics and metrics['lighthouse'].get('fcp'):
            fcp_values.append(metrics['lighthouse']['fcp'])
        if 'webpagetest' in metrics and metrics['webpagetest'].get('firstContentfulPaint'):
            fcp_values.append(metrics['webpagetest']['firstContentfulPaint'])

        if fcp_values:
            averages['avg_fcp'] = sum(fcp_values) / len(fcp_values)

        # LCP average
        if 'lighthouse' in metrics:
            averages['avg_lcp'] = metrics['lighthouse'].get('lcp', 0)

        # Performance Score average
        perf_scores = []
        if 'lighthouse' in metrics and metrics['lighthouse'].get('performance_score'):
            perf_scores.append(metrics['lighthouse']['performance_score'])
        if 'webpagetest' in metrics and metrics['webpagetest'].get('performance_score'):
            perf_scores.append(metrics['webpagetest']['performance_score'])
        if 'gtmetrix' in metrics and metrics['gtmetrix'].get('performanceScore'):
            perf_scores.append(metrics['gtmetrix']['performanceScore'])

        if perf_scores:
            averages['avg_performance_score'] = sum(perf_scores) / len(perf_scores)

        return averages

    def _generate_comparisons(
        self,
        main_site: Dict[str, Any],
        competitors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comparisons between main site and competitors"""

        if not competitors:
            return {}

        main_perf = main_site.get('averages', {}).get('avg_performance_score', 0)

        comparisons = {
            'rank': 1,
            'total_sites': len(competitors) + 1,
            'better_than': [],
            'worse_than': []
        }

        for comp in competitors:
            comp_perf = comp.get('averages', {}).get('avg_performance_score', 0)

            if main_perf > comp_perf:
                comparisons['better_than'].append({
                    'url': comp.get('url'),
                    'score': comp_perf,
                    'difference': main_perf - comp_perf
                })
            else:
                comparisons['worse_than'].append({
                    'url': comp.get('url'),
                    'score': comp_perf,
                    'difference': comp_perf - main_perf
                })
                comparisons['rank'] += 1

        return comparisons

    def _generate_summary(
        self,
        main_site: Dict[str, Any],
        comparisons: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate text summary of performance"""

        averages = main_site.get('averages', {})
        perf_score = averages.get('avg_performance_score', 0)

        summary = {
            'overall': self._get_performance_rating(perf_score),
            'ranking': f"Ranked {comparisons.get('rank', 'N/A')} out of {comparisons.get('total_sites', 1)} sites",
            'key_metrics': self._summarize_key_metrics(main_site)
        }

        return summary

    def _get_performance_rating(self, score: float) -> str:
        """Get performance rating based on score"""

        if score >= 90:
            return "Excellent - Your site has outstanding performance!"
        elif score >= 75:
            return "Good - Your site performs well with room for optimization."
        elif score >= 50:
            return "Fair - Your site needs performance improvements."
        else:
            return "Poor - Your site has significant performance issues."

    def _summarize_key_metrics(self, site: Dict[str, Any]) -> str:
        """Summarize key performance metrics"""

        averages = site.get('averages', {})

        fcp = averages.get('avg_fcp', 0)
        lcp = averages.get('avg_lcp', 0)

        summary_parts = []

        if fcp:
            fcp_rating = "good" if fcp < 1800 else "needs improvement" if fcp < 3000 else "poor"
            summary_parts.append(f"FCP: {fcp:.0f}ms ({fcp_rating})")

        if lcp:
            lcp_rating = "good" if lcp < 2500 else "needs improvement" if lcp < 4000 else "poor"
            summary_parts.append(f"LCP: {lcp:.0f}ms ({lcp_rating})")

        return ", ".join(summary_parts) if summary_parts else "Metrics unavailable"

    async def generate_recommendations(
        self,
        main_url: str,
        aggregated_metrics: Dict[str, Any]
    ) -> List[str]:
        """
        Generate AI-powered recommendations based on aggregated metrics

        Args:
            main_url: Main site URL
            aggregated_metrics: Aggregated performance metrics

        Returns:
            List of actionable recommendations
        """
        print(f"[IDEA] Generating AI-powered recommendations...")

        if not self.llm:
            return self._generate_rule_based_recommendations(aggregated_metrics)

        # Prepare data for AI analysis
        context = {
            'url': main_url,
            'metrics': aggregated_metrics['main_site'],
            'comparisons': aggregated_metrics['comparisons'],
            'summary': aggregated_metrics['summary']
        }

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a senior web performance consultant and optimization expert.
            Your goal is to provide highly specific, technical, and actionable recommendations that developers
            can implement immediately. Focus on Core Web Vitals (FCP, LCP, CLS, TTFB) and real-world optimizations.

            For each recommendation:
            - Be VERY specific about what to fix (e.g., mention specific file types, techniques, tools)
            - Provide technical implementation details
            - Quantify expected improvements where possible
            - Prioritize by impact on user experience and business metrics
            - Include both quick wins and long-term optimizations"""),
            HumanMessage(content=f"""Analyze these performance metrics and provide 8-12 highly detailed, prioritized recommendations:

{json.dumps(context, indent=2)}

Provide recommendations in this JSON format:
[
  {{
    "priority": "high|medium|low",
    "category": "Performance|Optimization|Best Practices|Images|JavaScript|CSS|Caching|Server",
    "title": "Specific, technical title (e.g., 'Implement WebP images with fallback', not just 'Optimize images')",
    "description": "Detailed, actionable description with specific techniques, tools, or code patterns. Include: WHAT to do, HOW to do it, and WHY it matters. Mention specific file types, size limits, or metrics.",
    "impact": "Quantified expected impact (e.g., 'Reduce LCP by 30-40%, improve load time by 1-2s', not just 'faster loading')"
  }}
]

Key areas to analyze:
1. FCP and LCP metrics - suggest specific resource optimizations
2. File sizes and requests - recommend code splitting, lazy loading, compression
3. Caching strategies - suggest specific cache headers and CDN usage
4. Image optimization - recommend modern formats (WebP, AVIF), responsive images, lazy loading
5. JavaScript optimization - suggest defer/async, tree shaking, code splitting
6. CSS optimization - recommend critical CSS, unused CSS removal
7. Server optimization - suggest HTTP/2, compression, edge caching
8. Third-party scripts - recommend async loading or alternatives

Be extremely specific and technical with measurable impact.""")
        ])

        try:
            response = await self.llm.ainvoke(prompt.format_messages())

            # Parse response
            content = response.content
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                return recommendations
            else:
                # Fallback to rule-based
                return self._generate_rule_based_recommendations(aggregated_metrics)

        except Exception as e:
            print(f"Error generating AI recommendations: {str(e)}")
            return self._generate_rule_based_recommendations(aggregated_metrics)

    def _generate_rule_based_recommendations(
        self,
        aggregated_metrics: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate rule-based recommendations as fallback"""

        recommendations = []
        main_site = aggregated_metrics.get('main_site', {})
        lighthouse = main_site.get('lighthouse', {})

        # FCP recommendations
        fcp = lighthouse.get('fcp', 0)
        if fcp > 3000:
            recommendations.append({
                'priority': 'high',
                'category': 'Performance',
                'title': 'Improve First Contentful Paint',
                'description': 'Reduce server response time, eliminate render-blocking resources, and optimize critical rendering path.',
                'impact': 'Users will see content faster, improving perceived performance'
            })

        # LCP recommendations
        lcp = lighthouse.get('lcp', 0)
        if lcp > 4000:
            recommendations.append({
                'priority': 'high',
                'category': 'Performance',
                'title': 'Optimize Largest Contentful Paint',
                'description': 'Optimize images, use CDN, implement lazy loading, and prioritize above-the-fold content.',
                'impact': 'Faster visual completion and better user experience'
            })

        # Add default recommendations
        recommendations.append({
            'priority': 'medium',
            'category': 'Optimization',
            'title': 'Implement Caching Strategy',
            'description': 'Use browser caching, CDN caching, and server-side caching to reduce load times.',
            'impact': 'Faster repeat visits and reduced server load'
        })

        return recommendations
