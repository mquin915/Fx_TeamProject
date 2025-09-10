// frontend/src/components/FxRateDashboard.tsx
import React, { useMemo, useState } from 'react';
import './Dashboard.css';

import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Tooltip, Legend,
  type ChartData, type ChartOptions
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend);

// -------------------------------
// 통화 상수 & 타입
// -------------------------------
export const CURRENCIES = ['USD','EUR','CNY','JPY100','ISK','RUB','KRW'] as const;
export type Currency = typeof CURRENCIES[number];

// -------------------------------
// API 응답 타입
// -------------------------------
type HistoryPoint = { date: string; rate: number | string | null | undefined };
type PredictPoint = { date: string; value: number | string | null | undefined };
type HistoryResp = { pair: string; data: HistoryPoint[] };
type PredictResp = { pair: string; horizon: number; yhat: PredictPoint[] };

// -------------------------------
// 유틸리티 함수
// -------------------------------
const normDate = (s: string | null | undefined): string => {
  if (!s) return '';
  return String(s).trim().slice(0, 10);
};

const toNum = (v: unknown): number | null => {
  if (v == null) return null;
  if (typeof v === 'number') return Number.isFinite(v) ? v : null;
  const cleaned = String(v).replace(/,/g, '').replace(/\s+/g, '').trim();
  const n = Number(cleaned);
  return Number.isFinite(n) ? n : null;
};

// -------------------------------
// API 호출 함수
// -------------------------------
async function apiGetHistory(pair: string, start: string, end: string): Promise<HistoryResp> {
  if (!pair) throw new Error('pair is required');
  const r = await fetch(`/api/history?pair=${encodeURIComponent(pair)}&start=${start}&end=${end}`);
  if (!r.ok) throw new Error(`History API error: ${r.status}`);
  return r.json();
}

async function apiGetPredict(pair: string, horizon: number): Promise<PredictResp> {
  if (!pair) throw new Error('pair is required');
  const r = await fetch(`/api/predict?pair=${encodeURIComponent(pair)}&horizon=${horizon}`);
  if (!r.ok) throw new Error(`Predict API error: ${r.status}`);
  return r.json();
}

// -------------------------------
// 메인 컴포넌트
// -------------------------------
export default function FxRateDashboard() {
  // State 관리
  const [base, setBase] = useState<Currency>('USD');
  const [target, setTarget] = useState<Currency>('KRW');
  const [start, setStart] = useState<string>(() => {
    const d = new Date(); 
    d.setFullYear(d.getFullYear() - 1);
    return d.toISOString().slice(0,10);
  });
  const [end, setEnd] = useState<string>(() => new Date().toISOString().slice(0,10));
  const [horizon, setHorizon] = useState<number>(7);

  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [predict, setPredict] = useState<PredictPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const pair = `${base}_${target}`;

  // 유효성 검사
  const validationMsg = useMemo(() => {
    if (base === target) return 'Base와 Target 통화는 달라야 합니다.';
    if (!start || !end) return '시작일/종료일을 선택하세요.';
    if (start > end) return '시작일이 종료일보다 앞서야 합니다.';
    return '';
  }, [base, target, start, end]);

  // 데이터 fetching 함수들
  const fetchHistory = async (): Promise<void> => {
    if (validationMsg) return;
    
    setLoading(true);
    setError('');
    setPredict([]); // 새 history를 가져올 때 기존 예측 초기화
    
    try {
      const res = await apiGetHistory(pair, start, end);
      const cleaned = (res.data ?? []).map(d => ({
        date: normDate(d.date),
        rate: toNum(d.rate)
      }));
      setHistory(cleaned);
      console.log(`Loaded ${cleaned.length} history points for ${pair}`);
    } catch (e: any) {
      setError(e?.message ?? 'History fetch error');
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchPredict = async (): Promise<void> => {
    if (!history.length) return;
    
    setLoading(true);
    setError('');
    
    try {
      const res = await apiGetPredict(pair, horizon);
      const cleaned = (res.yhat ?? []).map(d => ({
        date: normDate(d.date),
        value: toNum(d.value)
      }));
      setPredict(cleaned);
      console.log(`Loaded ${cleaned.length} prediction points for ${pair}`);
    } catch (e: any) {
      setError(e?.message ?? 'Prediction fetch error');
      setPredict([]);
    } finally {
      setLoading(false);
    }
  };

  // 차트 데이터 생성
  const chartData: ChartData<'line', (number | null)[], string> = useMemo(() => {
    if (!history.length) {
      return {
        labels: [],
        datasets: []
      };
    }

    // History 데이터 처리
    const historyLabels = history.map(d => d.date).filter(Boolean);
    const historyValues = history.map(d => toNum(d.rate));
    
    // 유효한 데이터가 있는지 확인
    const validHistoryValues = historyValues.filter(v => v !== null);
    if (validHistoryValues.length === 0) {
      console.warn('No valid history data found');
      return {
        labels: historyLabels,
        datasets: [{
          label: '환율 데이터 (데이터 없음)',
          data: historyValues,
          borderColor: '#dc2626',
          borderWidth: 2,
          pointRadius: 3,
          tension: 0.1,
          spanGaps: false,
        }]
      };
    }

    const datasets = [{
      label: '환율 데이터',
      data: historyValues,
      borderColor: '#2563eb',
      borderWidth: 2,
      pointRadius: 1,
      tension: 0.1,
      spanGaps: true,
      fill: false
    }];

    // 예측 데이터가 있으면 추가
    if (predict.length > 0) {
      // 전체 라벨 생성 (history + prediction)
      const allDates = new Set([...historyLabels]);
      predict.forEach(p => {
        if (p.date) allDates.add(p.date);
      });
      const allLabels = Array.from(allDates).sort();

      // History 데이터를 전체 라벨에 맞게 매핑
      const historyMap = new Map(history.map(d => [d.date, toNum(d.rate)]));
      const mappedHistoryData = allLabels.map(label => historyMap.get(label) ?? null);

      // Prediction 데이터를 전체 라벨에 맞게 매핑
      const predictionMap = new Map(predict.map(d => [d.date, toNum(d.value)]));
      const mappedPredictionData = allLabels.map(label => predictionMap.get(label) ?? null);

      return {
        labels: allLabels,
        datasets: [
          {
            ...datasets[0],
            data: mappedHistoryData,
          },
          {
            label: '예측',
            data: mappedPredictionData,
            borderColor: '#f59e0b',
            borderWidth: 2,
            borderDash: [6, 4],
            pointRadius: 2,
            tension: 0.1,
            spanGaps: true,
            fill: false
          }
        ]
      };
    }

    return {
      labels: historyLabels,
      datasets
    };
  }, [history, predict]);

  // Y축 범위 계산
  const yDomain = useMemo(() => {
    const historyValues = history.map(d => toNum(d.rate)).filter((v): v is number => v !== null);
    const predictValues = predict.map(d => toNum(d.value)).filter((v): v is number => v !== null);
    const allValues = [...historyValues, ...predictValues];
    
    if (!allValues.length) return { min: undefined, max: undefined };
    
    let min = Math.min(...allValues);
    let max = Math.max(...allValues);
    
    if (min === max) { 
      min -= Math.abs(min * 0.1) || 1; 
      max += Math.abs(max * 0.1) || 1; 
    }
    
    const padding = (max - min) * 0.05;
    return { 
      min: min - padding, 
      max: max + padding 
    };
  }, [history, predict]);

  // 차트 옵션
  const chartOptions: ChartOptions<'line'> = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    interaction: { 
      mode: 'index', 
      intersect: false 
    },
    scales: {
      x: { 
        type: 'category',
        grid: { 
          display: true,
          color: '#f3f4f6'
        }
      },
      y: { 
        min: yDomain.min, 
        max: yDomain.max,
        grid: {
          display: true,
          color: '#f3f4f6'
        }
      },
    },
    plugins: {
      legend: { 
        labels: { 
          usePointStyle: true 
        } 
      },
      tooltip: { 
        intersect: false,
        callbacks: {
          title: function(context) {
            return context[0]?.label || '';
          },
          label: function(context) {
            const value = context.parsed.y;
            if (value === null) return `${context.dataset.label}: 데이터 없음`;
            return `${context.dataset.label}: ${value.toFixed(4)}`;
          }
        }
      },
    }
  }), [yDomain.min, yDomain.max]);

  // 유효 데이터 개수
  const validHistoryCount = useMemo(() => {
    return history.reduce((acc, d) => {
      const v = toNum(d.rate);
      return acc + (v !== null ? 1 : 0);
    }, 0);
  }, [history]);

  return (
    <div className="container">
      <h1 className="page-title">환율 대시보드</h1>

      {/* 컨트롤 패널 */}
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="dashboard-toolbar">
          <div className="filters-grid">
            <div>
              <label>Base Currency</label><br/>
              <select value={base} onChange={e => setBase(e.target.value as Currency)}>
                {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label>Target Currency</label><br/>
              <select value={target} onChange={e => setTarget(e.target.value as Currency)}>
                {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label>시작일</label><br/>
              <input 
                type="date" 
                value={start} 
                onChange={e => setStart(e.target.value)} 
              />
            </div>
            <div>
              <label>종료일</label><br/>
              <input 
                type="date" 
                value={end} 
                onChange={e => setEnd(e.target.value)} 
              />
            </div>
          </div>

          <div className="controls-row">
            <div>
              <label>예측 일수</label><br/>
              <input 
                type="number" 
                min={1} 
                max={30} 
                value={horizon}
                onChange={e => setHorizon(Number(e.target.value) || 1)} 
              />
            </div>
            <button 
              className="btn btn--primary"
              onClick={fetchHistory} 
              disabled={!!validationMsg || loading}
            >
              {loading ? '로딩중...' : '환율 데이터 조회'}
            </button>
            <button 
              className="btn btn--predict"
              onClick={fetchPredict} 
              disabled={!history.length || loading}
            >
              {loading ? '예측중...' : '예측 실행'}
            </button>
          </div>
        </div>

        {/* 메시지 영역 */}
        <div className="messages">
          {validationMsg && (
            <div className="msg msg--error">{validationMsg}</div>
          )}
          {error && (
            <div className="msg msg--error">오류: {error}</div>
          )}
          {history.length > 0 && (
            <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '8px' }}>
              {pair}: {validHistoryCount}개 데이터 포인트 
              {predict.length > 0 && `, ${predict.length}개 예측 포인트`}
            </div>
          )}
        </div>
      </div>

      {/* 차트 영역 */}
      <div className="card chart-card">
        {loading ? (
          <div className="centered centered--muted">
            데이터를 불러오는 중...
          </div>
        ) : history.length === 0 ? (
          <div className="centered centered--hint">
            해당 데이터가 없습니다. 다른 범위를 선택한 후, "환율 데이터 조회" 버튼을 클릭하세요.
          </div>
        ) : validHistoryCount === 0 ? (
          <div className="centered centered--hint">
            선택한 기간에 유효한 데이터가 없습니다.<br/>
            다른 기간을 선택해보세요.
          </div>
        ) : (
          <Line
            data={chartData}
            options={chartOptions}
            height={460}
          />
        )}
      </div>
    </div>
  );
}