# 🚀 Lighthouse-Only Quick Start

This simplified version uses **only Lighthouse** for performance testing. Perfect for getting started quickly with **zero configuration**!

## ✅ What You Get

### Core Web Vitals Analysis
- ⚡ **First Contentful Paint (FCP)** - Time to first content
- 🎨 **Largest Contentful Paint (LCP)** - Time to main content
- 📐 **Cumulative Layout Shift (CLS)** - Visual stability
- 🚀 **Time to First Byte (TTFB)** - Server response time

### Additional Metrics
- DOM Content Loaded time
- Page load complete time
- Resource count and total size
- Performance scores (0-100)

### Visual Analysis
- 🖥️ Desktop screenshots (1920x1080)
- 📱 Tablet screenshots (768x1024)
- 📱 Mobile screenshots (375x667)
- 📄 Full page captures

### Smart Recommendations
- 🤖 AI-powered suggestions (optional)
- 📋 Rule-based fallback (works without API keys!)
- 🎯 Prioritized by impact
- ✅ Actionable improvement steps

### Professional Reports
- 📊 Complete PDF with all metrics
- 📸 Visual screenshots
- 💡 Detailed recommendations
- 📈 Performance scores

## ⚡ 5-Minute Setup

### Step 1: Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate

# Install dependencies (minimal set)
pip install -r requirements-minimal.txt

# Install Playwright browser (one-time)
playwright install chromium

# Create empty .env file (no keys needed!)
echo. > .env  # Windows
touch .env     # Mac/Linux

# Start the server
cd app
python main.py
```

✅ Backend running on **http://localhost:8000**

### Step 2: Frontend Setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

✅ Frontend running on **http://localhost:3000**

### Step 3: Analyze Your First Website!

1. Open **http://localhost:3000** in your browser
2. Enter a website URL (e.g., `https://example.com`)
3. Click **"Analyze Performance"**
4. Wait ~30-60 seconds ⏱️
5. View results and download PDF 📄

## 🎉 No API Keys Required!

This works **completely standalone** without any external services:

| Feature | Status | Technology |
|---------|--------|------------|
| ✅ Lighthouse Analysis | **Built-in** | Playwright |
| ✅ Screenshots | **Built-in** | Playwright |
| ✅ PDF Reports | **Built-in** | ReportLab |
| ✅ Basic Recommendations | **Built-in** | Rule-based |
| 🎯 AI Recommendations | Optional | OpenAI/Anthropic |

## 🔧 Optional: Add AI Recommendations

For smarter, context-aware recommendations, add to `backend/.env`:

```env
# Option 1: OpenAI
OPENAI_API_KEY=sk-...

# Option 2: Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
```

Get API keys:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

## 📊 Understanding Your Results

### Performance Scores

```
Score Range     Rating          Action
90-100         🟢 Excellent     Keep it up!
75-89          🟡 Good          Minor improvements
50-74          🟠 Fair          Needs optimization
0-49           🔴 Poor          Critical issues
```

### Core Web Vitals Thresholds

#### First Contentful Paint (FCP)
```
< 1.8s         🟢 Good
1.8s - 3.0s    🟡 Needs Improvement
> 3.0s         🔴 Poor
```

#### Largest Contentful Paint (LCP)
```
< 2.5s         🟢 Good
2.5s - 4.0s    🟡 Needs Improvement
> 4.0s         🔴 Poor
```

#### Cumulative Layout Shift (CLS)
```
< 0.1          🟢 Good
0.1 - 0.25     🟡 Needs Improvement
> 0.25         🔴 Poor
```

#### Time to First Byte (TTFB)
```
< 800ms        🟢 Good
800ms - 1800ms 🟡 Needs Improvement
> 1800ms       🔴 Poor
```

## 📝 Sample Analysis

```
🔍 Analyzing: https://example.com

Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Performance Score    85/100  🟢 Good
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Web Vitals:
✅ FCP:  1.2s    (Good)
✅ LCP:  2.1s    (Good)
⚠️  CLS:  0.15   (Needs Improvement)
✅ TTFB: 450ms   (Good)

Page Metrics:
📦 Total Size:    2.1 MB
🔗 Requests:      45
⏱️  Load Time:     2.8s

Top Recommendations:
1. 🎯 HIGH: Fix layout shift in hero section
   → Expected impact: Improve CLS to < 0.1

2. 🟡 MEDIUM: Optimize image sizes
   → Expected impact: Reduce load time by 30%

3. 🟢 LOW: Enable browser caching
   → Expected impact: Faster repeat visits
```

## 🛠️ Troubleshooting

### Issue: Playwright Installation Fails

**Solution:**
```bash
playwright install --with-deps chromium
```

### Issue: Port Already in Use

**Backend (8000):**

Edit `backend/app/config.py`:
```python
port: int = 8001  # Change to any available port
```

**Frontend (3000):**

Edit `frontend/vite.config.ts`:
```typescript
server: {
  port: 3001  // Change to any available port
}
```

### Issue: Import Errors

**Solution:** Make sure virtual environment is activated:

```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Then reinstall
pip install -r requirements-minimal.txt
```

### Issue: Frontend Won't Start

**Solution:** Clean install:
```bash
cd frontend
rm -rf node_modules package-lock.json  # Mac/Linux
# or
rmdir /s node_modules & del package-lock.json  # Windows

npm install
npm run dev
```

## 📂 What's Running?

### Active Components (Lighthouse-Only Mode)

```
✅ lighthouse_agent.py     - Core Web Vitals measurement
✅ screenshot_agent.py     - Multi-device screenshots
✅ analysis_agent.py       - Metrics aggregation
✅ report_agent.py         - PDF generation
```

### Skipped Components
```
⏭️ webpagetest_agent.py   - (Not used)
⏭️ gtmetrix_agent.py      - (Not used)
```

## 🚀 What to Analyze?

### Great Starting Points

1. **Your Homepage**
   ```
   https://yourwebsite.com
   ```

2. **Product Pages**
   ```
   https://yourwebsite.com/products/item
   ```

3. **Blog Posts**
   ```
   https://yourwebsite.com/blog/article
   ```

4. **Landing Pages**
   ```
   https://yourwebsite.com/special-offer
   ```

### Compare Competitors

```
Main URL:       https://yoursite.com
Competitor 1:   https://competitor1.com
Competitor 2:   https://competitor2.com
```

Analysis time: ~1-2 minutes per URL

## 🎯 Common Use Cases

### Case 1: Before/After Optimization

1. Run analysis before changes
2. Download PDF report
3. Make optimizations
4. Run analysis again
5. Compare results!

### Case 2: Competitive Analysis

1. Add your site + competitors
2. Compare performance scores
3. See where you rank
4. Identify improvement opportunities

### Case 3: Regular Monitoring

1. Analyze weekly/monthly
2. Track performance trends
3. Catch regressions early
4. Maintain performance

## 📈 Next Steps

Once you're comfortable with Lighthouse-only mode:

### Expand Testing
- ✅ Add WebPageTest for waterfall charts
- ✅ Add GTmetrix for multi-location testing
- ✅ Get more comprehensive metrics

### Scale to Production
- ✅ Convert to MCP servers
- ✅ Deploy with Docker
- ✅ Add Redis for job storage
- ✅ Set up monitoring

### Customize
- ✅ Add custom metrics
- ✅ Create custom reports
- ✅ Integrate with CI/CD
- ✅ Build dashboards

## 💡 Pro Tips

1. **Test During Off-Peak Hours**
   - More accurate TTFB measurements
   - Less network congestion

2. **Clear Cache Between Tests**
   - Get fresh measurements
   - Simulate first-time visitors

3. **Test Multiple Pages**
   - Homepage often isn't representative
   - Product pages may be slower

4. **Follow Recommendations in Order**
   - High priority items first
   - Biggest impact for effort

5. **Re-test After Changes**
   - Verify improvements
   - Watch for regressions

## API Usage

### Start Analysis
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "mainUrl": "https://example.com",
    "competitors": ["https://competitor.com"]
  }'
```

### Check Status
```bash
curl http://localhost:8000/api/status/{job_id}
```

### Get Results
```bash
curl http://localhost:8000/api/results/{job_id}
```

### Download PDF
```bash
curl http://localhost:8000/api/download/{job_id} -o report.pdf
```

## ✅ Success Checklist

Before you start analyzing:

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Playwright browser installed
- [ ] Backend running on :8000
- [ ] Frontend running on :3000
- [ ] Browser open to localhost:3000

## 🎊 You're Ready!

This Lighthouse-only version gives you:

- ✅ **Fast setup** - 5 minutes from zero to analyzing
- ✅ **Zero config** - No API keys required
- ✅ **Core metrics** - Everything you need to get started
- ✅ **Professional reports** - Publication-ready PDFs
- ✅ **Easy to extend** - Add more tools later

Start analyzing and improving your website performance today! 🚀

---

**Questions?** Check the main [README.md](README.md) or [ARCHITECTURE.md](ARCHITECTURE.md) for more details.
