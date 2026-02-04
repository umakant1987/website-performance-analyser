import React from 'react'

interface ProgressBarProps {
  progress: number
}

const ProgressBar: React.FC<ProgressBarProps> = ({ progress }) => {
  return (
    <div className="w-full">
      <div className="flex justify-between mb-2">
        <span className="text-sm font-medium text-gray-700">Progress</span>
        <span className="text-sm font-medium text-gray-700">{progress}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className="bg-gradient-to-r from-primary-600 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}

export default ProgressBar
