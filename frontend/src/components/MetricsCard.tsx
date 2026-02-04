import React from 'react'

interface MetricsCardProps {
  title: string
  value: number
  type: 'score' | 'time'
}

const MetricsCard: React.FC<MetricsCardProps> = ({ title, value, type }) => {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600'
    if (score >= 75) return 'text-yellow-600'
    if (score >= 50) return 'text-orange-600'
    return 'text-red-600'
  }

  const getTimeColor = (time: number) => {
    if (time < 2000) return 'text-green-600'
    if (time < 3500) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatValue = () => {
    if (type === 'score') {
      return `${Math.round(value)}/100`
    }
    return `${Math.round(value)}ms`
  }

  const getColor = () => {
    if (type === 'score') return getScoreColor(value)
    return getTimeColor(value)
  }

  return (
    <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-6 border border-gray-200">
      <h4 className="text-sm font-medium text-gray-600 mb-2">{title}</h4>
      <p className={`text-4xl font-bold ${getColor()}`}>
        {formatValue()}
      </p>
      <div className="mt-3 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${
            type === 'score'
              ? value >= 90
                ? 'bg-green-500'
                : value >= 75
                ? 'bg-yellow-500'
                : value >= 50
                ? 'bg-orange-500'
                : 'bg-red-500'
              : value < 2000
              ? 'bg-green-500'
              : value < 3500
              ? 'bg-yellow-500'
              : 'bg-red-500'
          }`}
          style={{
            width: type === 'score' ? `${value}%` : '100%'
          }}
        />
      </div>
    </div>
  )
}

export default MetricsCard
