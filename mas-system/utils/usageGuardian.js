// usageGuardian.js – tracks OpenRouter API calls
const dailyLimit = 200;
const perMinLimit = 10;
let dailyCount = 0;
let minuteTimestamps = [];
let lastDay = new Date().toISOString().slice(0,10);

export function checkUsage() {
  const now = Date.now();
  // reset daily at midnight UTC
  const currentDay = new Date().toISOString().slice(0,10);
  if (lastDay !== currentDay) {
    dailyCount = 0;
    lastDay = currentDay;
  }
  // minute window
  minuteTimestamps = minuteTimestamps.filter(t => now - t < 60000);
  if (minuteTimestamps.length >= perMinLimit) throw new Error('Per-minute API limit reached');
  if (dailyCount >= dailyLimit) throw new Error('Daily API limit reached');

  dailyCount++;
  minuteTimestamps.push(now);
}

export function getUsage() {
  return { dailyCount, perMinute: minuteTimestamps.length, dailyLimit, perMinLimit };
}
