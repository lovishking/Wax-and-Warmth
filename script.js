const bar = document.getElementById('bar');
const close = document.getElementById('close');
const nav = document.getElementById('navbar');

if (bar){
  bar.addEventListener('click', () =>{
    nav.classList.add('active');
  })
}

if (close){
  close.addEventListener('click', () =>{
    nav.classList.remove('active');
  })
}



// Add to Cart function (with quantity)
function addToCart(name, price, image, quantity = 1) {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
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
  
  // Add to Cart from product card element
  function addToCartFromElement(cartIcon) {
    const productCard = cartIcon.closest(".p");
    const imgElement = productCard.querySelector("img");
  
    const name = imgElement.getAttribute("data-name");
    const price = parseFloat(imgElement.getAttribute("data-price"));
    const image = imgElement.getAttribute("data-image");
  
    addToCart(name, price, image);
  }
  
  // Display cart items in cart table
  function displayCartTable() {
    const cartBody = document.getElementById("cart-body");
    const totalAmountDiv = document.getElementById("total-amount");
  
    if (!cartBody) return;
  
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    cartBody.innerHTML = "";
    let total = 0;
  
    cart.forEach((item, index) => {
      const subtotal = item.price * item.quantity;
      total += subtotal;
  
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><i class="fa-solid fa-trash" style="cursor:pointer;" onclick="removeItem(${index})"></i></td>
        <td><img src="${item.image}" alt="${item.name}" width="80"></td>
        <td>${item.name}</td>
        <td>₹${item.price}</td>
        <td>
          <input type="number" min="1" value="${item.quantity}" style="width:50px;" onchange="updateQuantity(${index}, this.value)">
        </td>
        <td>₹${subtotal}</td>
      `;
      cartBody.appendChild(row);
    });
  
    if (cart.length === 0) {
      cartBody.innerHTML = `<tr><td colspan="6">Your cart is empty</td></tr>`;
    }
  
    if (totalAmountDiv) {
      totalAmountDiv.textContent = `Total: ₹${total}`;
    }
  }
  
  // Remove item from cart
  function removeItem(index) {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart.splice(index, 1);
    localStorage.setItem("cart", JSON.stringify(cart));
    displayCartTable();
  }
  
  // Update quantity of a product
  function updateQuantity(index, newQuantity) {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    cart[index].quantity = parseInt(newQuantity);
    localStorage.setItem("cart", JSON.stringify(cart));
    displayCartTable();
  }
  
  // Checkout via WhatsApp
  function checkout() {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
  
    if (cart.length === 0) {
      alert("Your cart is empty!");
      return;
    }
  
    let message = "Hello! I'd like to order:\n\n";
    let total = 0;
  
    cart.forEach(item => {
      message += `${item.name} - ₹${item.price} x ${item.quantity}\n`;
      total += item.price * item.quantity;
    });
  
    message += `\nTotal: ₹${total}\n\nThank you!`;
  
    const whatsappURL = `https://wa.me/918969570204?text=${encodeURIComponent(message)}`;
    window.open(whatsappURL, "_blank");
  
    localStorage.removeItem("cart");
    displayCartTable();
  }
  
  // Open single product page with query params
  function openProduct(imgSrc, name, price) {
    const encodedImg = encodeURIComponent(imgSrc);
    const encodedName = encodeURIComponent(name);
    const encodedPrice = encodeURIComponent(price);
    window.location.href = `sproduct.html?img=${encodedImg}&name=${encodedName}&price=${encodedPrice}`;
  }
  
  // When product image clicked — open product detail page
  function handleProductClick(imgElement) {
    const name = imgElement.getAttribute("data-name");
    const price = parseFloat(imgElement.getAttribute("data-price"));
    const image = imgElement.getAttribute("data-image");
  
    openProduct(image, name, price);
  }
  
  // On single product page: load product details from query string
  function loadProductDetails() {
    const params = new URLSearchParams(window.location.search);
    const imgSrc = decodeURIComponent(params.get("img"));
    const name = decodeURIComponent(params.get("name"));
    const price = decodeURIComponent(params.get("price"));
  
    const imgElement = document.getElementById("product-img");
    const nameElement = document.getElementById("product-name");
    const priceElement = document.getElementById("product-price");
  
    if (imgElement) imgElement.src = imgSrc;
    if (nameElement) nameElement.textContent = name;
    if (priceElement) priceElement.textContent = `₹${price}`;
  }
  
  // Load cart items if on cart page
  window.addEventListener("DOMContentLoaded", () => {
    displayCartTable();
    loadProductDetails();
  });

  let selectedProduct = {};
function addToCartFromElement(el) {
  const productCard = el.closest(".p");
  selectedProduct = {
    name: productCard.querySelector("img").getAttribute("data-name"),
    price: productCard.querySelector("img").getAttribute("data-price"),
    image: productCard.querySelector("img").getAttribute("data-image")
  };

  document.getElementById("dialogProductName").innerText = selectedProduct.name;
  document.getElementById("quantity").value = 1;
  document.getElementById("cartDialog").style.display = "flex";
}

function confirmAddToCart() {
  const quantity = parseInt(document.getElementById("quantity").value);
  const product = { ...selectedProduct, quantity };

  // Retrieve existing cart from localStorage
  let cart = JSON.parse(localStorage.getItem("cart")) || [];

  // Check if product already exists in cart
  const existingProduct = cart.find(item => item.name === product.name);
  if (existingProduct) {
    existingProduct.quantity += quantity;
  } else {
    cart.push(product);
  }

  // Save updated cart to localStorage
  localStorage.setItem("cart", JSON.stringify(cart));

  alert(`${quantity} x ${product.name} added to cart.`);
  closeDialog();
}


function closeDialog() {
  document.getElementById("cartDialog").style.display = "none";
}


document.querySelectorAll('.p').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = (y - centerY) / 15;
    const rotateY = (x - centerX) / 15;
    card.style.transform = `rotateX(${-rotateX}deg) rotateY(${rotateY}deg) scale(1.03)`;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = `rotateX(0deg) rotateY(0deg) scale(1)`;
  });
});

