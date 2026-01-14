import React, { useState } from 'react'
import { screenStocksByAI } from '../services/api'

const AIScreeningPanel = ({ onResult, loading, setLoading }) => {
  // 状态管理
  const [query, setQuery] = useState('找出收盘价大于100元，成交量大于1000万的股票')
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  })
  const [market, setMarket] = useState('cn')
  const [exchange, setExchange] = useState('')
  const [exampleQueries, setExampleQueries] = useState([
    '找出最近30天收盘价持续上涨的股票',
    '找出成交量大于5000万，换手率大于5%的股票',
    '找出今天收盘价创历史新高的股票',
    '找出市盈率低于20，市净率低于1的股票',
    '找出最近一周涨幅超过10%的科技股'
  ])

  // 使用示例查询
  const useExampleQuery = (example) => {
    setQuery(example)
  }

  // 处理AI筛选
  const handleAIScreening = async () => {
    if (!query.trim()) {
      alert('请输入筛选条件')
      return
    }

    if (!dateRange.startDate || !dateRange.endDate) {
      alert('请选择日期范围')
      return
    }

    setLoading(true)
    try {
      const result = await screenStocksByAI({
        query: query,
        start_date: dateRange.startDate,
        end_date: dateRange.endDate,
        market: market,
        exchange: exchange
      })
      onResult(result)
    } catch (error) {
      console.error('AI筛选失败:', error)
      alert('AI筛选失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ai-screening-panel glass-effect">
      <h2>AI 自然语言筛选</h2>

      {/* 自然语言输入 */}
      <div className="query-section">
        <h3>输入筛选条件</h3>
        <textarea
          className="input query-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="请输入您的筛选条件，例如：找出收盘价大于100元，成交量大于1000万的股票"
          rows={4}
        ></textarea>
      </div>

      {/* 日期范围选择 */}
      <div className="date-range-section">
        <h3>日期范围（必填）</h3>
        <div className="date-inputs">
          <div className="date-input-group">
            <label>开始日期:</label>
            <input
              type="date"
              className="input"
              value={dateRange.startDate}
              onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
            />
          </div>
          <div className="date-input-group">
            <label>结束日期:</label>
            <input
              type="date"
              className="input"
              value={dateRange.endDate}
              onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
            />
          </div>
        </div>
      </div>

      {/* 市场和交易所选择 */}
      <div className="market-section">
        <h3>市场（必填）和交易所（可选）</h3>
        <div className="market-inputs">
          <div className="market-input-group">
            <label>市场:</label>
            <select
              className="input"
              value={market}
              onChange={(e) => setMarket(e.target.value)}
            >
              <option value="cn">中国A股</option>
              <option value="hk">香港港股</option>
              <option value="us">美国美股</option>
            </select>
          </div>
          <div className="market-input-group">
            <label>交易所:</label>
            <select
              className="input"
              value={exchange}
              onChange={(e) => setExchange(e.target.value)}
            >
              <option value="">全部</option>
              <option value="sh">上海交易所</option>
              <option value="sz">深圳交易所</option>
            </select>
          </div>
        </div>
      </div>

      {/* 示例查询 */}
      <div className="examples-section">
        <h3>示例查询</h3>
        <div className="examples-list">
          {exampleQueries.map((example, index) => (
            <button
              key={index}
              className="btn btn-secondary example-btn"
              onClick={() => useExampleQuery(example)}
            >
              {example}
            </button>
          ))}
        </div>
      </div>

      {/* 筛选按钮 */}
      <div className="screening-actions">
        <button
          className="btn btn-primary"
          onClick={handleAIScreening}
          disabled={loading}
        >
          {loading ? 'AI分析中...' : 'AI 智能筛选'}
        </button>
      </div>
    </div>
  )
}

export default AIScreeningPanel
