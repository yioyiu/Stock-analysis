import React, { useState } from 'react'
import StockChart from './StockChart'
import { analyzeStockByAI, fetchStockHistory, fetchStockBasic } from '../services/api'
import ProgressModal from './ProgressModal'

const Trader = ({ loading, setLoading }) => {
  // 状态管理
  const [stockCode, setStockCode] = useState('')
  const [analysisResult, setAnalysisResult] = useState(null)
  const [cachedHistory, setCachedHistory] = useState(null)
  const [fetching, setFetching] = useState(false)
  const [fetchModalOpen, setFetchModalOpen] = useState(false)
  const [analyzeModalOpen, setAnalyzeModalOpen] = useState(false)
  const [fetchSteps, setFetchSteps] = useState([
    { title: '准备获取', detail: '', status: 'pending' },
    { title: '请求数据', detail: '', status: 'pending' },
    { title: '缓存数据', detail: '', status: 'pending' }
  ])
  const [analyzeSteps, setAnalyzeSteps] = useState([
    { title: '准备分析', detail: '', status: 'pending' },
    { title: '提取数据', detail: '', status: 'pending' },
    { title: '发送AI请求', detail: '', status: 'pending' },
    { title: '接收结果', detail: '', status: 'pending' }
  ])
  const [strategy, setStrategy] = useState({
    riskPreference: 'medium',
    trendSensitivity: 'high',
    bias: 'neutral'
  })
  // 市场选择状态
  const [market, setMarket] = useState('cn') // 默认A股
  const markets = [
    { value: 'cn', label: 'A股' },
    { value: 'us', label: '美股' },
    { value: 'hk', label: '港股' },
    { value: 'other', label: '其他市场' }
  ]

  // 处理股票分析
  const handleAnalyzeStock = async () => {
    if (!stockCode.trim()) {
      alert('请输入股票代码')
      return
    }

    // 检查AI设置是否已配置
    const aiSettings = localStorage.getItem('aiSettings')
    if (!aiSettings) {
      alert('错误：请先配置AI模型参数\n\n操作步骤：\n1. 点击设置按钮（齿轮图标）\n2. 填写完整的AI参数\n3. 保存配置后再尝试分析')
      return
    }

    // 验证AI配置是否完整
    const parsedAISettings = JSON.parse(aiSettings)

    // 验证API密钥
    if (!parsedAISettings.openaiApiKey || parsedAISettings.openaiApiKey.trim() === '') {
      alert('错误：API密钥未配置\n\n请在设置中填写有效的API密钥\n- OpenAI: 从 https://platform.openai.com/api-keys 获取\n- 智谱: 从 https://open.bigmodel.cn/apikeys 获取')
      return
    }

    // 验证API基础地址
    if (!parsedAISettings.apiBaseUrl || parsedAISettings.apiBaseUrl.trim() === '') {
      alert('错误：API基础地址未配置\n\n请在设置中填写有效的API基础地址\n- OpenAI: https://api.openai.com/v1\n- 智谱: https://open.bigmodel.cn/api/paas/v4')
      return
    }

    // 验证API基础地址格式
    try {
      new URL(parsedAISettings.apiBaseUrl)
    } catch (e) {
      alert(`错误：API基础地址格式无效 (${parsedAISettings.apiBaseUrl})\n\n请在设置中填写有效的URL格式，例如：\n- https://api.openai.com/v1\n- https://open.bigmodel.cn/api/paas/v4`)
      return
    }

    // 验证AI模型名称
    if (!parsedAISettings.aiModelName || parsedAISettings.aiModelName.trim() === '') {
      alert('错误：AI模型名称未配置\n\n请在设置中填写有效的AI模型名称\n- OpenAI推荐: gpt-3.5-turbo, gpt-4\n- 智谱推荐: glm-4-flash')
      return
    }

    // 使用与获取历史数据时相同的格式化逻辑
    let formattedSymbol = stockCode.trim()
    // 根据市场添加前缀
    if (market === 'hk' && !formattedSymbol.startsWith('hk')) {
      formattedSymbol = `hk${formattedSymbol}`
    } else if (market === 'us') {
      // 美股直接使用
      formattedSymbol = formattedSymbol
    }
    // A股不添加默认前缀，让后端处理不同市场情况

    // 检查cachedHistory中的股票代码是否与当前输入的股票代码匹配
    let historyData = cachedHistory
    const isCachedHistoryValid = historyData && historyData.symbol && historyData.symbol === formattedSymbol

    if (!historyData || !isCachedHistoryValid) {
      // 如果没有缓存历史数据，或者缓存的股票代码不匹配，就从localStorage中获取
      const cachedData = localStorage.getItem(`stock_history_${formattedSymbol}`)
      const cachedTimestamp = localStorage.getItem(`stock_history_${formattedSymbol}_timestamp`)

      if (cachedData) {
        // 检查缓存是否过期（超过7天）
        const isExpired = cachedTimestamp && (Date.now() - parseInt(cachedTimestamp) > 7 * 24 * 60 * 60 * 1000)
        if (isExpired) {
          alert('缓存数据已过期，请重新点击"开始获取"更新数据')
          return
        }

        // 使用localStorage中的缓存数据
        historyData = JSON.parse(cachedData)
        setCachedHistory(historyData)
        console.log('使用localStorage中的缓存数据进行分析，股票代码:', formattedSymbol)
      } else {
        alert('请先点击"开始获取"以获取并缓存股票历史数据，再开始分析')
        return
      }
    } else {
      console.log('使用状态中的缓存数据进行分析，股票代码:', formattedSymbol)
    }

    setLoading(true)
    setAnalysisResult(null) // 重置分析结果，避免旧数据影响
    try {
      console.log('开始分析股票:', formattedSymbol)
      console.log('市场:', market)
      console.log('策略配置:', {
        risk_preference: strategy.riskPreference,
        trend_sensitivity: strategy.trendSensitivity,
        bias: strategy.bias
      })
      console.log('原始缓存数据条数:', historyData.data.length)

      // 打开分析进度弹窗
      setAnalyzeModalOpen(true)
      setAnalyzeSteps(prev => prev.map((s, i) => ({ ...s, status: i === 0 ? 'in-progress' : 'pending' })))

      // 步骤1：准备分析数据
      await new Promise(resolve => setTimeout(resolve, 300))
      setAnalyzeSteps(prev => prev.map((s, i) => i === 0 ? { ...s, status: 'completed', detail: `准备分析 ${formattedSymbol}` } : s))

      // 步骤2：从全部缓存数据中提取最近365天的数据
      setAnalyzeSteps(prev => prev.map((s, i) => i === 1 ? { ...s, status: 'in-progress', detail: '从缓存数据中提取最近365天的数据' } : s))

      // 确保数据按日期排序（从旧到新）
      const sortedData = [...historyData.data].sort((a, b) => new Date(a.date) - new Date(b.date))

      // 计算365天前的日期
      const thirtySixFiveDaysAgo = new Date()
      thirtySixFiveDaysAgo.setDate(thirtySixFiveDaysAgo.getDate() - 365)

      // 提取最近365天的数据
      const recent365DaysData = sortedData.filter(item => new Date(item.date) >= thirtySixFiveDaysAgo)

      console.log('提取最近365天的数据条数:', recent365DaysData.length)

      // 步骤3：数据提取完成，准备发送AI请求
      await new Promise(resolve => setTimeout(resolve, 300))
      setAnalyzeSteps(prev => prev.map((s, i) => i === 1 ? { ...s, status: 'completed', detail: `成功提取 ${recent365DaysData.length} 条近365天数据` } : s))
      setAnalyzeSteps(prev => prev.map((s, i) => i === 2 ? { ...s, status: 'in-progress', detail: '发送AI请求，使用提取的365天数据' } : s))

      // 创建包含最近365天数据的新对象
      const recentHistoryData = {
        ...historyData,
        data: recent365DaysData
      }

      const result = await analyzeStockByAI({
        symbol: formattedSymbol,
        // 不需要再传递日期范围，直接使用处理后的最近365天数据
        strategy: {
          risk_preference: strategy.riskPreference,
          trend_sensitivity: strategy.trendSensitivity,
          bias: strategy.bias
        }
      }, recentHistoryData.data)

      // 更新进度
      await new Promise(resolve => setTimeout(resolve, 300))
      setAnalyzeSteps(prev => prev.map((s, i) => i === 2 ? { ...s, status: 'completed', detail: 'AI请求发送成功' } : s))
      setAnalyzeSteps(prev => prev.map((s, i) => i === 3 ? { ...s, status: 'in-progress', detail: '接收并处理AI分析结果' } : s))

      console.log('分析结果:', result)
      // 保存格式化后的symbol，用于StockChart组件
      // 确保result是有效的对象
      if (result && typeof result === 'object') {
        // 处理历史相似走势中的return字段，确保它有正确的别名
        if (result.historical_similar_patterns) {
          result.historical_similar_patterns = result.historical_similar_patterns.map(pattern => ({
            ...pattern,
            return_value: pattern['return'] !== undefined ? pattern['return'] : pattern.return_value
          }))
        }

        // 获取股票基本信息
        let stockName = ''
        try {
          const basicInfo = await fetchStockBasic(formattedSymbol)
          if (basicInfo && basicInfo.name) {
            stockName = basicInfo.name
          }
        } catch (err) {
          console.error('获取股票基本信息失败:', err)
        }

        setAnalysisResult({
          ...result,
          formattedSymbol: formattedSymbol,
          stockName: stockName
        })

        // 更新进度为完成
        await new Promise(resolve => setTimeout(resolve, 300))
        setAnalyzeSteps(prev => prev.map((s, i) => ({ ...s, status: 'completed', detail: '分析完成' })))
      } else {
        throw new Error('分析结果无效')
      }
    } catch (error) {
      console.error('股票分析失败:', error)
      console.error('错误详情:', JSON.stringify(error, null, 2))

      // 构建详细的错误信息
      let errorInfo = '股票分析失败: '
      let errorStep = 2 // 默认是AI请求步骤出错
      let errorDetail = ''

      // 确定错误发生的步骤
      if (error.response) {
        // 服务器返回了错误响应
        const status = error.response.status
        const data = error.response.data

        if (data && data.detail) {
          errorInfo += data.detail
          errorDetail = data.detail

          // 根据错误信息确定错误步骤
          if (data.detail.includes('API密钥') || data.detail.includes('配置')) {
            errorStep = 0 // 准备分析步骤（配置问题）
          } else if (data.detail.includes('股票') || data.detail.includes('数据')) {
            errorStep = 1 // 提取数据步骤（数据问题）
          } else {
            errorStep = 2 // AI请求步骤
          }
        } else if (data && data.logic) {
          // 如果服务器返回了详细的错误逻辑
          errorInfo += data.logic
          errorDetail = data.logic
        } else {
          // 其他服务器错误
          errorInfo += `${status} - ${data.detail || data.message || '未知错误'}`
          errorDetail = `${status} - ${data.detail || data.message || '未知错误'}`
        }
      } else if (error.request) {
        // 请求已发送但没有收到响应
        errorInfo += '服务器无响应，请检查网络连接或稍后重试'
        errorDetail = '服务器无响应，请检查网络连接或稍后重试'
      } else if (error.code === 'ECONNABORTED') {
        // 请求超时
        errorInfo += '请求超时，请检查网络连接或稍后重试'
        errorDetail = '请求超时，请检查网络连接或稍后重试'
      } else {
        // 请求配置时发生错误
        errorInfo += error.message
        errorDetail = error.message
        errorStep = 0 // 配置问题
      }

      // 更新进度为失败，标记具体哪个步骤出错
      setAnalyzeSteps(prev => prev.map((s, i) => {
        if (i === errorStep) {
          return { ...s, status: 'failed', detail: errorDetail }
        } else if (i < errorStep) {
          return { ...s, status: 'completed' }
        } else {
          return { ...s, status: 'pending' }
        }
      }))

      // 显示详细的错误信息
      alert(errorInfo)
    } finally {
      setLoading(false)
      // 延长弹窗显示时间，让用户有足够时间查看进度
      setTimeout(() => setAnalyzeModalOpen(false), 1500)
    }
  }

  // 开始获取并缓存历史数据
  const handleFetchHistory = async () => {
    if (!stockCode.trim()) {
      alert('请输入股票代码'); return
    }

    setFetchModalOpen(true)
    setFetching(true)
    setFetchSteps(prev => prev.map((s, i) => ({ ...s, status: i === 0 ? 'in-progress' : 'pending' })))

    try {
      let formattedSymbol = stockCode.trim()

      // 根据市场添加前缀
      if (market === 'hk' && !formattedSymbol.startsWith('hk')) {
        formattedSymbol = `hk${formattedSymbol}`
      } else if (market === 'us') {
        // 美股直接使用
        formattedSymbol = formattedSymbol
      }
      // A股不添加默认前缀，让后端处理不同市场情况

      console.log('获取历史数据，股票代码:', formattedSymbol, '市场:', market)

      // 获取全部历史数据（不指定start_date，由后端处理）
      const endDate = new Date().toISOString().split('T')[0]

      setFetchSteps(prev => prev.map((s, i) => i === 0 ? { ...s, status: 'completed', detail: `准备获取 ${formattedSymbol} 的全部历史数据` } : s))
      setFetchSteps(prev => prev.map((s, i) => i === 1 ? { ...s, status: 'in-progress', detail: `请求 /stock/history，结束日期：${endDate}` } : s))

      // 获取全部历史数据，不指定开始日期
      const data = await fetchStockHistory(formattedSymbol, {
        end_date: endDate
        // 不指定start_date，让后端返回全部可用数据
      })

      // data 的结构预期为 { data: [...] }
      setFetchSteps(prev => prev.map((s, i) => i === 1 ? { ...s, status: 'completed', detail: '数据获取成功' } : s))
      setFetchSteps(prev => prev.map((s, i) => i === 2 ? { ...s, status: 'in-progress', detail: `获取到 ${data?.data?.length || 0} 条数据，正在缓存` } : s))

      // 将数据缓存到状态中
      setCachedHistory(data)

      // 同时将数据缓存到localStorage中，持久化存储
      localStorage.setItem(`stock_history_${formattedSymbol}`, JSON.stringify(data))
      localStorage.setItem(`stock_history_${formattedSymbol}_timestamp`, Date.now().toString())

      setFetchSteps(prev => prev.map((s, i) => ({ ...s, status: 'completed' })))
    } catch (err) {
      console.error('获取历史数据失败', err)

      // 构建详细的错误信息
      let errorInfo = '获取历史数据失败: '
      let errorDetail = err.message || String(err)

      if (err.response) {
        // 服务器返回了错误响应
        const status = err.response.status
        const data = err.response.data
        errorInfo += `${status} - ${data.detail || data.message || '未知错误'}`
        errorDetail = `${status} - ${data.detail || data.message || '未知错误'}`
      } else if (err.request) {
        // 请求已发送但没有收到响应
        errorInfo += '服务器无响应，请检查网络连接或稍后重试'
        errorDetail = '服务器无响应，请检查网络连接或稍后重试'
      } else if (err.code === 'ECONNABORTED') {
        // 请求超时
        errorInfo += '请求超时，请检查网络连接或稍后重试'
        errorDetail = '请求超时，请检查网络连接或稍后重试'
      } else {
        // 其他错误
        errorInfo += err.message || String(err)
        errorDetail = err.message || String(err)
      }

      // 更新进度为失败，标记具体哪个步骤出错
      setFetchSteps(prev => prev.map((s, i) => {
        if (i === 1) {
          return { ...s, status: 'failed', detail: errorDetail }
        } else if (i < 1) {
          return { ...s, status: 'completed' }
        } else {
          return { ...s, status: 'pending' }
        }
      }))

      // 显示详细的错误信息
      alert(errorInfo)
    } finally {
      setFetching(false)
      // 延长弹窗显示时间，让用户有足够时间查看进度
      setTimeout(() => setFetchModalOpen(false), 1500)
    }
  }

  return (
    <div className="trader-container">


      {/* 分析设置 */}
      <div className="strategy-config glass-effect">
        <h3>分析设置</h3>
        <div className="strategy-fields">
          <div className="input-group">
            <label>市场选择:</label>
            <select
              className="input"
              value={market}
              onChange={(e) => setMarket(e.target.value)}
            >
              {markets.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
          <div className="input-group">
            <label>股票代码:</label>
            <input
              type="text"
              className="input"
              value={stockCode}
              onChange={(e) => setStockCode(e.target.value)}
              placeholder={
                market === 'cn' ? '请输入股票代码，例如：000001' :
                  market === 'us' ? '请输入股票代码，例如：AAPL' :
                    market === 'hk' ? '请输入股票代码，例如：00700' :
                      '请输入股票代码'
              }
              autoComplete="off"
            />
          </div>
          <div className="input-group">
            <label>风险偏好:</label>
            <select
              className="input"
              value={strategy.riskPreference}
              onChange={(e) => setStrategy({ ...strategy, riskPreference: e.target.value })}
            >
              <option value="low">低风险</option>
              <option value="medium">中风险</option>
              <option value="high">高风险</option>
            </select>
          </div>
          <div className="input-group">
            <label>趋势敏感度:</label>
            <select
              className="input"
              value={strategy.trendSensitivity}
              onChange={(e) => setStrategy({ ...strategy, trendSensitivity: e.target.value })}
            >
              <option value="low">低敏感度</option>
              <option value="medium">中敏感度</option>
              <option value="high">高敏感度</option>
            </select>
          </div>
          <div className="input-group">
            <label>多空偏好:</label>
            <select
              className="input"
              value={strategy.bias}
              onChange={(e) => setStrategy({ ...strategy, bias: e.target.value })}
            >
              <option value="neutral">中性</option>
              <option value="long">多头偏好</option>
              <option value="short">空头偏好</option>
            </select>
          </div>
          <button
            className="btn btn-primary analyze-btn"
            onClick={handleFetchHistory}
            disabled={fetching || loading}
            style={{ marginRight: '8px' }}
          >
            {fetching ? '获取中...' : '开始获取'}
          </button>
          <button
            className="btn btn-primary analyze-btn"
            onClick={handleAnalyzeStock}
            disabled={loading || fetching}
          >
            {loading ? '分析中...' : '开始分析'}
          </button>
          {cachedHistory && cachedHistory.data && (
            <div style={{ marginTop: '8px', fontSize: '12px', color: '#999' }}>已缓存: {cachedHistory.data.length} 条</div>
          )}
        </div>
      </div>



      {/* 进度弹窗 - 移到条件渲染外部，确保始终可见 */}
      <ProgressModal isOpen={fetchModalOpen} title="获取历史数据" steps={fetchSteps} />
      <ProgressModal isOpen={analyzeModalOpen} title="AI 分析进度" steps={analyzeSteps} />

      {/* 分析结果展示 */}
      {analysisResult && (
        <div className="analysis-results">
          {/* 顶部：分析概览 */}
          <div className="analysis-overview glass-effect">
            <div className="trend-indicator">
              {/* 在趋势判断div内添加股票名称和代码标题 */}
              <h2 className="stock-title">
                {analysisResult.stockName && analysisResult.stockName !== 'Unknown' ? `${analysisResult.stockName} (${analysisResult.formattedSymbol || stockCode})` : analysisResult.formattedSymbol || stockCode}
              </h2>
              <h3>趋势判断</h3>
              <div className={`trend-badge ${analysisResult.trend ? analysisResult.trend.toLowerCase() : 'neutral'}`}>
                {analysisResult.trend || '暂无数据'}
              </div>
              <div className="confidence">
                置信度: {analysisResult.confidence ? (analysisResult.confidence * 100).toFixed(1) : '0.0'}%
              </div>
            </div>
            <div className="analysis-logic">
              <h3>分析逻辑</h3>
              <p>{analysisResult.logic || '暂无分析逻辑'}</p>
              <div className="support-level">
                近期支撑区间: {analysisResult.support_level || '暂无数据'}
              </div>
              <div className="resistance-level">
                近期压力区间: {analysisResult.resistance_level || '暂无数据'}
              </div>
            </div>
          </div>

          {/* 中部：可视化图表 */}
          <div className="chart-section glass-effect">
            <h3>股票数据可视化</h3>
            <StockChart
              stock={{
                symbol: analysisResult.formattedSymbol || stockCode,
                name: ''
              }}
              onAnalysis={() => { }}
              analysisResult={analysisResult}
            />
          </div>

          {/* 底部：详细分析和历史相似走势 */}
          <div className="detailed-analysis">
            {/* 详细分析 */}
            <div className="detail-section glass-effect">
              <h3>详细分析</h3>
              {analysisResult.detailed_analysis && Object.keys(analysisResult.detailed_analysis).length > 0 ? (
                <div className="analysis-details">
                  <div className="detail-item">
                    <h4>价格走势分析</h4>
                    <p>{analysisResult.detailed_analysis.price_analysis || '暂无数据'}</p>
                  </div>
                  <div className="detail-item">
                    <h4>成交量分析</h4>
                    <p>{analysisResult.detailed_analysis.volume_analysis || '暂无数据'}</p>
                  </div>
                  <div className="detail-item">
                    <h4>换手率分析</h4>
                    <p>{analysisResult.detailed_analysis.turnover_analysis || '暂无数据'}</p>
                  </div>
                  <div className="detail-item">
                    <h4>K线形态分析</h4>
                    <p>{analysisResult.detailed_analysis.kline_pattern_analysis || '暂无数据'}</p>
                  </div>
                </div>
              ) : (
                <p>暂无详细分析数据</p>
              )}
            </div>

            {/* 历史相似走势 */}
            <div className="similar-patterns glass-effect">
              <h3>历史相似走势</h3>
              {analysisResult.historical_similar_patterns && analysisResult.historical_similar_patterns.length > 0 ? (
                <div className="patterns-list">
                  {analysisResult.historical_similar_patterns.map((pattern, index) => (
                    <div key={index} className="pattern-item">
                      <div className="pattern-header">
                        <div className="pattern-date">
                          {pattern.pattern_date || '暂无日期'}
                        </div>
                        <div className={`pattern-result ${pattern.result ? pattern.result.toLowerCase() : 'neutral'}`}>
                          {pattern.result || '暂无结果'}
                        </div>
                        <div className={`pattern-return ${(pattern.return || 0) >= 0 ? 'positive' : 'negative'}`}>
                          涨跌幅: {((pattern.return || 0) * 100).toFixed(1)}%
                        </div>
                        <div className="pattern-similarity">
                          相似度: {((pattern.similarity || 0) * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div className="pattern-kline-segment">
                        <h4>K线片段描述:</h4>
                        <p>{pattern.kline_segment || '暂无描述'}</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p>暂无历史相似走势数据</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Trader
