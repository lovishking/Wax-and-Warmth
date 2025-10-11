// Sample Product Initialization for Wax and Warmth Admin Dashboard
// This script will create some sample products if none exist

function initializeSampleProducts() {
    const existingProducts = localStorage.getItem('waxProducts');
    
    if (existingProducts && JSON.parse(existingProducts).length > 0) {
        console.log('Products already exist, skipping initialization');
        return;
    }
    
    const sampleProducts = [
        {
            id: 1704067200000, // Sample timestamp
            name: "Lavender Dreams",
            price: 349,
            description: "A soothing lavender-scented candle perfect for relaxation and meditation. Made with natural soy wax and essential oils.",
            category: "candles",
            stock: 15,
            image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJsYXZlbmRlciIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LXNpemU9IjE4IiBmaWxsPSJ3aGl0ZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkxhdmVuZGVyIERyZWFtczwvdGV4dD48L3N2Zz4=",
            dateAdded: new Date().toISOString()
        },
        {
            id: 1704067260000,
            name: "Vanilla Bliss",
            price: 299,
            description: "Sweet vanilla fragrance that fills your home with warmth and comfort. Hand-poured with love.",
            category: "candles",
            stock: 20,
            image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJidXJseXdvb2QiLz48dGV4dCB4PSI1MCUiIHk9IjUwJSIgZm9udC1zaXplPSIxOCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj5WYW5pbGxhIEJsaXNzPC90ZXh0Pjwvc3ZnPg==",
            dateAdded: new Date().toISOString()
        },
        {
            id: 1704067320000,
            name: "Rose Garden Wax Melts",
            price: 199,
            description: "Beautiful rose-scented wax melts that create a romantic ambiance. Set of 6 pieces.",
            category: "wax-melts",
            stock: 25,
            image: "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSJwaW5rIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSI+Um9zZSBHYXJkZW4gV2F4IE1lbHRzPC90ZXh0Pjwvc3ZnPg==",
            dateAdded: new Date().toISOString()
        }
    ];
    
    localStorage.setItem('waxProducts', JSON.stringify(sampleProducts));
    localStorage.setItem('websiteProducts', JSON.stringify(sampleProducts));
    
    console.log('Sample products initialized successfully');
    return sampleProducts;
}

// Run initialization when script is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure page is fully loaded
    setTimeout(initializeSampleProducts, 500);
});

// Export function for manual use
window.initializeSampleProducts = initializeSampleProducts;