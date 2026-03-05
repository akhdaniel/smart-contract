#!/bin/bash

# Deployment script for Vue Portal
# Run this script from the server: /mnt/disk2/odoo17/smc/vit-portal-vue/

echo "🚀 Starting Vue Portal deployment..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from vit-portal-vue directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Build the application
echo "🔨 Building application..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Error: Build failed - dist directory not found"
    exit 1
fi

# Ask for Odoo static directory
echo "📁 Where is your Odoo vit_portal static directory?"
echo "Example: /mnt/disk2/odoo17/addons17/vit_portal/static"
read -p "Enter path: " ODOO_STATIC_DIR

if [ ! -d "$ODOO_STATIC_DIR" ]; then
    echo "❌ Error: Directory $ODOO_STATIC_DIR does not exist"
    exit 1
fi

# Deploy files
echo "📤 Deploying files to $ODOO_STATIC_DIR..."
cp -r dist/* "$ODOO_STATIC_DIR/"

echo "✅ Deployment completed successfully!"
echo "🔄 Please restart your Odoo server and clear browser cache"
echo "🌐 Test the application and check browser console for any errors"