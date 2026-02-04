import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface AnalysisRequest {
  mainUrl: string
  competitors: string[]
}

export interface AnalysisStatus {
  job_id: string
  status: string
  progress: number
  current_step: string
  results?: any
  error?: string
}

export interface AnalysisResults {
  job_id: string
  main_url: string
  lighthouse_results: any[]
  screenshots: any[]
  aggregated_metrics: any
  recommendations: any[]
  errors: string[]
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const performanceApi = {
  // Start a new analysis
  startAnalysis: async (data: AnalysisRequest): Promise<AnalysisStatus> => {
    const response = await api.post('/api/analyze', data)
    return response.data
  },

  // Get analysis status
  getStatus: async (jobId: string): Promise<AnalysisStatus> => {
    const response = await api.get(`/api/status/${jobId}`)
    return response.data
  },

  // Get complete results
  getResults: async (jobId: string): Promise<AnalysisResults> => {
    const response = await api.get(`/api/results/${jobId}`)
    return response.data
  },

  // Download PDF report
  downloadReport: async (jobId: string): Promise<Blob> => {
    const response = await api.get(`/api/download/${jobId}`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Health check
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/health')
    return response.data
  }
}

export default api
