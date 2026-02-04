import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { performanceApi, AnalysisStatus, AnalysisResults } from '../services/api'
import { ArrowDownTrayIcon, ArrowLeftIcon } from '@heroicons/react/24/outline'
import ProgressBar from '../components/ProgressBar'
import MetricsCard from '../components/MetricsCard'
import RecommendationsList from '../components/RecommendationsList'

const ResultsPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()

  const [status, setStatus] = useState<AnalysisStatus | null>(null)
  const [results, setResults] = useState<AnalysisResults | null>(null)
  const [error, setError] = useState('')
  const [polling, setPolling] = useState(true)

  useEffect(() => {
    if (!jobId) return

    let shouldContinuePolling = true

    const pollStatus = async () => {
      try {
        const statusData = await performanceApi.getStatus(jobId)
        setStatus(statusData)

        if (statusData.status === 'completed') {
          shouldContinuePolling = false
          setPolling(false)
          const resultsData = await performanceApi.getResults(jobId)
          setResults(resultsData)
        } else if (statusData.status === 'failed') {
          shouldContinuePolling = false
          setPolling(false)
          setError(statusData.error || 'Analysis failed')
        }
      } catch (err: any) {
        shouldContinuePolling = false
        setError('Failed to fetch analysis status')
        setPolling(false)
      }
    }

    // Initial poll
    pollStatus()

    // Continue polling
    const interval = setInterval(() => {
      if (shouldContinuePolling) {
        pollStatus()
      }
    }, 3000) // Poll every 3 seconds

    return () => {
      shouldContinuePolling = false
      clearInterval(interval)
    }
  }, [jobId])

  const handleDownloadReport = async () => {
    if (!jobId) return

    try {
      const blob = await performanceApi.downloadReport(jobId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `performance-report-${jobId}.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err) {
      alert('Failed to download report')
    }
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-white hover:text-white/80 transition"
          >
            <ArrowLeftIcon className="h-5 w-5" />
            New Analysis
          </button>

          {results && (
            <button
              onClick={handleDownloadReport}
              className="flex items-center gap-2 bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition shadow-lg"
            >
              <ArrowDownTrayIcon className="h-5 w-5" />
              Download PDF Report
            </button>
          )}
        </div>

        {/* Progress Section */}
        {polling && status && (
          <div className="bg-white rounded-2xl shadow-2xl p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Analyzing Performance...
            </h2>
            <ProgressBar progress={status.progress} />
            <p className="mt-4 text-gray-600">{status.current_step}</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-white rounded-2xl shadow-2xl p-8">
            <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
              <h3 className="font-semibold mb-2">Analysis Failed</h3>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="space-y-8">
            {/* Summary Card */}
            <div className="bg-white rounded-2xl shadow-2xl p-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Performance Analysis Complete
              </h2>
              <p className="text-gray-600 mb-6">{results.main_url}</p>

              {/* Metrics Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricsCard
                  title="Performance Score"
                  value={results.aggregated_metrics?.main_site?.averages?.avg_performance_score || 0}
                  type="score"
                />
                <MetricsCard
                  title="First Contentful Paint"
                  value={results.aggregated_metrics?.main_site?.averages?.avg_fcp || 0}
                  type="time"
                />
                <MetricsCard
                  title="Largest Contentful Paint"
                  value={results.aggregated_metrics?.main_site?.averages?.avg_lcp || 0}
                  type="time"
                />
              </div>
            </div>

            {/* Competitor Comparison */}
            {results.aggregated_metrics?.competitors && results.aggregated_metrics.competitors.length > 0 && (
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">
                  Competitor Performance Comparison
                </h3>

                <div className="mb-6">
                  <p className="text-lg text-gray-700">
                    Your site ranks <span className="font-bold text-primary-600">#{results.aggregated_metrics.comparisons?.rank || 'N/A'}</span> out of{' '}
                    <span className="font-bold">{results.aggregated_metrics.comparisons?.total_sites || 'N/A'}</span> analyzed sites.
                  </p>
                </div>

                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Website
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Performance Score
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          FCP (ms)
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          LCP (ms)
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {/* Main Site */}
                      <tr className="bg-blue-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                          Your Site
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                          {results.aggregated_metrics.main_site?.averages?.avg_performance_score?.toFixed(1) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                          {Math.round(results.aggregated_metrics.main_site?.averages?.avg_fcp || 0) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                          {Math.round(results.aggregated_metrics.main_site?.averages?.avg_lcp || 0) || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                            Main
                          </span>
                        </td>
                      </tr>

                      {/* Competitors */}
                      {results.aggregated_metrics.competitors.map((competitor: any, index: number) => {
                        const mainScore = results.aggregated_metrics.main_site?.averages?.avg_performance_score || 0
                        const compScore = competitor.averages?.avg_performance_score || 0
                        const status = compScore < mainScore ? 'Worse' : compScore > mainScore ? 'Better' : 'Equal'
                        const statusColor = status === 'Worse' ? 'bg-green-100 text-green-800' : status === 'Better' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'

                        return (
                          <tr key={index}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {competitor.url?.replace('https://', '').replace('http://', '').substring(0, 30) || `Competitor ${index + 1}`}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                              {competitor.averages?.avg_performance_score?.toFixed(1) || 'N/A'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                              {Math.round(competitor.averages?.avg_fcp || 0) || 'N/A'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                              {Math.round(competitor.averages?.avg_lcp || 0) || 'N/A'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColor}`}>
                                {status}
                              </span>
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>

                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">
                    <span className="font-semibold">Summary:</span> Your site performs{' '}
                    <span className="font-bold text-green-600">better</span> than{' '}
                    {results.aggregated_metrics.comparisons?.better_than?.length || 0} competitor(s) and{' '}
                    <span className="font-bold text-red-600">worse</span> than{' '}
                    {results.aggregated_metrics.comparisons?.worse_than?.length || 0} competitor(s).
                  </p>
                </div>
              </div>
            )}

            {/* Recommendations */}
            {results.recommendations && results.recommendations.length > 0 && (
              <div className="bg-white rounded-2xl shadow-2xl p-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6">
                  AI-Powered Recommendations for Your Website
                </h3>
                <RecommendationsList recommendations={results.recommendations} />
              </div>
            )}

            {/* Detailed Metrics */}
            <div className="bg-white rounded-2xl shadow-2xl p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                Detailed Metrics
              </h3>

              {/* Lighthouse Results */}
              {results.lighthouse_results && results.lighthouse_results.length > 0 && (
                <div className="mb-8">
                  <h4 className="text-xl font-semibold text-gray-800 mb-4">
                    Lighthouse Analysis
                  </h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Metric
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Value
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Rating
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {results.lighthouse_results[0]?.data?.metrics && (
                          <>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                First Contentful Paint
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {Math.round(results.lighthouse_results[0].data.metrics.fcp)}ms
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                  results.lighthouse_results[0].data.metrics.fcp < 1800
                                    ? 'bg-green-100 text-green-800'
                                    : results.lighthouse_results[0].data.metrics.fcp < 3000
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {results.lighthouse_results[0].data.metrics.fcp < 1800
                                    ? 'Good'
                                    : results.lighthouse_results[0].data.metrics.fcp < 3000
                                    ? 'Needs Improvement'
                                    : 'Poor'}
                                </span>
                              </td>
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                Largest Contentful Paint
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {Math.round(results.lighthouse_results[0].data.metrics.lcp)}ms
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                  results.lighthouse_results[0].data.metrics.lcp < 2500
                                    ? 'bg-green-100 text-green-800'
                                    : results.lighthouse_results[0].data.metrics.lcp < 4000
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {results.lighthouse_results[0].data.metrics.lcp < 2500
                                    ? 'Good'
                                    : results.lighthouse_results[0].data.metrics.lcp < 4000
                                    ? 'Needs Improvement'
                                    : 'Poor'}
                                </span>
                              </td>
                            </tr>
                            <tr>
                              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                Cumulative Layout Shift
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {results.lighthouse_results[0].data.metrics.cls.toFixed(3)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                                  results.lighthouse_results[0].data.metrics.cls < 0.1
                                    ? 'bg-green-100 text-green-800'
                                    : results.lighthouse_results[0].data.metrics.cls < 0.25
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : 'bg-red-100 text-red-800'
                                }`}>
                                  {results.lighthouse_results[0].data.metrics.cls < 0.1
                                    ? 'Good'
                                    : results.lighthouse_results[0].data.metrics.cls < 0.25
                                    ? 'Needs Improvement'
                                    : 'Poor'}
                                </span>
                              </td>
                            </tr>
                          </>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultsPage
