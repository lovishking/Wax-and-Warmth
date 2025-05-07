// Cart functionality
let cart = [];

// Add item to cart
function addToCart(productId) {
    // You can modify the productId to dynamically get more details of the product
    const product = {
        id: productId,
        name: document.querySelector(`#product-${productId} .name`).innerText,
        price: document.querySelector(`#product-${productId} .price`).innerText
    };

    // Add the product to the cart array
    cart.push(product);
    updateCartIcon();
}

// Update cart icon with cart count
function updateCartIcon() {
    const cartCount = cart.length;
    document.querySelector(".fa-cart-shopping").innerText = `(${cartCount})`;  // update cart count icon
}

// Handle navigation between pages and cart details
document.querySelector("#navbar a[href='cart.html']").addEventListener("click", function () {
    localStorage.setItem("cart", JSON.stringify(cart)); // Store cart in local storage for persistence
});

window.onload = () => {
    const cartData = JSON.parse(localStorage.getItem("cart"));
    if (cartData) {
        cart = cartData;  // Load cart from local storage
        updateCartIcon();
    }
};
