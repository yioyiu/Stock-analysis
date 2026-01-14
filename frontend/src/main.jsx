import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// 确保DOM元素存在
const rootElement = document.getElementById('root')
if (!rootElement) {
  console.error('根元素不存在，无法渲染React应用')
} else {
  // 标准的 ErrorBoundary 类组件，能捕获子组件渲染/生命周期错误
  class ErrorBoundary extends React.Component {
    constructor(props) {
      super(props)
      this.state = { hasError: false, error: null, errorInfo: null }
    }

    static getDerivedStateFromError(error) {
      return { hasError: true }
    }

    componentDidCatch(error, errorInfo) {
      console.error('捕获到渲染错误:', error, errorInfo)
      this.setState({ error, errorInfo })
      // 这里可以上报到后端或上报工具
    }

    render() {
      if (this.state.hasError) {
        return (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            backgroundColor: '#667eea',
            color: '#ffffff',
            padding: '20px',
            textAlign: 'center'
          }}>
            <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>应用出现错误</h1>
            <p style={{ fontSize: '1rem', marginBottom: '1rem' }}>{this.state.error?.toString() || '未知错误'}</p>
            <details style={{ color: '#fff', maxWidth: '800px', textAlign: 'left' }}>
              <summary>错误详情（展开查看）</summary>
              <pre style={{ whiteSpace: 'pre-wrap' }}>{this.state.errorInfo?.componentStack}</pre>
            </details>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '10px 20px',
                fontSize: '1rem',
                backgroundColor: '#ffffff',
                color: '#667eea',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                marginTop: '16px'
              }}
            >
              刷新页面
            </button>
          </div>
        )
      }
      return this.props.children
    }
  }

  // 全局未处理 Promise 拒绝处理，避免沉默失败
  window.addEventListener('unhandledrejection', (event) => {
    console.error('未处理的 Promise 拒绝:', event.reason)
  })

  // 渲染应用
  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>
  )
}
