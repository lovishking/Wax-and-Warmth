// Initialize cart from localStorage or as empty array
let cart = JSON.parse(localStorage.getItem("cart")) || [];

// Function to add a product to the cart
function addToCart(name, price, image) {
    const product = { name, price, image, quantity: 1 };

    // Check if product already exists in cart
    const existingProduct = cart.find(item => item.name === name);
    if (existingProduct) {
        existingProduct.quantity += 1;
    } else {
        cart.push(product);
    }

    // Save cart back to localStorage
    localStorage.setItem("cart", JSON.stringify(cart));

    // Optionally alert or toast message
    alert(`${name} added to cart`);
}

// Load cart items into the cart page
function loadCart() {
    const cartBody = document.getElementById("cart-body");
    if (!cartBody) return;

    cartBody.innerHTML = "";
    let total = 0;

    cart.forEach((item, index) => {
        const subtotal = item.price * item.quantity;
        total += subtotal;
        document.getElementById("total-amount").textContent = `Total: ₹${total}`;


        cartBody.innerHTML += `
        <tr>
            <td><button onclick="removeFromCart(${index})">X</button></td>
            <td><img src="${item.image}" width="50"></td>
            <td>${item.name}</td>
            <td>${item.price}</td>
            <td><input type="number" value="${item.quantity}" min="1" onchange="updateQuantity(${index}, this.value)"></td>
            <td>${subtotal}</td>
        </tr>
        `;
    });

    if (cartBody.innerHTML === "") {
        cartBody.innerHTML = `<tr><td colspan="6">Your cart is empty</td></tr>`;
    }
    document.getElementById("total-amount").textContent = `Total: ₹${total}`;
}

// Remove item from cart
function removeFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCart();
}

// Update quantity in cart
function updateQuantity(index, newQuantity) {
    cart[index].quantity = parseInt(newQuantity);
    localStorage.setItem("cart", JSON.stringify(cart));
    loadCart();
}

// Run this on cart.html to load cart
window.onload = loadCart;

function checkout() {
    if (cart.length === 0) {
        alert("Your cart is empty.");
        return;
    }

    let message = "Hello! I'd like to place an order:\n\n";
    let totalAmount = 0;

    cart.forEach(item => {
        const subtotal = item.price * item.quantity;
        totalAmount += subtotal;
        message += `• ${item.name} x ${item.quantity} = ₹${subtotal}\n`;
    });

    message += `\nTotal: ₹${totalAmount}\nThank you!`;

    // Encode message for URL
    const encodedMessage = encodeURIComponent(message);

    // Set WhatsApp link
    const whatsappNumber = "918969570204";
    const whatsappURL = `https://wa.me/${whatsappNumber}?text=${encodedMessage}`;

    // Redirect to WhatsApp
    window.open(whatsappURL, '_blank');

    // Optionally clear cart after redirect
    localStorage.removeItem("cart");
    cart = [];
    loadCart();
}
function openProduct(imgSrc) {
    // encode URI components to safely pass them in the URL
    const encodedImg = encodeURIComponent(imgSrc);
    window.location.href = `sproduct.html?img=${encodedImg}`;
}
function addToCart(name, price, image) {
    alert(`Added "${name}" to cart for Rs ${price}`);
  }
  