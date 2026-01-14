import React from 'react'

const ProgressModal = ({ isOpen, title, steps }) => {
    if (!isOpen) return null

    return (
        <div className="progress-modal-overlay">
            <div className="progress-modal">
                <h3>{title}</h3>
                <div className="progress-steps">
                    {steps.map((s, idx) => (
                        <div key={idx} className="progress-step">
                            <div className={`step-index ${s.status}`}>{idx + 1}</div>
                            <div className="step-body">
                                <div className="step-title">{s.title}</div>
                                <div className="step-detail">{s.detail}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <style>{`
        .progress-modal-overlay{
          position:fixed;left:0;top:0;right:0;bottom:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;z-index:1000;
        }
        .progress-modal{background:#fff;color:#333;padding:20px;border-radius:8px;width:420px;box-shadow:0 8px 24px rgba(0,0,0,0.2)}
        .progress-modal h3{margin:0 0 12px 0}
        .progress-step{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #eee}
        .step-index{width:28px;height:28px;border-radius:14px;display:flex;align-items:center;justify-content:center;background:#ddd;color:#fff}
        .step-index.completed{background:#4caf50}
        .step-index.in-progress{background:#2196f3}
        .step-body .step-title{font-weight:600}
        .step-detail{font-size:12px;color:#666}
      `}</style>
        </div>
    )
}

export default ProgressModal
