import React from 'react'

const AnalysisResult = ({ result }) => {
  return (
    <div className="analysis-result">
      <h3>AI 分析结果</h3>
      
      <div className="analysis-content">
        <div className="analysis-header">
          <div className="stock-info">
            <h4>{result.symbol} - {result.name}</h4>
            <p className="industry">{result.industry}</p>
            <div className="analysis-meta">
              <span className={`condition-status ${result.meets_conditions ? 'success' : 'failed'}`}>
                {result.meets_conditions ? '符合条件' : '不符合条件'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="analysis-body">
          <div className="analysis-reason">
            <h4>分析理由</h4>
            <p>{result.analysis_reason}</p>
          </div>
          
          <div className="risk-warning">
            <h4>风险提示</h4>
            <p>{result.risk_warning}</p>
          </div>
        </div>
      </div>
      
      <div className="analysis-footer">
        <button className="btn btn-secondary">
          导出分析报告
        </button>
        <button className="btn btn-secondary">
          保存到我的收藏
        </button>
      </div>
    </div>
  )
}

export default AnalysisResult
