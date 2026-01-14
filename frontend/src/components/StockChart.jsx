import React, { useEffect, useState, useRef } from 'react'
import * as echarts from 'echarts'
import { fetchStockHistory } from '../services/api'

const StockChart = ({ stock, onAnalysis, analysisResult }) => {
  const [stockData, setStockData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  // 图表实例引用
  const chartInstanceRef = useRef(null)
  // 图表容器引用
  const chartContainerRef = useRef(null)

  // 加载股票数据
  const loadStockData = async (symbol) => {
    if (!symbol) return

    setLoading(true)
    setError(null)
    try {
      console.log('开始加载股票数据:', symbol)
      const data = await fetchStockHistory(symbol)
      console.log('获取到股票数据:', data)
      setStockData(data)
    } catch (err) {
      setError('加载股票数据失败')
      console.error('加载股票数据失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 当stock.symbol变化时，重新加载数据
  useEffect(() => {
    if (stock && stock.symbol) {
      loadStockData(stock.symbol)
    }
  }, [stock?.symbol])

  // 获取复权类型的中文名称
  const getAdjustName = () => {
    if (!stockData) return '前复权'
    const adjust = stockData.adjust || 'qfq'
    const adjustMap = {
      'qfq': '前复权',
      'hfq': '后复权',
      '': '不复权'
    }
    return adjustMap[adjust] || adjust
  }

  // 生成图表配置
  const generateChartOption = () => {
    if (!stockData || !stockData.data || stockData.data.length === 0) {
      return {
        backgroundColor: 'transparent',
        title: {
          text: '无可用图表数据',
          left: 'center',
          top: 'center',
          textStyle: {
            color: '#ffffff',
            fontSize: 16
          }
        }
      }
    }

    // 准备K线数据，注意ECharts K线数据格式：[开盘, 收盘, 最低, 最高]
    const klineData = stockData.data.map(item => {
      // 确保所有值都是有效的数字，如果不是则使用默认值
      return [
        Number.isFinite(Number(item.open)) ? Number(item.open) : Number(item.close),
        Number.isFinite(Number(item.close)) ? Number(item.close) : 0,
        Number.isFinite(Number(item.low)) ? Number(item.low) : 0,
        Number.isFinite(Number(item.high)) ? Number(item.high) : 0
      ];
    })

    // 准备日期数据
    const dates = stockData.data.map(item => item.date)

    // 准备成交量数据
    const volumeData = stockData.data.map(item => {
      const open = Number(item.open)
      const close = Number(item.close)
      const volume = Number.isFinite(Number(item.volume)) ? Number(item.volume) : 0
      // 只返回成交量数值，颜色通过itemStyle的color函数根据开盘收盘比较来设置
      return volume
    })

    // 准备换手率数据
    const turnoverData = stockData.data.map(item => {
      const turnover = Number(item.turnover)
      return [item.date, turnover]
    }).filter(data => data[1] && Number.isFinite(data[1]))

    // 解析支撑和压力区间
    const parseLevel = (levelStr) => {
      if (!levelStr) return null
      // 提取数字部分，支持格式如 "10-12元"、"15.5-17.2"、"9.8 - 11.5 元"
      const match = levelStr.match(/([\d.]+)\s*-\s*([\d.]+)/)
      if (match) {
        return {
          low: parseFloat(match[1]),
          high: parseFloat(match[2])
        }
      }
      return null
    }

    const supportLevel = parseLevel(analysisResult?.support_level || '')
    const resistanceLevel = parseLevel(analysisResult?.resistance_level || '')

    return {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            show: true,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            color: '#ffffff',
            fontSize: 12
          }
        },
        formatter: function (params) {
          const date = params[0].axisValue
          let html = `${date}<br/>`

          params.forEach(param => {
            if (param.seriesName === 'K线') {
              const data = param.data
              html += `开盘: ${data[0]}<br/>`
              html += `收盘: ${data[1]}<br/>`
              html += `最低: ${data[2]}<br/>`
              html += `最高: ${data[3]}<br/>`
            } else if (param.seriesName === '成交量') {
              html += `成交量: ${param.data}<br/>`
            } else if (param.seriesName === '换手率') {
              html += `换手率: ${param.data[1].toFixed(2)}%<br/>`
            }
          })

          return html
        }
      },
      legend: {
        data: ['K线', '成交量', '换手率', '支撑区间', '压力区间'],
        textStyle: {
          color: '#ffffff'
        },
        // 允许点击图例切换系列显示/隐藏
        selectedMode: true
      },
      grid: [
        {
          left: '3%',
          right: '4%',
          top: '3%',
          height: '38%'
        },
        {
          left: '3%',
          right: '4%',
          top: '45%',
          height: '18%'
        },
        {
          left: '3%',
          right: '4%',
          top: '67%',
          height: '23%'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: {
            lineStyle: {
              color: '#ffffff'
            }
          },
          axisLabel: {
            color: '#ffffff',
            rotate: 45
          },
          splitLine: {
            show: false
          }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: {
            lineStyle: {
              color: '#ffffff'
            }
          },
          axisTick: {
            show: false
          },
          splitLine: {
            show: false
          },
          axisLabel: {
            show: false
          }
        },
        {
          type: 'category',
          gridIndex: 2,
          data: dates,
          scale: true,
          boundaryGap: false,
          axisLine: {
            lineStyle: {
              color: '#ffffff'
            }
          },
          axisTick: {
            show: false
          },
          splitLine: {
            show: false
          },
          axisLabel: {
            show: false
          }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(255, 255, 255, 0.1)', 'rgba(255, 255, 255, 0.05)']
            }
          },
          axisLine: {
            lineStyle: {
              color: '#ffffff'
            }
          },
          axisLabel: {
            color: '#ffffff'
          }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 3,
          axisLine: {
            lineStyle: {
              color: '#ffffff'
            }
          },
          axisLabel: {
            color: '#ffffff',
            // 添加成交量数值格式化，显示为万或亿
            formatter: function (value) {
              if (value >= 100000000) {
                return (value / 100000000).toFixed(2) + '亿';
              } else if (value >= 10000) {
                return (value / 10000).toFixed(2) + '万';
              }
              return value;
            }
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        },
        {
          scale: true,
          gridIndex: 2,
          splitNumber: 2,
          axisLine: {
            lineStyle: {
              color: '#ffffff'
            }
          },
          axisLabel: {
            color: '#ffffff',
            formatter: '{value}%'
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: 'rgba(255, 255, 255, 0.1)'
            }
          }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1, 2],
          start: Math.max(0, 100 - (365 / (stockData.data.length || 1)) * 100),
          end: 100
        },
        {
          show: true,
          xAxisIndex: [0, 1, 2],
          type: 'slider',
          bottom: '5%',
          start: Math.max(0, 100 - (365 / (stockData.data.length || 1)) * 100),
          end: 100,
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          borderColor: 'rgba(255, 255, 255, 0.2)',
          fillerColor: 'rgba(102, 126, 234, 0.3)',
          textStyle: {
            color: '#ffffff'
          }
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: klineData,
          itemStyle: {
            // A股和港股使用红涨绿跌，其他市场使用绿涨红跌
            // 这里设置为红涨绿跌，符合国内股票市场习惯
            color: '#ff4d4f',
            color0: '#52c41a',
            borderColor: '#ff4d4f',
            borderColor0: '#52c41a'
          }
        },
        // 支撑区间
        ...(supportLevel ? [{
          name: '支撑区间',
          type: 'line',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: [],
          markArea: {
            silent: true,
            itemStyle: {
              color: 'rgba(82, 196, 26, 0.4)',
              opacity: 0.6
            },
            data: [
              [
                { yAxis: supportLevel.low },
                { yAxis: supportLevel.high }
              ]
            ]
          },
          z: 1
        }] : []),
        // 压力区间
        ...(resistanceLevel ? [{
          name: '压力区间',
          type: 'line',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: [],
          markArea: {
            silent: true,
            itemStyle: {
              color: 'rgba(255, 77, 79, 0.4)',
              opacity: 0.6
            },
            data: [
              [
                { yAxis: resistanceLevel.low },
                { yAxis: resistanceLevel.high }
              ]
            ]
          },
          z: 1
        }] : []),
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumeData,
          itemStyle: {
            // 与K线颜色逻辑保持一致：红涨绿跌
            color: function (params) {
              // 根据对应K线的开盘收盘比较来设置颜色
              const index = params.dataIndex
              const open = klineData[index][0]
              const close = klineData[index][1]
              return open > close ? '#52c41a' : '#ff4d4f'
            }
          }
        },
        {
          name: '换手率',
          type: 'line',
          xAxisIndex: 2,
          yAxisIndex: 2,
          data: turnoverData,
          smooth: true,
          symbol: 'none',
          lineStyle: {
            color: '#667eea',
            width: 2
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
            ])
          }
        }
      ]
    }
  }

  // 初始化图表
  const initChart = () => {
    if (!chartContainerRef.current) return

    // 销毁之前的实例
    if (chartInstanceRef.current) {
      chartInstanceRef.current.dispose()
      chartInstanceRef.current = null
    }

    try {
      // 创建新实例
      chartInstanceRef.current = echarts.init(chartContainerRef.current)

      // 设置配置
      const option = generateChartOption()
      chartInstanceRef.current.setOption(option)

      // 添加窗口大小变化监听
      const handleResize = () => {
        if (chartInstanceRef.current) {
          chartInstanceRef.current.resize()
        }
      }

      window.addEventListener('resize', handleResize)

      // 返回清理函数
      return () => {
        window.removeEventListener('resize', handleResize)
        if (chartInstanceRef.current) {
          chartInstanceRef.current.dispose()
          chartInstanceRef.current = null
        }
      }
    } catch (error) {
      console.error('初始化图表失败:', error)
      return null
    }
  }

  // 更新图表
  const updateChart = () => {
    if (chartInstanceRef.current) {
      try {
        const option = generateChartOption()
        chartInstanceRef.current.setOption(option, true)
      } catch (error) {
        console.error('更新图表失败:', error)
        // 如果更新失败，重新初始化
        initChart()
      }
    }
  }

  // 只在数据变化且DOM可用时初始化图表
  useEffect(() => {
    if (!chartContainerRef.current) return
    if (!stockData || !stockData.data || stockData.data.length === 0) return

    const cleanup = initChart()

    return () => {
      if (cleanup) cleanup()
    }
  }, [stockData])

  // 当分析结果变化时，更新图表标记
  useEffect(() => {
    updateChart()
  }, [analysisResult])

  return (
    <div className="stock-chart">
      <div className="chart-header">
        <h3>{stock?.name} ({stock?.symbol}) - K线图</h3>
        <div className="chart-meta">
          <span className="meta-item">复权类型: {getAdjustName()}</span>
          <span className="meta-item">日K线图</span>
        </div>
      </div>
      <div className="chart-wrapper">
        {loading ? (
          <div className="loading">
            <p>加载股票数据中...</p>
          </div>
        ) : error ? (
          <div className="error">
            <p>{error}</p>
            <button className="btn btn-secondary" onClick={() => loadStockData(stock?.symbol)}>
              重试
            </button>
          </div>
        ) : (
          <div
            ref={chartContainerRef}
            style={{ height: '600px', width: '100%' }}
          />
        )}
      </div>
    </div>
  )
}

export default StockChart