# Wax and Warmth - Admin Panel Guide

## Overview

The admin panel allows you to manage products, view newsletter subscribers, and configure website settings. Products added through the admin panel will automatically appear on the home page and shop page.

## Access Instructions

### 1. Admin Login

- **URL**: `https://wax-and-warmth.shop/admin-login.html`
- **Username**: `admin`
- **Password**: `[PROTECTED - Contact admin for credentials]`
- **Quick Access**: Click "Admin" in the main navigation bar (located next to Contact)
- **Alternative Access**: Small "Admin" link in the footer of the main website

**Security Note**: Admin credentials are now encrypted and protected from inspection. The login system includes anti-debugging measures and session security.

### 2. Admin Dashboard Features

#### 🛍️ Product Management

- **Add New Products**: Upload images, set prices, descriptions, categories, and stock levels
- **Edit Existing Products**: Click "Edit" on any product to modify its details
- **Delete Products**: Remove products from the catalog
- **Image Upload**: Drag & drop or click to upload product images
- **Categories**: Candles, Wax Melts, Gift Sets, Custom
- **Automatic Integration**: Products automatically appear on home and shop pages

#### 📧 Newsletter Management

- **View Subscribers**: See all newsletter subscribers
- **Export Data**: Download subscriber information
- **Search Function**: Find specific subscribers
- **Statistics**: View subscription statistics

#### ⚙️ Website Settings

- **Site Information**: Update site name and description
- **Contact Details**: Modify contact email and phone number
- **Save Settings**: Apply changes to website configuration

### 3. Product Upload Process

1. **Login to Admin Dashboard**
2. **Navigate to Products Section** (default view)
3. **Fill Product Information**:
   - Product Name (required)
   - Price in ₹ (required)
   - Description (optional but recommended)
   - Category (required - select from dropdown)
   - Stock Quantity (required - default: 1)
4. **Upload Product Image**:
   - Click on upload area or drag & drop image
   - Supported formats: JPG, PNG, GIF, WebP
   - Image will be automatically resized and optimized
5. **Click "Add Product"**
6. **Verify**: Product appears in "Current Products" section
7. **Check Website**: Visit home page or shop page to see new product

### 4. Technical Details

#### Storage System

- **Local Storage**: Products are stored in browser's localStorage
- **Cross-Page Sync**: Products automatically sync across all website pages
- **Backup**: Export products as JSON for backup
- **Import**: Restore products from JSON backup

#### Image Handling

- **Format**: Images are converted to base64 and stored locally
- **Size**: No file size limit, but larger images may slow loading
- **Optimization**: Consider resizing images to 500x500px for best performance

#### Authentication

- **Enhanced Security**: Login system now uses encrypted credential validation
- **Session Management**: Secure session tokens with 24-hour expiration
- **Anti-Debugging**: Protection against developer tools and console inspection
- **Auto-Logout**: Sessions expire automatically for security
- **Encrypted Storage**: Credentials are hashed and obfuscated in code

### 5. Mobile Support

- **Responsive Design**: Admin panel works on mobile devices
- **Touch-Friendly**: All buttons and forms optimized for touch
- **Mobile Upload**: Camera integration for direct photo upload

### 6. Troubleshooting

#### Products Not Appearing on Website

1. Check if localStorage is enabled in browser
2. Refresh the home/shop page
3. Clear browser cache and reload
4. Verify product was successfully added in admin dashboard

#### Login Issues

1. Ensure correct username: `admin`
2. Ensure correct password: `waxandwarmth2025`
3. Clear browser cache
4. Try incognito/private browsing mode

#### Image Upload Problems

1. Check file format (must be image)
2. Try smaller file size
3. Ensure stable internet connection
4. Use different browser if issues persist

### 7. Best Practices

#### Product Management

- **High-Quality Images**: Use clear, well-lit product photos
- **Detailed Descriptions**: Include material, size, burn time, scent notes
- **Competitive Pricing**: Research market prices for similar products
- **Stock Management**: Keep stock levels updated to avoid overselling
- **Category Organization**: Use consistent categorization

#### Content Guidelines

- **Professional Descriptions**: Use proper grammar and spelling
- **Consistent Branding**: Maintain brand voice across all products
- **SEO-Friendly**: Use descriptive product names and keywords
- **Mobile-First**: Ensure descriptions are readable on mobile

### 8. Data Backup & Recovery

#### Regular Backups

1. Go to Settings section in admin dashboard
2. Export products data regularly
3. Save JSON files in secure location
4. Consider weekly backups for active catalogs

#### Recovery Process

1. Login to admin dashboard
2. Go to Settings section
3. Use import function to restore from JSON backup
4. Verify all products loaded correctly

### 9. Security Considerations

#### Access Control

- **Password Protection**: Keep admin password secure
- **Limited Access**: Only share credentials with authorized personnel
- **Regular Updates**: Consider changing password periodically
- **Logout**: Always logout when finished

#### Data Privacy

- **Newsletter Data**: Handle subscriber information responsibly
- **Local Storage**: Data is stored locally in browser
- **No Cloud Sync**: Products are not automatically backed up

### 10. Support & Maintenance

#### Contact Information

- **Email**: realwaxandwarmth@gmail.com
- **Phone**: +91 6200835077
- **WhatsApp**: Available for immediate support

#### Future Enhancements

- **Cloud Storage**: Potential integration with cloud services
- **Advanced Analytics**: Sales tracking and performance metrics
- **Multi-Admin**: Support for multiple admin accounts
- **API Integration**: Connect with e-commerce platforms

---

## Quick Start Checklist

- [ ] Access admin panel at `/admin-login.html`
- [ ] Login with provided credentials
- [ ] Navigate to Products section
- [ ] Add your first product with image
- [ ] Check product appears on main website
- [ ] Set up regular backup routine
- [ ] Configure website settings
- [ ] Test newsletter functionality

---

_This admin panel is designed to be simple yet powerful, allowing you to manage your Wax and Warmth product catalog efficiently while maintaining a professional online presence._
