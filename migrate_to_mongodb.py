#!/usr/bin/env python3
"""
Migration script to transfer data from SQLite to MongoDB
Run this script if you have existing data in SQLite that you want to transfer to MongoDB
"""

import sqlite3
from pymongo import MongoClient
import os
import certifi

def migrate_sqlite_to_mongodb():
    """Migrate data from SQLite to MongoDB"""
    
    # MongoDB Configuration
    MONGO_URI = "mongodb+srv://admin:Ans%23umaan2003@cluster0.jssosyw.mongodb.net/herbal_website?retryWrites=true&w=majority&appName=Cluster0"
    DB_NAME = "herbal_website"
    COLLECTION_NAME = "products"
    
    # SQLite database path - using the correct one from the project
    SQLITE_DB = "products.db" 
    
    try:
        # Connect to MongoDB with SSL certificate fix
        print("🔌 Connecting to MongoDB...")
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        client.admin.command('ping')
        db = client[DB_NAME]
        products_collection = db[COLLECTION_NAME]
        print("✅ MongoDB connected successfully!")
        
        # Check if SQLite database exists
        if not os.path.exists(SQLITE_DB):
            # Try alternate path just in case
            if os.path.exists("database.db"):
                SQLITE_DB = "database.db"
            else:
                print(f"❌ SQLite database '{SQLITE_DB}' not found.")
                print("No migration needed - starting fresh with MongoDB!")
                return
        
        # Connect to SQLite
        print(f"🔌 Connecting to SQLite ({SQLITE_DB})...")
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        sqlite_cursor = sqlite_conn.cursor()
        
        # Get all products from SQLite
        sqlite_cursor.execute("SELECT * FROM products")
        sqlite_products = sqlite_cursor.fetchall()
        
        if not sqlite_products:
            print("ℹ️ No products found in SQLite database.")
            return
        
        print(f"📦 Found {len(sqlite_products)} products in SQLite database.")
        
        # Check if MongoDB collection already has data
        mongo_count = products_collection.count_documents({})
        if mongo_count > 0:
            print(f"⚠️ MongoDB collection already has {mongo_count} products.")
            response = input("Do you want to overwrite existing data? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled.")
                return
            else:
                # Clear existing data
                products_collection.delete_many({})
                print("🗑️ Cleared existing MongoDB data.")
        
        # Migrate each product
        migrated_count = 0
        for product in sqlite_products:
            # SQLite format: (id, name, description, price, image)
            product_data = {
                'name': product[1],
                'description': product[2],
                'price': product[3],
                'image': product[4]
            }
            
            # Insert into MongoDB
            products_collection.insert_one(product_data)
            migrated_count += 1
            print(f"✅ Migrated: {product[1]}")
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"📊 Migrated {migrated_count} products from SQLite to MongoDB")
        
        # Close connections
        sqlite_conn.close()
        client.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nPossible solutions:")
        print("1. Ensure your IP address is whitelisted in MongoDB Atlas.")
        print("2. Check your internet connection.")

if __name__ == "__main__":
    print("🚀 Starting SQLite to MongoDB migration...")
    migrate_sqlite_to_mongodb()
    print("✨ Migration script completed!")
