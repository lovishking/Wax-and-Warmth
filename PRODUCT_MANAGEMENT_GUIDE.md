# Product Images Management Guide

## Overview

All product images and details are now centrally managed in the `product-images.js` file. This makes it easy to add, edit, or remove products that will automatically appear on both the home page and shop page.

## How to Add New Products

### Method 1: Edit the Configuration File

1. **Open** `product-images.js` file
2. **Find** the `PRODUCT_IMAGES` array
3. **Add** a new product object with this format:

```javascript
{
    id: 7, // Next available ID number
    name: "Your Product Name",
    image: "/products/your-image.jpg", // Path to your image
    price: 299, // Price in rupees
    description: "Product description here",
    category: "candles", // Options: candles, wax-melts, gift-sets, custom
    featured: true // true = shows on home page, false = only on shop page
}
```

### Method 2: Add Using JavaScript Console

1. **Open** your website in browser
2. **Press** F12 to open developer tools
3. **Go** to Console tab
4. **Type** this command:

```javascript
addNewProduct({
  name: "Your Product Name",
  image: "/products/your-image.jpg",
  price: 299,
  description: "Product description here",
  category: "candles",
  featured: true,
});
```

## Product Image Guidelines

### Image Requirements

- **Format**: JPG, PNG, GIF, or WebP
- **Size**: Recommended 500x500 pixels for best performance
- **Quality**: High resolution, well-lit product photos
- **Background**: Clean, neutral background preferred

### Image Placement

- **Upload** your product images to the `/products/` folder
- **Name** them descriptively (e.g., `lavender-candle.jpg`)
- **Reference** them in the configuration as `/products/filename.jpg`

## Product Categories

### Available Categories

- **candles**: Regular candles
- **wax-melts**: Wax melts and tarts
- **gift-sets**: Bundled products
- **custom**: Custom or personalized items

### Featured Products

- **featured: true** = Shows on home page and shop page
- **featured: false** = Shows only on shop page

## Example: Adding a New Product

### Step-by-Step Example

1. **Upload** image `rose-garden-candle.jpg` to `/products/` folder
2. **Open** `product-images.js`
3. **Add** this to the PRODUCT_IMAGES array:

```javascript
{
    id: 7,
    name: "Rose Garden Delight",
    image: "/products/rose-garden-candle.jpg",
    price: 349,
    description: "Elegant rose-scented candle with natural soy wax",
    category: "candles",
    featured: true
}
```

4. **Save** the file
5. **Refresh** your website - the product will appear automatically!

## Product Display Logic

### Home Page (index.html)

- Shows only products where `featured: true`
- Typically 6-8 products for best layout

### Shop Page (shop.html)

- Shows ALL products regardless of featured status
- Complete product catalog

## Editing Existing Products

### To Modify a Product

1. **Find** the product in `PRODUCT_IMAGES` array
2. **Change** any property (name, price, description, etc.)
3. **Save** the file
4. **Refresh** website to see changes

### To Remove a Product

1. **Find** the product object in `PRODUCT_IMAGES` array
2. **Delete** the entire object (including opening { and closing })
3. **Save** the file

## Advanced Features

### Filtering by Category

```javascript
// Get only candles
const candles = getProductsByCategory("candles");

// Get only featured products
const featured = getFeaturedProducts();

// Get all products
const all = getAllProducts();
```

### Adding Multiple Products at Once

```javascript
// Add multiple products
const newProducts = [
  {
    name: "Product 1",
    image: "/products/product1.jpg",
    price: 199,
    category: "candles",
    featured: true,
  },
  {
    name: "Product 2",
    image: "/products/product2.jpg",
    price: 299,
    category: "wax-melts",
    featured: false,
  },
];

// Add them all
newProducts.forEach((product) => addNewProduct(product));
```

## Troubleshooting

### Products Not Showing

1. **Check** image path is correct
2. **Verify** image file exists in `/products/` folder
3. **Ensure** JavaScript syntax is correct (no missing commas, brackets)
4. **Clear** browser cache and refresh

### Image Not Loading

1. **Verify** image file name matches exactly (case-sensitive)
2. **Check** image file isn't corrupted
3. **Try** different image format
4. **Ensure** image is in `/products/` folder

### Layout Issues

1. **Resize** images to consistent dimensions
2. **Keep** product names reasonably short
3. **Test** on mobile devices
4. **Check** CSS isn't overriding styles

## Best Practices

### Product Names

- Keep under 20 characters for mobile compatibility
- Use descriptive, searchable names
- Avoid special characters

### Pricing

- Use whole numbers (no decimals)
- Keep competitive with market rates
- Update regularly for promotions

### Descriptions

- Include key features (scent, material, size)
- Mention burn time for candles
- Use selling language but stay factual

### Organization

- Group similar products together in the array
- Use consistent naming conventions
- Comment complex products for clarity

---

## Quick Reference

### File Structure

```
/product-images.js          ← Product configuration
/products/                  ← Image folder
  ├── product1.jpg
  ├── product2.jpg
  └── ...
/index.html                 ← Home page (shows featured)
/shop.html                  ← Shop page (shows all)
```

### Essential Commands

- **Add Product**: Edit `PRODUCT_IMAGES` array
- **Refresh Site**: Save file + refresh browser
- **Debug**: F12 → Console → Check for errors

This centralized system makes managing your product catalog simple and efficient!
