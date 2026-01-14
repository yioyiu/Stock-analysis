import React from 'react'

const StockList = ({ stocks, onSelect, selectedStock }) => {
  return (
    <div className="stock-list">
      <h3>股票列表</h3>
      <div className="stock-list-content">
        {stocks.length === 0 ? (
          <div className="no-stocks">
            <p>没有找到符合条件的股票</p>
          </div>
        ) : (
          stocks.map((stock, index) => (
            <div
              key={`${stock.symbol}-${index}`}
              className={`stock-item ${selectedStock?.symbol === stock.symbol ? 'selected' : ''}`}
              onClick={() => onSelect(stock)}
            >
              <div className="stock-info">
                <div className="stock-symbol">{stock.symbol}</div>
                <div className="stock-name">{stock.name}</div>
              </div>
              <div className="stock-meta">
                <div className="stock-industry">{stock.industry}</div>
                <div className="stock-market">{stock.market}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default StockList
