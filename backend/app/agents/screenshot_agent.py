"""
Screenshot Agent for capturing website screenshots
Uses Playwright for high-quality screenshots
"""
import asyncio
from typing import Dict, Any
from playwright.async_api import async_playwright
from pathlib import Path
import base64
from app.config import settings


class ScreenshotAgent:
    """Agent for capturing website screenshots"""

    def __init__(self):
        self.screenshots_dir = settings.screenshots_dir

    async def capture(self, url: str, job_id: str) -> Dict[str, Any]:
        """
        Capture screenshots of the given URL

        Args:
            url: The URL to capture
            job_id: Job ID for organizing screenshots

        Returns:
            Dictionary containing screenshot paths and metadata
        """
        print(f"[SCREENSHOT] Capturing screenshots for {url}")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )

                # Create job-specific directory
                job_dir = self.screenshots_dir / job_id
                job_dir.mkdir(parents=True, exist_ok=True)

                # Capture desktop screenshot
                desktop_path = await self._capture_viewport(
                    browser, url, job_dir, 'desktop',
                    width=1920, height=1080
                )

                # Capture tablet screenshot
                tablet_path = await self._capture_viewport(
                    browser, url, job_dir, 'tablet',
                    width=768, height=1024
                )

                # Capture mobile screenshot
                mobile_path = await self._capture_viewport(
                    browser, url, job_dir, 'mobile',
                    width=375, height=667
                )

                # Capture full page screenshot (desktop)
                fullpage_path = await self._capture_fullpage(
                    browser, url, job_dir
                )

                await browser.close()

                return {
                    'success': True,
                    'url': url,
                    'screenshots': {
                        'desktop': str(desktop_path),
                        'tablet': str(tablet_path),
                        'mobile': str(mobile_path),
                        'fullpage': str(fullpage_path)
                    },
                    'metadata': {
                        'job_id': job_id,
                        'directory': str(job_dir)
                    }
                }

        except Exception as e:
            print(f"[ERROR] Screenshot error for {url}: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'screenshots': {}
            }

    async def _capture_viewport(
        self,
        browser,
        url: str,
        output_dir: Path,
        device_type: str,
        width: int,
        height: int
    ) -> Path:
        """Capture screenshot for specific viewport"""

        context = await browser.new_context(
            viewport={'width': width, 'height': height},
            user_agent=self._get_user_agent(device_type)
        )

        page = await context.new_page()

        try:
            # Using 'domcontentloaded' for better reliability on cloud infrastructure
            await page.goto(url, wait_until='domcontentloaded', timeout=90000)
            await asyncio.sleep(3)  # Wait for animations and additional content

            # Sanitize URL for filename
            safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_')[:50]
            screenshot_path = output_dir / f"{device_type}_{safe_url}.png"

            await page.screenshot(path=str(screenshot_path))

            return screenshot_path

        finally:
            await context.close()

    async def _capture_fullpage(
        self,
        browser,
        url: str,
        output_dir: Path
    ) -> Path:
        """Capture full page screenshot"""

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )

        page = await context.new_page()

        try:
            # Using 'domcontentloaded' for better reliability on cloud infrastructure
            await page.goto(url, wait_until='domcontentloaded', timeout=90000)
            await asyncio.sleep(3)

            # Sanitize URL for filename
            safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_')[:50]
            screenshot_path = output_dir / f"fullpage_{safe_url}.png"

            await page.screenshot(
                path=str(screenshot_path),
                full_page=True
            )

            return screenshot_path

        finally:
            await context.close()

    def _get_user_agent(self, device_type: str) -> str:
        """Get appropriate user agent for device type"""

        agents = {
            'desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'tablet': 'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        }

        return agents.get(device_type, agents['desktop'])

    async def capture_with_dimensions(
        self,
        url: str,
        job_id: str,
        custom_dimensions: list
    ) -> Dict[str, Any]:
        """
        Capture screenshots with custom dimensions

        Args:
            url: The URL to capture
            job_id: Job ID for organizing screenshots
            custom_dimensions: List of dicts with 'name', 'width', 'height'

        Returns:
            Dictionary containing screenshot paths
        """

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                job_dir = self.screenshots_dir / job_id
                job_dir.mkdir(parents=True, exist_ok=True)

                screenshots = {}

                for dim in custom_dimensions:
                    name = dim['name']
                    width = dim['width']
                    height = dim['height']

                    screenshot_path = await self._capture_viewport(
                        browser, url, job_dir, name, width, height
                    )

                    screenshots[name] = str(screenshot_path)

                await browser.close()

                return {
                    'success': True,
                    'url': url,
                    'screenshots': screenshots
                }

        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'screenshots': {}
            }
