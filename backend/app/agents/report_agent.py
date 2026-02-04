"""
Report Agent for generating comprehensive PDF reports
Uses ReportLab for PDF generation
"""
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
from app.config import settings
import os
import html


class ReportAgent:
    """Agent for generating PDF performance reports"""

    def __init__(self):
        self.reports_dir = settings.reports_dir

    async def generate_report(
        self,
        job_id: str,
        main_url: str,
        competitor_urls: List[str],
        lighthouse_results: List[Dict[str, Any]],
        webpagetest_results: List[Dict[str, Any]],
        gtmetrix_results: List[Dict[str, Any]],
        screenshots: List[Dict[str, Any]],
        aggregated_metrics: Dict[str, Any],
        recommendations: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive PDF report

        Args:
            job_id: Job ID
            main_url: Main website URL
            competitor_urls: List of competitor URLs
            lighthouse_results: Lighthouse test results
            webpagetest_results: WebPageTest results
            gtmetrix_results: GTmetrix results
            screenshots: Screenshot data
            aggregated_metrics: Aggregated performance metrics
            recommendations: AI-generated recommendations

        Returns:
            Dictionary with PDF path and metadata
        """
        print(f"[REPORT] Generating PDF report for job {job_id}...")

        try:
            # Create PDF filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"performance_report_{job_id}_{timestamp}.pdf"
            pdf_path = self.reports_dir / pdf_filename

            # Create PDF
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )

            # Build content
            story = []
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=30,
                alignment=TA_CENTER
            )

            # Title Page
            story.extend(self._create_title_page(main_url, styles, title_style))

            # Executive Summary
            story.extend(self._create_executive_summary(
                aggregated_metrics, styles
            ))

            # Performance Scores
            story.extend(self._create_performance_scores(
                aggregated_metrics, styles
            ))

            # Detailed Metrics
            story.extend(self._create_detailed_metrics(
                lighthouse_results, webpagetest_results, gtmetrix_results, styles
            ))

            # Competitor Comparison
            if competitor_urls:
                story.extend(self._create_competitor_comparison(
                    aggregated_metrics, styles
                ))

            # Recommendations
            story.extend(self._create_recommendations_section(
                recommendations, styles
            ))

            # Screenshots
            story.extend(self._create_screenshots_section(
                screenshots, styles
            ))

            # Build PDF
            doc.build(story)

            return {
                'success': True,
                'pdf_path': str(pdf_path),
                'filename': pdf_filename,
                'size': os.path.getsize(pdf_path),
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[ERROR] Error generating PDF report: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _create_title_page(
        self,
        main_url: str,
        styles,
        title_style
    ) -> List:
        """Create title page"""

        elements = []

        # Title
        elements.append(Spacer(1, 1.5*inch))
        elements.append(Paragraph(
            "Website Performance Analysis Report",
            title_style
        ))

        elements.append(Spacer(1, 0.5*inch))

        # URL
        elements.append(Paragraph(
            f"<b>Analyzed Website:</b> {main_url}",
            styles['Normal']
        ))

        elements.append(Spacer(1, 0.3*inch))

        # Date
        elements.append(Paragraph(
            f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles['Normal']
        ))

        elements.append(Spacer(1, 0.5*inch))

        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_JUSTIFY
        )

        elements.append(Paragraph(
            "This report provides comprehensive performance analysis using industry-standard tools including "
            "Lighthouse, WebPageTest, and GTmetrix. The metrics and recommendations are based on automated "
            "testing and AI-powered analysis.",
            disclaimer_style
        ))

        elements.append(PageBreak())

        return elements

    def _create_executive_summary(
        self,
        aggregated_metrics: Dict[str, Any],
        styles
    ) -> List:
        """Create executive summary section"""

        elements = []

        elements.append(Paragraph("Executive Summary", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))

        summary = aggregated_metrics.get('summary', {})

        # Overall rating
        elements.append(Paragraph(
            f"<b>Overall Performance:</b> {summary.get('overall', 'N/A')}",
            styles['Normal']
        ))

        elements.append(Spacer(1, 0.1*inch))

        # Ranking
        if summary.get('ranking'):
            elements.append(Paragraph(
                f"<b>Competitive Ranking:</b> {summary.get('ranking')}",
                styles['Normal']
            ))

        elements.append(Spacer(1, 0.1*inch))

        # Key metrics
        elements.append(Paragraph(
            f"<b>Key Metrics:</b> {summary.get('key_metrics', 'N/A')}",
            styles['Normal']
        ))

        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_performance_scores(
        self,
        aggregated_metrics: Dict[str, Any],
        styles
    ) -> List:
        """Create performance scores section"""

        elements = []

        elements.append(Paragraph("Performance Scores", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))

        main_site = aggregated_metrics.get('main_site', {})
        averages = main_site.get('averages', {})

        # Create scores table
        data = [
            ['Metric', 'Score', 'Rating']
        ]

        avg_perf = averages.get('avg_performance_score', 0)
        data.append([
            'Overall Performance',
            f'{avg_perf:.1f}/100',
            self._get_score_rating(avg_perf)
        ])

        avg_fcp = averages.get('avg_fcp', 0)
        if avg_fcp:
            data.append([
                'First Contentful Paint (FCP)',
                f'{avg_fcp:.0f}ms',
                self._get_fcp_rating(avg_fcp)
            ])

        avg_lcp = averages.get('avg_lcp', 0)
        if avg_lcp:
            data.append([
                'Largest Contentful Paint (LCP)',
                f'{avg_lcp:.0f}ms',
                self._get_lcp_rating(avg_lcp)
            ])

        # Style table
        table = Table(data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_detailed_metrics(
        self,
        lighthouse_results: List[Dict[str, Any]],
        webpagetest_results: List[Dict[str, Any]],
        gtmetrix_results: List[Dict[str, Any]],
        styles
    ) -> List:
        """Create detailed metrics section"""

        elements = []

        elements.append(Paragraph("Detailed Performance Metrics", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))

        # Lighthouse Metrics
        main_lighthouse = next((r for r in lighthouse_results if r.get('is_main')), None)
        if main_lighthouse and main_lighthouse.get('success'):
            elements.append(Paragraph("Lighthouse Metrics", styles['Heading2']))
            metrics = main_lighthouse.get('data', {}).get('metrics', {})

            data = [
                ['Metric', 'Value'],
                ['First Contentful Paint', f"{metrics.get('fcp', 0):.0f}ms"],
                ['Largest Contentful Paint', f"{metrics.get('lcp', 0):.0f}ms"],
                ['Cumulative Layout Shift', f"{metrics.get('cls', 0):.3f}"],
                ['Time to First Byte', f"{metrics.get('ttfb', 0):.0f}ms"],
            ]

            table = Table(data, colWidths=[3*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_competitor_comparison(
        self,
        aggregated_metrics: Dict[str, Any],
        styles
    ) -> List:
        """Create competitor comparison section"""

        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("Competitor Performance Comparison", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))

        comparisons = aggregated_metrics.get('comparisons', {})
        main_site = aggregated_metrics.get('main_site', {})
        competitors = aggregated_metrics.get('competitors', [])

        # Ranking summary
        elements.append(Paragraph(
            f"Your site ranks <b>#{comparisons.get('rank', 'N/A')}</b> out of "
            f"<b>{comparisons.get('total_sites', 'N/A')}</b> analyzed sites.",
            styles['Heading2']
        ))

        elements.append(Spacer(1, 0.3*inch))

        # Create comparison table
        if competitors:
            elements.append(Paragraph("Performance Metrics Comparison", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))

            # Build table data
            main_avg = main_site.get('averages', {})

            table_data = [
                ['Website', 'Performance Score', 'FCP (ms)', 'LCP (ms)', 'Status']
            ]

            # Add main site
            main_perf = main_avg.get('avg_performance_score', 0)
            main_fcp = main_avg.get('avg_fcp', 0)
            main_lcp = main_avg.get('avg_lcp', 0)

            table_data.append([
                'Your Site',
                f'{main_perf:.1f}',
                f'{main_fcp:.0f}' if main_fcp else 'N/A',
                f'{main_lcp:.0f}' if main_lcp else 'N/A',
                'Main'
            ])

            # Add competitors
            for comp in competitors:
                comp_avg = comp.get('averages', {})
                comp_url = comp.get('url', 'Unknown')
                comp_perf = comp_avg.get('avg_performance_score', 0)
                comp_fcp = comp_avg.get('avg_fcp', 0)
                comp_lcp = comp_avg.get('avg_lcp', 0)

                # Truncate URL for display
                display_url = comp_url.replace('https://', '').replace('http://', '')
                if len(display_url) > 30:
                    display_url = display_url[:27] + '...'

                status = 'Better' if comp_perf < main_perf else 'Worse' if comp_perf > main_perf else 'Equal'

                table_data.append([
                    display_url,
                    f'{comp_perf:.1f}',
                    f'{comp_fcp:.0f}' if comp_fcp else 'N/A',
                    f'{comp_lcp:.0f}' if comp_lcp else 'N/A',
                    status
                ])

            # Create and style table
            table = Table(table_data, colWidths=[2*inch, 1.3*inch, 1.3*inch, 1.3*inch, 1*inch])

            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Highlight main site row
                ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e0f2fe')),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ]

            # Color code the status column
            for i in range(2, len(table_data)):
                status = table_data[i][4]
                if status == 'Worse':
                    table_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#fee2e2')))
                    table_style.append(('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#991b1b')))
                elif status == 'Better':
                    table_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#dcfce7')))
                    table_style.append(('TEXTCOLOR', (4, i), (4, i), colors.HexColor('#166534')))

            table.setStyle(TableStyle(table_style))
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))

            # Add summary
            better_count = len(comparisons.get('better_than', []))
            worse_count = len(comparisons.get('worse_than', []))

            elements.append(Paragraph("Comparison Summary:", styles['Heading3']))
            elements.append(Paragraph(
                f"Your site performs <b>better</b> than {better_count} competitor(s) "
                f"and <b>worse</b> than {worse_count} competitor(s).",
                styles['Normal']
            ))

        elements.append(Spacer(1, 0.3*inch))

        return elements

    def _create_recommendations_section(
        self,
        recommendations: List[Dict[str, str]],
        styles
    ) -> List:
        """Create recommendations section"""

        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("Performance Recommendations", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))

        for i, rec in enumerate(recommendations, 1):
            # Priority badge
            priority = rec.get('priority', 'medium')
            priority_color = {
                'high': colors.red,
                'medium': colors.orange,
                'low': colors.green
            }.get(priority, colors.grey)

            # Escape HTML in text to prevent parsing errors
            title = html.escape(rec.get('title', 'Recommendation'))
            category = html.escape(rec.get('category', 'General'))
            description = html.escape(rec.get('description', 'No description available.'))
            impact = html.escape(rec.get('impact', '')) if rec.get('impact') else None

            elements.append(Paragraph(
                f"<b>{i}. {title}</b> "
                f"<font color='{priority_color.hexval()}'>[{priority.upper()}]</font>",
                styles['Heading3']
            ))

            elements.append(Paragraph(
                f"<b>Category:</b> {category}",
                styles['Normal']
            ))

            elements.append(Paragraph(
                description,
                styles['Normal']
            ))

            if impact:
                elements.append(Paragraph(
                    f"<b>Expected Impact:</b> {impact}",
                    styles['Normal']
                ))

            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _create_screenshots_section(
        self,
        screenshots: List[Dict[str, Any]],
        styles
    ) -> List:
        """Create screenshots section"""

        elements = []

        elements.append(PageBreak())
        elements.append(Paragraph("Website Screenshots", styles['Heading1']))
        elements.append(Spacer(1, 0.2*inch))

        # Add main site screenshots
        main_screenshots = next((s for s in screenshots if s.get('is_main')), None)

        if main_screenshots and main_screenshots.get('data', {}).get('success'):
            screenshot_data = main_screenshots.get('data', {}).get('screenshots', {})

            # Desktop screenshot
            if screenshot_data.get('desktop') and os.path.exists(screenshot_data['desktop']):
                elements.append(Paragraph("Desktop View (1920x1080)", styles['Heading2']))
                try:
                    img = RLImage(screenshot_data['desktop'], width=6*inch, height=4*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.2*inch))
                except Exception as e:
                    print(f"Error adding screenshot: {str(e)}")

        return elements

    def _get_score_rating(self, score: float) -> str:
        """Get rating for a score"""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Poor"

    def _get_fcp_rating(self, fcp: float) -> str:
        """Get FCP rating"""
        if fcp < 1800:
            return "Good"
        elif fcp < 3000:
            return "Needs Improvement"
        else:
            return "Poor"

    def _get_lcp_rating(self, lcp: float) -> str:
        """Get LCP rating"""
        if lcp < 2500:
            return "Good"
        elif lcp < 4000:
            return "Needs Improvement"
        else:
            return "Poor"
