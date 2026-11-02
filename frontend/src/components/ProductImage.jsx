import { useMemo, useState } from 'react';

const apiOrigin = new URL(import.meta.env.VITE_API_URL || 'http://localhost:8000/api').origin;
const productPlaceholder = '/wax/images/candle-546563.jpg';

function candidatesFor(source) {
  if (!source) return [productPlaceholder];
  const original = source.startsWith('http')
    ? source
    : source.startsWith('/')
      ? source
      : `/wax/${source}`;
  const candidates = [original];
  try {
    const path = new URL(original, window.location.origin).pathname;
    const mediaPath = path.includes('/media/') ? path.split('/media/').pop() : null;
    const relativePath = mediaPath || path.replace(/^\//, '').replace(/^wax\//, '');
    if (relativePath.startsWith('products/')) candidates.push(`/wax/${relativePath}`);
  } catch {
    // Keep the original source and fall back to the bundled placeholder.
  }
  if (original.startsWith(`${apiOrigin}/media/`)) {
    candidates.push(`/wax/${original.slice(`${apiOrigin}/media/`.length)}`);
  }
  candidates.push(productPlaceholder);
  return [...new Set(candidates)];
}

export default function ProductImage({ src, alt = '', ...props }) {
  const candidates = useMemo(() => candidatesFor(src), [src]);
  const [failedSource, setFailedSource] = useState(null);
  const candidateIndex = failedSource?.src === src ? failedSource.index : 0;

  if (candidateIndex >= candidates.length) {
    return <div className={props.className} role="img" aria-label={alt || 'Product image unavailable'} />;
  }

  return (
    <img
      {...props}
      src={candidates[candidateIndex]}
      alt={alt}
      onError={() => setFailedSource({ src, index: candidateIndex + 1 })}
    />
  );
}
