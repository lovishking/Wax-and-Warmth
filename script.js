// Initialize cart from localStorage or as empty array
let cart = JSON.parse(localStorage.getItem("cart")) || [];

// Add to Cart function (with quantity)
function addToCart(name, price, image, quantity = 1) {
    const existingProduct = cart.find(item => item.name === name);

    if (existingProduct) {
        existingProduct.quantity += quantity;
    } else {
        const product = { name, price, image, quantity };
        cart.push(product);
    }

    localStorage.setItem("cart", JSON.stringify(cart));
    alert(`${quantity} ${name} added to cart`);
}

// Load Cart items into cart page
function loadCart() {
    const cartBody = document.getElementById("cart-body");
    if (!cartBody) return;

    cartBody.innerHTML = "";
    let total = 0;

    cart.forEach((item, index) => {
        const subtotal = item.price * item.quantity;
        total += subtotal;

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

    if (cart.length === 0) {
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

// WhatsApp Checkout
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

    const encodedMessage = encodeURIComponent(message);
    const whatsappNumber = "918969570204";
    const whatsappURL = `https://wa.me/${whatsappNumber}?text=${encodedMessage}`;

    window.open(whatsappURL, '_blank');

    localStorage.removeItem("cart");
    cart = [];
    loadCart();
}

// Load Cart items on cart page load
window.onload = loadCart;

// Open Product Detail Page
function openProduct(imgSrc, name, price) {
    const encodedImg = encodeURIComponent(imgSrc);
    const encodedName = encodeURIComponent(name);
    const encodedPrice = encodeURIComponent(price);
    window.location.href = `sproduct.html?img=${encodedImg}&name=${encodedName}&price=${encodedPrice}`;
}
