# Storefront

React and Vite customer storefront. Product images and the brand mark are in `public/wax`.

## Run locally

```powershell
npm install
npm run dev
```

Create `.env.local` if it does not exist:

```text
VITE_API_URL=http://localhost:8000/api
```

Set `VITE_API_URL` to the API origin plus `/api` before building for deployment. It is a public frontend setting; never put credentials or server secrets in `VITE_*` variables.

Cloudflare Pages uses this directory as its root, `npm run build` as the build command, and `dist` as the output directory. The `_redirects` file enables client-side routes on refresh.
