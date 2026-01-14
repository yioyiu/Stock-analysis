import React, { useState, useEffect } from 'react'

const Settings = ({ isOpen, onClose }) => {
  // 状态管理
  const [settings, setSettings] = useState({
    openaiApiKey: '',
    apiBaseUrl: 'https://api.openai.com/v1',
    aiModelName: 'gpt-3.5-turbo',
    temperature: 0.1
  })

  // 从localStorage加载设置
  useEffect(() => {
    const savedSettings = localStorage.getItem('aiSettings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }
  }, [])

  // 保存设置到localStorage
  const handleSave = () => {
    localStorage.setItem('aiSettings', JSON.stringify(settings))
    onClose()
    // 触发设置更新事件
    window.dispatchEvent(new Event('aiSettingsUpdated'))
  }

  // 处理输入变化
  const handleChange = (e) => {
    const { name, value } = e.target
    setSettings(prev => ({
      ...prev,
      [name]: name === 'temperature' ? parseFloat(value) || 0 : value
    }))
  }

  if (!isOpen) return null

  return (
    <div className="settings-modal-overlay">
      <div className="settings-modal glass-effect">
        <div className="settings-header">
          <h2>AI 模型设置</h2>
          <button className="btn btn-secondary close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="settings-content">
          {/* 核心设置区域 */}
          <div className="settings-core">
            {/* API Key 设置 */}
            <div className="setting-item">
              <label htmlFor="openaiApiKey">API 密钥</label>
              <input
                type="password"
                id="openaiApiKey"
                name="openaiApiKey"
                className="input"
                value={settings.openaiApiKey}
                onChange={handleChange}
                placeholder="请输入 OpenAI/智谱 API 密钥"
              />
              <p className="setting-hint">用于访问 AI 模型的 API 密钥</p>
            </div>

            {/* API 基础地址 */}
            <div className="setting-item">
              <label htmlFor="apiBaseUrl">API 基础地址</label>
              <input
                type="text"
                id="apiBaseUrl"
                name="apiBaseUrl"
                className="input"
                value={settings.apiBaseUrl}
                onChange={handleChange}
                placeholder="例如: https://api.openai.com/v1 或 https://open.bigmodel.cn/api/paas/v4"
              />
              <p className="setting-hint">OpenAI: https://api.openai.com/v1 | 智谱: https://open.bigmodel.cn/api/paas/v4</p>
            </div>

            {/* AI 模型名称 */}
            <div className="setting-item">
              <label htmlFor="aiModelName">AI 模型名称</label>
              <input
                type="text"
                id="aiModelName"
                name="aiModelName"
                className="input"
                value={settings.aiModelName}
                onChange={handleChange}
                placeholder="例如: gpt-3.5-turbo 或 glm-4-flash"
              />
              <p className="setting-hint">智谱推荐模型: glm-4-flash</p>
            </div>

            {/* 温度参数 */}
            <div className="setting-item">
              <label htmlFor="temperature">温度参数</label>
              <input
                type="number"
                id="temperature"
                name="temperature"
                className="input"
                value={settings.temperature}
                onChange={handleChange}
                min="0"
                max="2"
                step="0.1"
                placeholder="0.1-2.0"
              />
              <p className="setting-hint">控制输出的随机性，值越高越随机，推荐 0.1-0.5</p>
            </div>
          </div>

          {/* 设置示例区域 */}
          <div className="settings-extra">
            {/* 智谱模型配置示例 */}
            <div className="settings-example">
              <h3>智谱 GLM-4.5-Flash 配置示例</h3>
              <div className="example-content">
                <p><strong>API 密钥:</strong> sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx</p>
                <p><strong>API 基础地址:</strong> https://open.bigmodel.cn/api/paas/v4</p>
                <p><strong>AI 模型名称:</strong> glm-4-flash</p>
                <p><strong>温度参数:</strong> 0.1</p>
              </div>
            </div>
          </div>
        </div>

        <div className="settings-actions">
          <button
            className="btn delete-ai-btn"
            onClick={() => {
              if (window.confirm('确定要删除当前配置的AI智能体吗？')) {
                localStorage.removeItem('aiSettings')
                onClose()
                window.dispatchEvent(new Event('aiSettingsUpdated'))
              }
            }}
          >
            🗑️ 删除 AI 智能体
          </button>
          <button className="btn btn-secondary" onClick={onClose}>
            取消
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            保存设置
          </button>
        </div>
      </div>
    </div>
  )
}

export default Settings
