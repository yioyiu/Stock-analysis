import React, { useState, useEffect } from 'react'
import { testAIConnection } from '../services/api'

const AIAgentCard = ({ aiSettings, onEdit }) => {
  if (!aiSettings) return null

  const [isEnabled, setIsEnabled] = useState(true)
  const [connectionStatus, setConnectionStatus] = useState({ connected: false, message: '' })
  const [testing, setTesting] = useState(false)

  // 测试AI模型连接
  const testConnection = async () => {
    setTesting(true)
    try {
      // 检查AI设置是否完整
      if (!aiSettings.openaiApiKey || !aiSettings.apiBaseUrl || !aiSettings.aiModelName) {
        setConnectionStatus({
          connected: false,
          message: '连接测试失败：AI设置不完整'
        })
        return
      }

      const result = await testAIConnection(aiSettings)
      setConnectionStatus({
        connected: result.success,
        message: result.message
      })
    } catch (error) {
      let errorMessage = '连接测试失败：网络错误或服务器问题'

      // 处理不同类型的错误
      if (error.response) {
        // 服务器返回了错误响应
        if (error.response.data) {
          if (error.response.data.detail) {
            errorMessage = error.response.data.detail
          } else if (error.response.data.message) {
            errorMessage = error.response.data.message
          }
        }
      } else if (error.request) {
        // 请求已发送但没有收到响应
        errorMessage = '连接测试失败：服务器无响应，请检查网络连接'
      } else {
        // 请求配置时发生错误
        errorMessage = `连接测试失败：${error.message}`
      }

      setConnectionStatus({
        connected: false,
        message: errorMessage
      })
    } finally {
      setTesting(false)
    }
  }

  // 初始化时测试连接
  useEffect(() => {
    testConnection()
  }, [aiSettings])

  // 切换AI智能体启用状态
  const toggleEnabled = () => {
    const newIsEnabled = !isEnabled
    setIsEnabled(newIsEnabled)

    // 如果从关闭到开启，进行连接测试
    if (newIsEnabled) {
      testConnection()
      window.dispatchEvent(new Event('aiAgentEnabled'))
    } else {
      window.dispatchEvent(new Event('aiAgentDisabled'))
    }
  }

  // 点击卡片处理
  const handleCardClick = () => {
    // 点击卡片弹出编辑窗口
    onEdit()
  }

  return (
    <div className="ai-agent-card glass-effect">
      <div
        className="ai-agent-content"
        onClick={handleCardClick}
      >
        <div className="ai-agent-main-info">
          <div className="ai-agent-basic">
            <div className="ai-agent-icon">🤖</div>
            <div>
              <h3>{aiSettings.aiModelName}</h3>
              <div className="ai-agent-status">
                <div className={`status-indicator ${connectionStatus.connected && isEnabled ? 'online' : connectionStatus.connected ? 'idle' : 'offline'}`}></div>
                <span className="status-text">
                  {testing ? '测试连接中...' :
                    connectionStatus.connected ? (isEnabled ? '已连接' : '连接正常(已禁用)') :
                      '连接失败'}
                </span>
              </div>
            </div>
          </div>

          {/* 开关滑块 */}
          <div className="ai-agent-toggle">
            <label className="toggle-switch" onClick={(e) => e.stopPropagation()}> {/* 防止触发卡片点击 */}
              <input
                type="checkbox"
                checked={isEnabled}
                onChange={toggleEnabled}
                onClick={(e) => e.stopPropagation()} // 防止触发卡片点击
              />
              <span className="toggle-slider"></span>
            </label>
            <span className="toggle-label" onClick={(e) => e.stopPropagation()}> {/* 防止触发卡片点击 */}
              {isEnabled ? '开启' : '关闭'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIAgentCard
