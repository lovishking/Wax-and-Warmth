import { useEffect, useRef, useState } from 'react';
import { Flame, Sparkles } from 'lucide-react';
import { useStorefront } from '../context/StorefrontContext';
import { PRODUCTS_READY_EVENT } from '../api/storefrontEvents';
import './WakeUpGame.css';

const ROUND_SECONDS = 50;

export default function WakeUpGame() {
  const { loading, error, refreshSettings } = useStorefront();
  const [visible, setVisible] = useState(false);
  const [seconds, setSeconds] = useState(ROUND_SECONDS);
  const [score, setScore] = useState(0);
  const [drops, setDrops] = useState([]);
  const [basket, setBasket] = useState(50);
  const [productsReady, setProductsReady] = useState(false);
  const board = useRef(null);
  const nextId = useRef(0);
  const basketPosition = useRef(50);
  const remainingTime = useRef(ROUND_SECONDS);

  useEffect(() => {
    const markReady = () => setProductsReady(true);
    window.addEventListener(PRODUCTS_READY_EVENT, markReady);
    return () => window.removeEventListener(PRODUCTS_READY_EVENT, markReady);
  }, []);

  useEffect(() => {
    if (productsReady) { setVisible(false); return undefined; }
    if (error) { setVisible(true); return undefined; }
    if (!loading) { setVisible(false); return undefined; }
    const delay = window.setTimeout(() => setVisible(true), 700);
    return () => window.clearTimeout(delay);
  }, [loading, error, productsReady]);

  useEffect(() => {
    if (!visible) return undefined;
    const start = Date.now();
    remainingTime.current = ROUND_SECONDS;
    setSeconds(ROUND_SECONDS);
    const timer = window.setInterval(() => {
      const remaining = Math.max(0, ROUND_SECONDS - Math.floor((Date.now() - start) / 1000));
      remainingTime.current = remaining;
      setSeconds(remaining);
      if (remaining === 0) window.clearInterval(timer);
    }, 200);
    return () => window.clearInterval(timer);
  }, [visible]);

  useEffect(() => {
    if (!visible || productsReady || !error || loading) return undefined;
    const retry = window.setInterval(() => refreshSettings(), 4000);
    return () => window.clearInterval(retry);
  }, [visible, productsReady, error, loading, refreshSettings]);

  useEffect(() => {
    if (!visible) return undefined;
    const tick = window.setInterval(() => {
      if (remainingTime.current === 0) return;
      setDrops((current) => {
        const falling = current.map((drop) => ({ ...drop, y: drop.y + 1.65 }));
        const caught = falling.filter((drop) => drop.y >= 83 && drop.y <= 96 && Math.abs(drop.x - basketPosition.current) < 11);
        if (caught.length) setScore((value) => value + caught.length);
        const remaining = falling.filter((drop) => drop.y < 100 && !caught.includes(drop));
        if (Math.random() < 0.12) remaining.push({ id: nextId.current++, x: 7 + Math.random() * 86, y: -5, tone: Math.random() > 0.5 ? 'gold' : 'cream' });
        return remaining;
      });
    }, 70);
    return () => window.clearInterval(tick);
  }, [visible]);

  function moveBasket(event) {
    const bounds = board.current?.getBoundingClientRect();
    if (!bounds) return;
    const position = Math.min(91, Math.max(9, ((event.clientX - bounds.left) / bounds.width) * 100));
    basketPosition.current = position;
    setBasket(position);
  }

  if (!visible || productsReady || (!loading && !error)) return null;

  return <div className="wake-overlay" role="dialog" aria-modal="true" aria-labelledby="wake-title">
    <section className="wake-card">
      <div className="wake-heading"><span className="wake-mark"><Flame size={19}/></span><span className="wake-wordmark">WAX AND WARMTH</span><span className="wake-live">CANDLE CATCH</span></div>
      <div className="wake-copy"><p className="wake-kicker">A LITTLE MOMENT OF PLAY</p><h1 id="wake-title">Catch the candlelight</h1><p>Slide your basket and catch the falling sparks. How many can you gather?</p></div>
      <div className="wake-stats"><span><Sparkles size={16}/> Sparks caught <b>{score}</b></span><span className="wake-clock">{seconds > 0 ? `00:${String(seconds).padStart(2, '0')}` : 'One moment…'}</span></div>
      <div className="wake-board" ref={board} onPointerMove={moveBasket} onPointerDown={moveBasket} aria-label="Move your basket under the falling candle sparks">
        <div className="wake-moon"/><div className="wake-horizon"/>
        {drops.map((drop) => <span key={drop.id} className={`wake-spark ${drop.tone}`} style={{ left: `${drop.x}%`, top: `${drop.y}%` }}>✦</span>)}
        <div className="wake-basket" style={{ left: `${basket}%` }}><span>✧</span></div>
        <div className="wake-board-hint">MOVE YOUR POINTER TO CATCH THE SPARKS</div>
      </div>
      <div className="wake-footer"><span>{seconds > 0 ? 'Move your basket and collect the golden sparks.' : `Beautifully done — you caught ${score} ${score === 1 ? 'spark' : 'sparks'}!`}</span><span className="wake-dots"><i/><i/><i/></span></div>
    </section>
  </div>;
}
