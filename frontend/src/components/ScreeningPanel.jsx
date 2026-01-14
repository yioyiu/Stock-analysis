import React, { useState } from 'react'
import { screenStocksByRule } from '../services/api'

const ScreeningPanel = ({ onResult, loading, setLoading }) => {
  // 状态管理
  const [rules, setRules] = useState([
    { indicator: 'close', operator: '>', value: 100 }
  ])
  const [dateRange, setDateRange] = useState({
    startDate: '',
    endDate: ''
  })
  const [market, setMarket] = useState('cn')
  const [exchange, setExchange] = useState('')

  // 指标选项
  const indicatorOptions = [
    { value: 'close', label: '收盘价' },
    { value: 'volume', label: '成交量' },
    { value: 'turnover', label: '换手率' },
    { value: 'high', label: '最高价' },
    { value: 'low', label: '最低价' },
    { value: 'open', label: '开盘价' }
  ]

  // 操作符选项
  const operatorOptions = [
    { value: '>', label: '>' },
    { value: '<', label: '<' },
    { value: '>=', label: '>=' },
    { value: '<=', label: '<=' },
    { value: '==', label: '==' }
  ]

  // 添加规则
  const addRule = () => {
    setRules([...rules, { indicator: 'close', operator: '>', value: 0 }])
  }

  // 删除规则
  const removeRule = (index) => {
    if (rules.length > 1) {
      const newRules = rules.filter((_, i) => i !== index)
      setRules(newRules)
    }
  }

  // 更新规则
  const updateRule = (index, field, value) => {
    const newRules = [...rules]
    newRules[index][field] = value
    setRules(newRules)
  }

  // 处理筛选
  const handleScreening = async () => {
    if (!dateRange.startDate || !dateRange.endDate) {
      alert('请选择日期范围')
      return
    }

    setLoading(true)
    try {
      const result = await screenStocksByRule({
        rules: rules,
        start_date: dateRange.startDate,
        end_date: dateRange.endDate,
        market: market,
        exchange: exchange
      })
      onResult(result)
    } catch (error) {
      console.error('筛选失败:', error)
      alert('筛选失败，请重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="screening-panel glass-effect">
      <h2>规则筛选</h2>

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

      {/* 筛选规则 */}
      <div className="rules-section">
        <div className="rules-header">
          <h3>筛选规则</h3>
          <button className="btn btn-secondary" onClick={addRule}>
            + 添加规则
          </button>
        </div>

        <div className="rules-list">
          {rules.map((rule, index) => (
            <div key={index} className="rule-item">
              <div className="rule-fields">
                {/* 指标选择 */}
                <select
                  className="input"
                  value={rule.indicator}
                  onChange={(e) => updateRule(index, 'indicator', e.target.value)}
                >
                  {indicatorOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>

                {/* 操作符选择 */}
                <select
                  className="input"
                  value={rule.operator}
                  onChange={(e) => updateRule(index, 'operator', e.target.value)}
                >
                  {operatorOptions.map(option => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>

                {/* 值输入 */}
                <input
                  type="number"
                  className="input"
                  value={rule.value}
                  onChange={(e) => updateRule(index, 'value', parseFloat(e.target.value) || 0)}
                  placeholder="输入数值"
                />
              </div>

              {/* 删除按钮 */}
              <button
                className="btn btn-secondary delete-rule-btn"
                onClick={() => removeRule(index)}
                disabled={rules.length === 1}
              >
                删除
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 筛选按钮 */}
      <div className="screening-actions">
        <button
          className="btn btn-primary"
          onClick={handleScreening}
          disabled={loading}
        >
          {loading ? '筛选中...' : '开始筛选'}
        </button>
      </div>
    </div>
  )
}

export default ScreeningPanel
