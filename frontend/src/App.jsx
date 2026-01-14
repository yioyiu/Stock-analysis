import React, { useState, useEffect } from 'react'
import Settings from './components/Settings'
import AIAgentCard from './components/AIAgentCard'
import Trader from './components/Trader'
import './App.css'

function App() {
  // 状态管理
  const [loading, setLoading] = useState(false)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [aiSettings, setAiSettings] = useState(null)

  // 加载AI设置
  useEffect(() => {
    const loadSettings = () => {
      const savedSettings = localStorage.getItem('aiSettings')
      if (savedSettings) {
        setAiSettings(JSON.parse(savedSettings))
      }
    }

    // 初始加载
    loadSettings()

    // 监听设置更新事件
    window.addEventListener('aiSettingsUpdated', loadSettings)

    return () => {
      window.removeEventListener('aiSettingsUpdated', loadSettings)
    }
  }, [])

  // 编辑AI设置
  const handleEditAI = () => {
    setSettingsOpen(true)
  }

  // 删除AI设置
  const handleDeleteAI = () => {
    if (window.confirm('确定要删除当前配置的AI智能体吗？')) {
      localStorage.removeItem('aiSettings')
      setAiSettings(null)
      window.dispatchEvent(new Event('aiSettingsUpdated'))
    }
  }

  return (
    <div className="app">
      {/* 头部 */}
      <header className="app-header glass-effect">
        <div className="header-content">
          <div>
            <h1>AI 分析系统</h1>
            <p>基于 AkShare 数据源 + AI 分析引擎的智能股票分析系统</p>
          </div>
          <div className="header-actions">
            <button
              className="btn btn-secondary settings-btn"
              onClick={() => setSettingsOpen(true)}
            >
              ⚙️ 设置
            </button>
          </div>
        </div>
      </header>

      {/* 设置模态框 */}
      <Settings
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />

      {/* AI智能体卡片 - 独立容器 */}
      <div className="ai-agent-container">
        <div className="container">
          <AIAgentCard
            aiSettings={aiSettings}
            onEdit={handleEditAI}
            onDelete={handleDeleteAI}
          />
        </div>
      </div>

      {/* 主要内容 - 仅AI交易员页面 */}
      <main>
        <Trader loading={loading} setLoading={setLoading} />
      </main>

      {/* 底部 */}
      <footer className="app-footer glass-effect">
        <p>AI 分析系统 © 2024</p>
      </footer>
    </div>
  )
}

export default App
