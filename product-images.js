// Product Images Configuration
// This file contains all product images and their details for easy management
// Add new products here and they will automatically appear on home and shop pages

const PRODUCT_IMAGES = [
    {
        id: 1,
        name: "Small bubble",
        image: "/products/smallbubble.jpg",
        price: 99,
        description: "Small bubble",
        category: "candles",
        featured: true,
        note: "(x2)",
        rating: 4.8
    },
    {
        id: 2,
        name: "Coconut spiced candle",
        image: "/products/coconutspicedcandle.jpg",
        price: 199,
        description: "Coconut spiced candle",
        category: "candles",
        featured: true,
        rating: 4.9
    },
    {
        id: 3,
        name: "Flower in bowl",
        image: "/products/flowerinbowl.jpg",
        price: 249,
        description: "Flower in bowl",
        category: "candles",
        featured: true,
        rating: 4.7
    },
    {
        id: 4,
        name: "Garden in a boat",
        image: "/products/gardeninaboat.jpg",
        price: 499,
        description: "Garden in a boat",
        category: "candles",
        featured: true,
        rating: 5.0
    },
    {
        id: 5,
        name: "Heart candle",
        image: "/products/heartcandle.jpg",
        price: 199,
        description: "Heart candle",
        category: "candles",
        featured: false,
        rating: 4.6
    },
    {
        id: 6,
        name: "Iced coffee latte",
        image: "/products/icedcoffeelatte.jpg",
        price: 220,
        description: "Iced coffee latte",
        category: "latte",
        featured: true,
        rating: 4.8
    },
    {
        id: 7,
        name: "iced lavander latte",
        image: "/products/icedlavander.jpg",
        price: 220,
        description: "Iced lavander latte",
        category: "latte",
        featured: false,
        rating: 4.5
    },
    {
        id: 8,
        name: "Iced Strawberry latte",
        image: "/products/icedstrawberrylatte.jpg",
        price: 220,
        description: "Iced Strawberry latte",
        category: "latte",
        featured: false,
        rating: 4.7
    },
    {
        id: 9,
        name: "Ocean in a boat",
        image: "/products/oceaninaboat.jpg",
        price: 499,
        description: "Ocean in a boat",
        category: "candles",
        featured: false,
        rating: 4.9
    },
    {
        id: 10,
        name: "Ocean jar candle",
        image: "/products/oceanjarcandle.jpg",
        price: 220,
        description: "Ocean jar candle",
        category: "candles",
        featured: false,
        rating: 4.6
    },
    {
        id: 11,
        name: "Peony candle",
        image: "/products/peonycandle.jpg",
        price: 99,
        description: "Peony candle",
        category: "candles",
        featured: false,
        note: "(CUSTOMISED COLOUR)",
        rating: 4.8
    },
    {
        id: 12,
        name: "pink heart",
        image: "/products/pinkheart.jpg",
        price: 199,
        description: "pink heart",
        category: "candles",
        featured: false,
        rating: 4.5
    },
    {
        id: 13,
        name: "red heart",
        image: "/products/redheart.jpg",
        price: 199,
        description: "red heart",
        category: "candles",
        featured: false,
        rating: 4.7
    },
    {
        id: 14,
        name: "Spiral candle",
        image: "/products/spiralcandle.jpg",
        price: 199,
        description: "Spiral candle",
        category: "candles",
        featured: false,
        rating: 4.9
    },
    {
        id: 15,
        name: "Red Peony",
        image: "/products/roseinacage.jpg",
        price: 99,
        description: "Red Peony",
        category: "candles",
        featured: false,
        rating: 4.6
    },
    {
        id: 16,
        name: "Custom1",
        image: "/products/custom1.jpg",
        price: 99,
        description: "Custom1",
        category: "candles",
        featured: false,
        rating: 4.8
    },
    {
        id: 17,
        name: "Large bubble",
        image: "/products/largebubble.jpg",
        price: 199,
        description: "Large bubble",
        category: "candles",
        featured: false,
        note: "(x2)",
        rating: 4.7
    }
];

// Function to get all products
function getAllProducts() {
    return PRODUCT_IMAGES;
}

// Function to get featured products (for home page)
function getFeaturedProducts() {
    return PRODUCT_IMAGES.filter(product => product.featured);
}

// Function to get products by category
function getProductsByCategory(category) {
    return PRODUCT_IMAGES.filter(product => product.category === category);
}

// Function to add new product (for easy addition)
function addNewProduct(productData) {
    const newProduct = {
        id: Math.max(...PRODUCT_IMAGES.map(p => p.id)) + 1,
        featured: productData.featured || false,
        ...productData
    };
    PRODUCT_IMAGES.push(newProduct);
    return newProduct;
}

// Function to generate star rating HTML
function generateStarRating(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    let starsHtml = '';
    
    // Add full stars
    for (let i = 0; i < fullStars; i++) {
        starsHtml += '<i class="fas fa-star"></i>';
    }
    
    // Add half star if needed
    if (hasHalfStar) {
        starsHtml += '<i class="fas fa-star-half-alt"></i>';
    }
    
    // Add empty stars
    for (let i = 0; i < emptyStars; i++) {
        starsHtml += '<i class="far fa-star"></i>';
    }
    
    return `<div class="star-rating">${starsHtml} <span class="rating-number">(${rating})</span></div>`;
}

// Function to generate product HTML
function generateProductHTML(product) {
    const noteHtml = product.note ? `<small>${product.note}</small>` : '';
    const ratingHtml = product.rating ? generateStarRating(product.rating) : '';
    return `
        <div class="pc">
            <div class="p">
                <img src="${product.image}" alt="${product.name}"
                    data-name="${product.name}" data-price="${product.price}"
                    data-image="${product.image}"
                    onclick="handleProductClick(this)" style="cursor: pointer;">
                <div class="prod">
                    <div class="des">
                        <span>${product.name}</span>
                        ${ratingHtml}
                        <h5>₹${product.price}/-</h5>${noteHtml}
                    </div>
                    <div class="bun">
                        <!-- Cart icon -->
                        <a href="#"><i class="fa-solid fa-cart-shopping cart"
                            onclick="addToCartFromElement(this)"></i></a>
                        <!-- Add to Cart button -->
                        <button onclick="addToCartFromElement(this)">
                            Add to Cart
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Function to load products on page
function loadProductsFromConfig() {
    const currentPage = window.location.pathname;
    let productsToShow = [];
    
    if (currentPage === '/' || currentPage === '/index.html' || currentPage.includes('index')) {
        // Home page - show all products (like original design)
        productsToShow = getAllProducts();
    } else if (currentPage === '/shop.html' || currentPage.includes('shop')) {
        // Shop page - show all products
        productsToShow = getAllProducts();
    } else {
        // Other pages - show all products
        productsToShow = getAllProducts();
    }
    
    const productContainer = document.querySelector('#pro1 .procont');
    if (productContainer && productsToShow.length > 0) {
        // Clear existing products
        productContainer.innerHTML = '';
        
        // Add products from configuration
        productsToShow.forEach(product => {
            productContainer.innerHTML += generateProductHTML(product);
        });
        
        console.log(`Loaded ${productsToShow.length} products from configuration`);
    }
}

// Auto-load products when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadProductsFromConfig();
});

// Export functions for global use
window.PRODUCT_IMAGES = PRODUCT_IMAGES;
window.getAllProducts = getAllProducts;
window.getFeaturedProducts = getFeaturedProducts;
window.getProductsByCategory = getProductsByCategory;
window.addNewProduct = addNewProduct;
window.loadProductsFromConfig = loadProductsFromConfig;