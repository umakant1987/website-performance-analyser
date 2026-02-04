import React from 'react'
import {
  ExclamationTriangleIcon,
  InformationCircleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

interface Recommendation {
  priority: 'high' | 'medium' | 'low'
  category: string
  title: string
  description: string
  impact?: string
}

interface RecommendationsListProps {
  recommendations: Recommendation[]
}

const RecommendationsList: React.FC<RecommendationsListProps> = ({ recommendations }) => {
  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />
      case 'medium':
        return <InformationCircleIcon className="h-6 w-6 text-yellow-500" />
      case 'low':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />
      default:
        return <InformationCircleIcon className="h-6 w-6 text-gray-500" />
    }
  }

  const getPriorityBadge = (priority: string) => {
    const colors = {
      high: 'bg-red-100 text-red-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    }

    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${colors[priority as keyof typeof colors]}`}>
        {priority.toUpperCase()}
      </span>
    )
  }

  return (
    <div className="space-y-4">
      {recommendations.map((rec, index) => (
        <div
          key={index}
          className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              {getPriorityIcon(rec.priority)}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h4 className="text-lg font-semibold text-gray-900">
                  {rec.title}
                </h4>
                {getPriorityBadge(rec.priority)}
              </div>
              <p className="text-sm text-gray-600 mb-1">
                <span className="font-medium">Category:</span> {rec.category}
              </p>
              <p className="text-gray-700 mb-3">
                {rec.description}
              </p>
              {rec.impact && (
                <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded">
                  <p className="text-sm text-blue-800">
                    <span className="font-semibold">Expected Impact:</span> {rec.impact}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default RecommendationsList
