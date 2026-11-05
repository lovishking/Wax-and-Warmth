const PRODUCTS_READY_EVENT = 'storefront:products-ready';

export function notifyProductsReady() {
  window.dispatchEvent(new Event(PRODUCTS_READY_EVENT));
}

export { PRODUCTS_READY_EVENT };
