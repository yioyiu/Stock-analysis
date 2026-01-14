import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || window.location.origin + '/api/v1',
  timeout: 60000, // 增加超时时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 拦截器配置
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

// API 接口定义

// 获取股票历史数据
export const fetchStockHistory = async (symbol, params = {}) => {
  return apiClient.get(`/stock/history`, {
    params: {
      symbol,
      ...params
    }
  })
}

// 获取股票基本信息
export const fetchStockBasic = async (symbol) => {
  return apiClient.get(`/stock/basic`, {
    params: { symbol }
  })
}

// 获取股票代码列表
export const fetchStockSymbols = async (market = 'cn') => {
  return apiClient.get(`/stock/symbols`, {
    params: { market }
  })
}

// 规则筛选股票
export const screenStocksByRule = async (data) => {
  return apiClient.post(`/screening/rule`, data)
}

// 获取AI设置
const getAISettings = () => {
  const settings = localStorage.getItem('aiSettings')
  return settings ? JSON.parse(settings) : null
}

// 转换AI设置字段名
export const convertAISettingsToBackendFormat = (aiSettings) => {
  if (!aiSettings) return null

  return {
    api_key: aiSettings.openaiApiKey,
    base_url: aiSettings.apiBaseUrl,
    model_name: aiSettings.aiModelName,
    temperature: aiSettings.temperature
  }
}

// AI 筛选股票
export const screenStocksByAI = async (data) => {
  const aiSettings = getAISettings()
  const backendAISettings = convertAISettingsToBackendFormat(aiSettings)

  return apiClient.post(`/screening/ai`, {
    ...data,
    ai_config: backendAISettings
  })
}

// AI 分析股票
export const analyzeStockByAI = async (data, history_data = null) => {
  const aiSettings = getAISettings()
  const backendAISettings = convertAISettingsToBackendFormat(aiSettings)

  const body = {
    ...data,
    ai_config: backendAISettings
  }

  // 如果前端已经预取了历史数据，则一并传给后端以避免重复请求
  if (history_data) body.history_data = history_data

  return apiClient.post(`/ai/analyze`, body)
}

// AI 解释筛选结果
export const explainScreeningResult = async (result, query) => {
  const aiSettings = getAISettings()
  const backendAISettings = convertAISettingsToBackendFormat(aiSettings)

  return apiClient.post(`/ai/explain`, result, {
    params: {
      query,
      ...(backendAISettings ? { ai_config: JSON.stringify(backendAISettings) } : {})
    }
  })
}

// 测试AI模型连接
export const testAIConnection = async (aiSettings) => {
  // 将前端字段名转换为后端期望的格式
  const backendAISettings = convertAISettingsToBackendFormat(aiSettings)
  return apiClient.post(`/ai/test-connection`, backendAISettings)
}
