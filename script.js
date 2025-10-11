const bar = document.getElementById('bar');
const close = document.getElementById('close');
const nav = document.getElementById('navbar');

if (bar){
  bar.addEventListener('click', () =>{
    nav.classList.add('active');
  });
}

if (close){
  close.addEventListener('click', () =>{
    nav.classList.remove('active');
  });
}

// Add to Cart function (with quantity)
function addToCart(name, price, image, quantity = 1) {
  try {
    console.log('addToCart called:', { name, price, image, quantity });
    
    // Check localStorage availability
    if (typeof Storage === "undefined") {
      console.error('LocalStorage not available');
      alert('Your browser does not support storage. Cart won\'t work.');
      return;
    }
    
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const existingProduct = cart.find(item => item.name === name);

    if (existingProduct) {
      existingProduct.quantity += quantity;
      console.log('Updated existing product quantity');
    } else {
      const product = { name, price, image, quantity };
      cart.push(product);
      console.log('Added new product to cart');
    }

    localStorage.setItem("cart", JSON.stringify(cart));
    console.log('Cart updated in localStorage:', cart);
    
    // Mobile-friendly notification
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (isMobile) {
      // Quick visual feedback instead of alert for mobile
      const notification = document.createElement('div');
      notification.textContent = `${name} added to cart!`;
      notification.style.cssText = `
        position: fixed; 
        top: 20px; 
        right: 20px; 
        background: green; 
        color: white; 
        padding: 10px; 
        border-radius: 5px; 
        z-index: 9999;
        font-size: 14px;
      `;
      document.body.appendChild(notification);
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 2000);
    }
    
  } catch (error) {
    console.error('Error in addToCart:', error);
    alert('Error adding item to cart');
  }
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

  const whatsappURL = `https://wa.me/916200835077?text=${encodeURIComponent(message)}`;
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

// Dialog logic
let selectedProduct = {};
function addToCartFromElement(el) {
  // Check if it's the new modern card design
  let productCard = el.closest(".modern-product-card");
  let name, price, image;
  
  if (productCard) {
    // Modern card design - get data from button attributes
    name = el.getAttribute("data-name");
    price = el.getAttribute("data-price");
    image = el.getAttribute("data-image");
  } else {
    // Legacy card design - get data from image element
    productCard = el.closest(".p");
    if (productCard) {
      const imgElement = productCard.querySelector("img");
      name = imgElement.getAttribute("data-name");
      price = imgElement.getAttribute("data-price");
      image = imgElement.getAttribute("data-image");
    }
  }

  if (!name || !price || !image) {
    console.error('Missing product data for dialog');
    return;
  }

  selectedProduct = {
    name: name,
    price: price,
    image: image
  };

  document.getElementById("dialogProductName").innerText = selectedProduct.name;
  document.getElementById("quantity").value = 1;
  document.getElementById("cartDialog").style.display = "flex";
}

function confirmAddToCart() {
  const quantity = parseInt(document.getElementById("quantity").value);
  const product = { ...selectedProduct, quantity };

  let cart = JSON.parse(localStorage.getItem("cart")) || [];

  const existingProduct = cart.find(item => item.name === product.name);
  if (existingProduct) {
    existingProduct.quantity += quantity;
  } else {
    cart.push(product);
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  
  // Show success feedback
  if (window.showNotification) {
    showNotification(`${quantity} x ${product.name} added to cart!`, "success");
  }
  
  closeDialog();
}

function closeDialog() {
  document.getElementById("cartDialog").style.display = "none";
}

// 3D card effect
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

// Testimonials carousel
const testimonials = document.querySelectorAll('.testimonial');
let currentIndex = 0;
let autoSlideInterval = setInterval(showNextTestimonial, 5000); // Change every 5 seconds

function showTestimonial(index) {
  testimonials.forEach((t, i) => {
    t.classList.toggle('active', i === index);
  });
}

function showNextTestimonial() {
  currentIndex = (currentIndex + 1) % testimonials.length;
  showTestimonial(currentIndex);
}

function showPrevTestimonial() {
  currentIndex = (currentIndex - 1 + testimonials.length) % testimonials.length;
  showTestimonial(currentIndex);
}

document.getElementById('nextBtn').addEventListener('click', () => {
  showNextTestimonial();
  resetAutoSlide();
});

document.getElementById('prevBtn').addEventListener('click', () => {
  showPrevTestimonial();
  resetAutoSlide();
});

function resetAutoSlide() {
  clearInterval(autoSlideInterval);
  autoSlideInterval = setInterval(showNextTestimonial, 5000);
}

// Initialize first testimonial
showTestimonial(currentIndex);

// Dynamic Product Loading from Admin Dashboard
function loadAdminProducts() {
  const adminProducts = JSON.parse(localStorage.getItem('websiteProducts') || '[]');
  
  if (adminProducts.length === 0) {
    console.log('No admin products found, keeping default products');
    return;
  }
  
  const productContainer = document.querySelector('#pro1 .procont');
  if (!productContainer) {
    console.log('Product container not found');
    return;
  }
  
  // Clear existing products (but keep first few as fallback)
  // productContainer.innerHTML = '';
  
  // Create HTML for admin products
  const adminProductsHTML = adminProducts.map(product => `
    <div class="pc">
      <div class="p">
        <img src="${product.image}" alt="${product.name}"
          data-name="${product.name}" data-price="${product.price}"
          data-image="${product.image}"
          onclick="handleProductClick(this)" style="cursor: pointer;">
        <div class="prod">
          <div class="des">
            <span>${product.name}</span>
            <h5>₹${product.price}/-</h5>
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
  `).join('');
  
  // Append admin products to existing ones
  productContainer.innerHTML += adminProductsHTML;
  
  console.log(`Loaded ${adminProducts.length} admin products`);
}

// Listen for product updates from admin dashboard
window.addEventListener('productsUpdated', function(event) {
  console.log('Products updated event received');
  loadAdminProducts();
});

// Load admin products when page loads
document.addEventListener('DOMContentLoaded', function() {
  loadAdminProducts();
});

// For mobile: Handle storage events across tabs/windows
window.addEventListener('storage', function(e) {
  if (e.key === 'websiteProducts') {
    console.log('Storage event detected for products');
    loadAdminProducts();
  }
});

// Testimonial Auto-Scroll for Mobile
function initTestimonialAutoScroll() {
  const testimonialGrid = document.querySelector('.testimonial-grid');
  const testimonialCards = document.querySelectorAll('.testimonial-card');
  
  if (!testimonialGrid || testimonialCards.length === 0) return;
  
  // Check if it's mobile view
  function isMobileView() {
    return window.innerWidth <= 477;
  }
  
  let currentIndex = 0;
  let autoScrollInterval;
  
  function startAutoScroll() {
    if (!isMobileView()) return;
    
    autoScrollInterval = setInterval(() => {
      currentIndex = (currentIndex + 1) % testimonialCards.length;
      const scrollPosition = currentIndex * 300; // 280px card width + 20px gap
      
      testimonialGrid.scrollTo({
        left: scrollPosition,
        behavior: 'smooth'
      });
    }, 4000); // Change every 4 seconds
  }
  
  function stopAutoScroll() {
    if (autoScrollInterval) {
      clearInterval(autoScrollInterval);
      autoScrollInterval = null;
    }
  }
  
  // Start/stop based on mobile view
  function handleResize() {
    if (isMobileView()) {
      testimonialGrid.style.overflowX = 'auto';
      startAutoScroll();
    } else {
      stopAutoScroll();
      testimonialGrid.style.overflowX = 'visible';
      testimonialGrid.scrollTo({ left: 0 });
    }
  }
  
  // Pause auto-scroll when user interacts
  testimonialGrid.addEventListener('touchstart', stopAutoScroll);
  testimonialGrid.addEventListener('scroll', () => {
    stopAutoScroll();
    // Restart after 3 seconds of no interaction
    setTimeout(() => {
      if (isMobileView()) startAutoScroll();
    }, 3000);
  });
  
  // Initialize
  handleResize();
  window.addEventListener('resize', handleResize);
}

// Initialize testimonial auto-scroll when DOM is loaded
document.addEventListener('DOMContentLoaded', initTestimonialAutoScroll);
