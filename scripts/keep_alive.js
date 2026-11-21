#!/usr/bin/env node
/**
 * Backend Keep-Alive Cron / Ping Script (Node.js)
 * ------------------------------------------------
 * Periodically pings the backend to keep it active.
 * Zero external dependencies (uses native fetch in Node 18+).
 */

const targetUrl = process.env.BACKEND_PING_URL || process.env.BACKEND_URL || 'https://wax-and-warmth.onrender.com/api/settings/';
const intervalMinutes = parseFloat(process.env.PING_INTERVAL_MINUTES || '10');
const intervalMs = Math.max(10, intervalMinutes * 60) * 1000;
const runOnce = process.argv.includes('--once');

function log(level, message) {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
  console.log(`[${timestamp}] [${level}] ${message}`);
}

async function ping() {
  const start = Date.now();
  try {
    const res = await fetch(targetUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'WaxAndWarmth-KeepAlive-Node/1.0',
        'Accept': 'application/json, */*',
      },
      signal: AbortSignal.timeout(30000),
    });
    const duration = Date.now() - start;
    if (res.ok) {
      log('SUCCESS', `Status ${res.status} OK from ${targetUrl} (${duration}ms) - Backend is awake!`);
      return true;
    } else {
      log('AWAKE', `Server responded with status ${res.status} (${duration}ms) - Backend is awake!`);
      return true;
    }
  } catch (err) {
    const duration = Date.now() - start;
    log('ERROR', `Request failed to ${targetUrl}: ${err.message} (${duration}ms)`);
    return false;
  }
}

async function main() {
  console.log('='.repeat(65));
  console.log(' Wax & Warmth Keep-Alive (Node.js)');
  console.log(` Target URL : ${targetUrl}`);
  console.log(` Interval   : ${intervalMinutes} minutes`);
  console.log('='.repeat(65));

  if (runOnce) {
    const ok = await ping();
    process.exitCode = ok ? 0 : 1;
    return;
  }

  await ping();
  const nextTime = new Date(Date.now() + intervalMs).toLocaleTimeString();
  log('INFO', `Next ping at ${nextTime}. Press Ctrl+C to stop.\n`);

  setInterval(async () => {
    await ping();
    const next = new Date(Date.now() + intervalMs).toLocaleTimeString();
    log('INFO', `Next ping at ${next}. Press Ctrl+C to stop.\n`);
  }, intervalMs);
}

main();
