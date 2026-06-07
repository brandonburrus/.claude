# Web performance checklist

Detailed reference for optimize-performance. The skill carries the Core Web Vitals targets and the diagnosis workflow; this is the working checklist behind them: what to inspect per layer, how to measure, and the anti-patterns that recur.

## Table of Contents

- [TTFB diagnosis](#ttfb-diagnosis)
- [Frontend](#frontend)
- [Backend](#backend)
- [Measurement](#measurement)
- [Anti-patterns](#anti-patterns)

## TTFB diagnosis

When TTFB is slow (over 800ms), split it in the DevTools Network waterfall and attack the dominant segment:

- DNS resolution slow: add `<link rel="dns-prefetch">` or `<link rel="preconnect">` for known origins
- TCP/TLS handshake slow: enable HTTP/2 or HTTP/3, verify keep-alive, consider edge deployment
- Server processing slow: profile the backend, check slow queries, add caching

## Frontend

### Images

- Modern formats (WebP, AVIF)
- Responsively sized with `srcset` and `sizes`
- Explicit `width` and `height` on `<img>` and `<source>` to prevent CLS
- Below-the-fold images use `loading="lazy"` and `decoding="async"`
- The hero/LCP image uses `fetchpriority="high"` and is never lazy-loaded

### JavaScript

- Initial bundle under 200KB gzipped
- Code-split with dynamic `import()` for routes and heavy features
- Tree shaking on (dependency ships ESM and marks `sideEffects: false`)
- No blocking JS in `<head>`; use `defer` or `async`
- Heavy computation offloaded to a Web Worker where it applies
- `React.memo()` on expensive components that re-render with unchanged props; `useMemo`/`useCallback` only where profiling shows a benefit
- Long tasks (over 50ms) broken up to keep the main thread free; this is the main lever for INP
- Yield inside long loops so input can run between chunks: `scheduler.yield()` (preferred), then `scheduler.postTask()` with priorities, `isInputPending()`, or a manual `yieldToMain`; `requestIdleCallback` for deferrable work (analytics flush, prefetch)
- Non-critical work (analytics, logging) deferred out of event handlers so the interaction response is not delayed
- Third-party scripts `async`/`defer`, size-audited, and fronted by a facade when heavy (chat widgets, embeds)

### CSS

- Critical CSS inlined or preloaded
- No render-blocking CSS for non-critical styles
- No CSS-in-JS runtime cost in production (extract at build time)

### Fonts

- 2-3 families, 2-3 weights each; every extra weight is another request
- WOFF2 only (smallest, universal support; skip WOFF/TTF/EOT)
- Self-hosted where possible; third-party font CDNs add DNS, TCP, and TLS round-trips
- LCP-critical fonts preloaded: `<link rel="preload" as="font" type="font/woff2" crossorigin>`
- `font-display: swap` (or `optional` for non-critical) to avoid the FOIT render block
- Subsetted with `unicode-range` to ship only the glyphs a page needs
- Variable fonts when multiple weights are needed (one file replaces many)
- Fallback metrics tuned with `size-adjust`, `ascent-override`, `descent-override` to cut CLS on swap
- System font stack considered before any custom font

### Network

- Static assets cached with a long `max-age` plus content hashing
- API responses cached where appropriate (`Cache-Control`)
- HTTP/2 or HTTP/3 enabled
- `<link rel="preconnect">` for known third-party origins
- `fetchpriority` on critical non-image resources too (key preloads, above-the-fold scripts), not only images
- No unnecessary redirects

### Rendering

- No layout thrashing; batch DOM reads, then batch writes
- Animations limited to `transform` and `opacity` (GPU-accelerated)
- Long lists virtualized (for example `react-window`)
- No unnecessary full-page re-renders
- Off-screen sections use `content-visibility: auto` with `contain-intrinsic-size` to skip their layout and paint
- No `unload` handlers and no `Cache-Control: no-store` on HTML, so back/forward cache (bfcache) stays eligible

## Backend

### Database

- No N+1 patterns; use eager loading or joins
- Indexes on filtered and sorted columns
- List endpoints paginated; never `SELECT *` an unbounded table
- Connection pooling configured
- Slow-query logging on

### API

- p95 response time under 200ms
- No synchronous heavy computation in request handlers
- Bulk operations instead of loops of individual calls
- Response compression (gzip or brotli)
- Caching where it fits (in-memory, Redis, CDN)

### Infrastructure

- CDN for static assets
- Server close to users, or edge deployment
- Horizontal scaling configured where needed
- Health-check endpoint for the load balancer

## Measurement

INP is field-first: check [CrUX](https://developer.chrome.com/docs/crux/vis) or your RUM tool for real-user INP before optimizing, then reproduce in DevTools Performance while interacting, and test on a mid-range Android or with 4x to 6x CPU throttling (INP problems often only show on slower hardware).

```bash
# Lighthouse
npx lighthouse https://localhost:3000 --output json --output-path ./report.json

# Bundle analysis
npx webpack-bundle-analyzer stats.json   # or: npx vite-bundle-visualizer
npx bundlesize

# Web Vitals in code (attribution build gives per-interaction detail)
import { onINP } from 'web-vitals/attribution';
onINP(({ value, attribution }) => {
  const { interactionTarget, inputDelay, processingDuration, presentationDelay } = attribution;
  console.log({ value, interactionTarget, inputDelay, processingDuration, presentationDelay });
});
```

## Anti-patterns

| Anti-pattern | Impact | Fix |
|---|---|---|
| N+1 queries | linear DB load growth | joins, includes, or batch loading |
| unbounded queries | memory exhaustion, timeouts | always paginate, add `LIMIT` |
| missing indexes | reads slow as data grows | index filtered and sorted columns |
| layout thrashing | jank, dropped frames | batch reads, then batch writes |
| unoptimized images | slow LCP, wasted bandwidth | WebP, responsive sizes, lazy load |
| large bundles | slow Time to Interactive | code split, tree shake, audit deps |
| blocking the main thread | poor INP, unresponsive UI | chunk long tasks, offload to a worker |
| memory leaks | growing memory, eventual crash | clean up listeners, intervals, refs |
