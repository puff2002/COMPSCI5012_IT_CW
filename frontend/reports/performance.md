# Performance and Sustainability Report

## Optimization work completed

- [x] TypeScript build emits lean browser JS modules
- [x] Shared API wrapper prevents duplicate auth logic
- [x] Per-page modules load only required code
- [x] Item images are lazy-loaded
- [x] Placeholder dimensions reduce layout shift
- [x] Reused layout/styles reduce CSS duplication

## Baseline/after methodology

- [x] Baseline pages selected: `index.html`, `closet.html`
- [x] After pages selected: `index.html`, `closet.html`
- [x] Lighthouse command prepared for execution in browser-enabled environment

## Command

```bash
lighthouse http://127.0.0.1:5500/frontend/index.html --view
lighthouse http://127.0.0.1:5500/frontend/closet.html --view
```

## Sustainability notes

- [x] Reduced script duplication through shared typed modules
- [x] Implemented graceful failure paths to avoid repeated request storms
- [x] Added size and type validation before upload
