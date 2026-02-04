import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { performanceApi } from '../services/api'
import { PlusIcon, XMarkIcon, RocketLaunchIcon } from '@heroicons/react/24/outline'

const HomePage: React.FC = () => {
  const navigate = useNavigate()
  const [mainUrl, setMainUrl] = useState('')
  const [competitors, setCompetitors] = useState<string[]>([''])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const addCompetitor = () => {
    if (competitors.length < 5) {
      setCompetitors([...competitors, ''])
    }
  }

  const removeCompetitor = (index: number) => {
    setCompetitors(competitors.filter((_, i) => i !== index))
  }

  const updateCompetitor = (index: number, value: string) => {
    const updated = [...competitors]
    updated[index] = value
    setCompetitors(updated)
  }

  const isValidUrl = (url: string): boolean => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validate main URL
    if (!mainUrl || !isValidUrl(mainUrl)) {
      setError('Please enter a valid URL for your website')
      return
    }

    // Filter out empty competitor URLs and validate
    const validCompetitors = competitors.filter(url => url.trim() !== '')
    const invalidCompetitors = validCompetitors.filter(url => !isValidUrl(url))

    if (invalidCompetitors.length > 0) {
      setError('Please enter valid URLs for all competitor websites')
      return
    }

    try {
      setLoading(true)

      const response = await performanceApi.startAnalysis({
        mainUrl,
        competitors: validCompetitors
      })

      // Navigate to results page
      navigate(`/results/${response.job_id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start analysis. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            Website Performance Analyzer
          </h1>
          <p className="text-xl text-white/90">
            AI-powered performance analysis using Lighthouse, WebPageTest & GTmetrix
          </p>
        </div>

        {/* Main Form */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Main URL Input */}
            <div>
              <label htmlFor="mainUrl" className="block text-sm font-medium text-gray-700 mb-2">
                Your Website URL *
              </label>
              <input
                type="url"
                id="mainUrl"
                value={mainUrl}
                onChange={(e) => setMainUrl(e.target.value)}
                placeholder="https://example.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                required
              />
              <p className="mt-1 text-sm text-gray-500">
                Enter the URL of the website you want to analyze
              </p>
            </div>

            {/* Competitor URLs */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Competitor Websites (Optional)
              </label>
              <div className="space-y-3">
                {competitors.map((competitor, index) => (
                  <div key={index} className="flex gap-2">
                    <input
                      type="url"
                      value={competitor}
                      onChange={(e) => updateCompetitor(index, e.target.value)}
                      placeholder={`https://competitor-${index + 1}.com`}
                      className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                    />
                    <button
                      type="button"
                      onClick={() => removeCompetitor(index)}
                      className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                    >
                      <XMarkIcon className="h-6 w-6" />
                    </button>
                  </div>
                ))}
              </div>

              {competitors.length < 5 && (
                <button
                  type="button"
                  onClick={addCompetitor}
                  className="mt-3 flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
                >
                  <PlusIcon className="h-5 w-5" />
                  Add Competitor URL
                </button>
              )}

              <p className="mt-2 text-sm text-gray-500">
                Compare your website's performance against up to 5 competitors
              </p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-primary-600 to-purple-600 text-white font-semibold py-4 px-6 rounded-lg hover:from-primary-700 hover:to-purple-700 transform hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Starting Analysis...
                </>
              ) : (
                <>
                  <RocketLaunchIcon className="h-6 w-6" />
                  Analyze Performance
                </>
              )}
            </button>
          </form>

          {/* Features List */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              What's Included:
            </h3>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                Lighthouse performance audit
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                WebPageTest analysis
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                GTmetrix comprehensive testing
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                Core Web Vitals (FCP, LCP, CLS)
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                Multi-device screenshots
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                AI-powered recommendations
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                Competitor comparison
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                Downloadable PDF report
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage
