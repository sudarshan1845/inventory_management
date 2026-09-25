-- my_data.sql
-- Inserts your personal categories, suppliers, and products
-- Run with: mysql -u root -p inventory_db < my_data.sql
-- OR from inside the mysql shell: source C:\path\to\my_data.sql

USE inventory_db;

-- Categories (existing ones are skipped automatically via INSERT IGNORE)
INSERT IGNORE INTO categories (name) VALUES
('Electronics'), ('Accessories'), ('Bags'), ('Stationery'),
('Office Supplies'), ('Electrical'), ('Appliances'), ('Kitchen'),
('Furniture'), ('Computer Parts'), ('Storage'), ('Printer Supplies');

-- Suppliers
INSERT IGNORE INTO suppliers (name) VALUES
('ABC Electronics'), ('XYZ Traders'), ('Tech World'), ('Mobile Hub'),
('Office Mart'), ('Bag House'), ('Stationery Hub'), ('Electrical Hub'),
('Home Supplies'), ('Kitchen World'), ('Furniture World'), ('Computer World'),
('Print Solutions');

-- Products
-- (price = selling price, cost_price set to 80% of price as a placeholder since
--  your sheet didn't include cost price -- edit later if you want exact costs)
INSERT INTO products (name, category_id, supplier_id, price, cost_price, quantity, min_stock)
VALUES
('Wireless Mouse', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='ABC Electronics'), 599, 479.20, 25, 10),
('USB Keyboard', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='XYZ Traders'), 899, 719.20, 18, 8),
('Bluetooth Speaker', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='ABC Electronics'), 1499, 1199.20, 12, 5),
('USB-C Cable', (SELECT id FROM categories WHERE name='Accessories'), (SELECT id FROM suppliers WHERE name='Tech World'), 299, 239.20, 45, 15),
('HDMI Cable', (SELECT id FROM categories WHERE name='Accessories'), (SELECT id FROM suppliers WHERE name='Tech World'), 450, 360.00, 22, 8),
('Power Bank 10000mAh', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='Mobile Hub'), 999, 799.20, 16, 6),
('Wireless Earbuds', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='Mobile Hub'), 1799, 1439.20, 9, 10),
('Laptop Stand', (SELECT id FROM categories WHERE name='Accessories'), (SELECT id FROM suppliers WHERE name='Office Mart'), 799, 639.20, 14, 5),
('Webcam HD', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='Tech World'), 1299, 1039.20, 11, 5),
('USB Hub', (SELECT id FROM categories WHERE name='Accessories'), (SELECT id FROM suppliers WHERE name='XYZ Traders'), 549, 439.20, 27, 10),
('Laptop Backpack', (SELECT id FROM categories WHERE name='Bags'), (SELECT id FROM suppliers WHERE name='Bag House'), 1199, 959.20, 20, 7),
('Office Backpack', (SELECT id FROM categories WHERE name='Bags'), (SELECT id FROM suppliers WHERE name='Bag House'), 899, 719.20, 15, 5),
('Travel Bag', (SELECT id FROM categories WHERE name='Bags'), (SELECT id FROM suppliers WHERE name='Bag House'), 1599, 1279.20, 8, 5),
('Notebook A4', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Office Mart'), 80, 64.00, 75, 20),
('Notebook A5', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Office Mart'), 60, 48.00, 65, 15),
('Ball Pen Blue', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Stationery Hub'), 10, 8.00, 150, 30),
('Ball Pen Black', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Stationery Hub'), 10, 8.00, 120, 30),
('Gel Pen', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Stationery Hub'), 15, 12.00, 90, 20),
('Pencil HB', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Stationery Hub'), 8, 6.40, 200, 40),
('Eraser', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Stationery Hub'), 5, 4.00, 180, 40),
('Sharpener', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Stationery Hub'), 7, 5.60, 100, 25),
('Marker Pen', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Office Mart'), 25, 20.00, 70, 15),
('Whiteboard Marker', (SELECT id FROM categories WHERE name='Stationery'), (SELECT id FROM suppliers WHERE name='Office Mart'), 30, 24.00, 55, 15),
('Stapler', (SELECT id FROM categories WHERE name='Office Supplies'), (SELECT id FROM suppliers WHERE name='Office Mart'), 120, 96.00, 32, 10),
('Stapler Pins', (SELECT id FROM categories WHERE name='Office Supplies'), (SELECT id FROM suppliers WHERE name='Office Mart'), 35, 28.00, 85, 20),
('Paper Clips', (SELECT id FROM categories WHERE name='Office Supplies'), (SELECT id FROM suppliers WHERE name='Office Mart'), 25, 20.00, 100, 25),
('Calculator', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='ABC Electronics'), 350, 280.00, 28, 10),
('Extension Board', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='Electrical Hub'), 699, 559.20, 17, 6),
('LED Bulb 9W', (SELECT id FROM categories WHERE name='Electrical'), (SELECT id FROM suppliers WHERE name='Electrical Hub'), 120, 96.00, 50, 15),
('LED Bulb 12W', (SELECT id FROM categories WHERE name='Electrical'), (SELECT id FROM suppliers WHERE name='Electrical Hub'), 160, 128.00, 42, 15),
('LED Tube Light', (SELECT id FROM categories WHERE name='Electrical'), (SELECT id FROM suppliers WHERE name='Electrical Hub'), 450, 360.00, 20, 8),
('Table Lamp', (SELECT id FROM categories WHERE name='Electrical'), (SELECT id FROM suppliers WHERE name='Electrical Hub'), 799, 639.20, 13, 5),
('Ceiling Fan', (SELECT id FROM categories WHERE name='Electrical'), (SELECT id FROM suppliers WHERE name='Home Supplies'), 2499, 1999.20, 7, 5),
('Electric Kettle', (SELECT id FROM categories WHERE name='Appliances'), (SELECT id FROM suppliers WHERE name='Home Supplies'), 1299, 1039.20, 10, 5),
('Mixer Grinder', (SELECT id FROM categories WHERE name='Appliances'), (SELECT id FROM suppliers WHERE name='Home Supplies'), 2499, 1999.20, 6, 4),
('Water Bottle 1L', (SELECT id FROM categories WHERE name='Kitchen'), (SELECT id FROM suppliers WHERE name='Home Supplies'), 199, 159.20, 60, 20),
('Steel Bottle', (SELECT id FROM categories WHERE name='Kitchen'), (SELECT id FROM suppliers WHERE name='Home Supplies'), 399, 319.20, 35, 10),
('Coffee Mug', (SELECT id FROM categories WHERE name='Kitchen'), (SELECT id FROM suppliers WHERE name='Kitchen World'), 149, 119.20, 45, 15),
('Lunch Box', (SELECT id FROM categories WHERE name='Kitchen'), (SELECT id FROM suppliers WHERE name='Kitchen World'), 299, 239.20, 28, 10),
('Glass Set', (SELECT id FROM categories WHERE name='Kitchen'), (SELECT id FROM suppliers WHERE name='Kitchen World'), 349, 279.20, 20, 8),
('Office Chair', (SELECT id FROM categories WHERE name='Furniture'), (SELECT id FROM suppliers WHERE name='Furniture World'), 4999, 3999.20, 8, 3),
('Study Table', (SELECT id FROM categories WHERE name='Furniture'), (SELECT id FROM suppliers WHERE name='Furniture World'), 6999, 5599.20, 5, 2),
('Plastic Chair', (SELECT id FROM categories WHERE name='Furniture'), (SELECT id FROM suppliers WHERE name='Furniture World'), 999, 799.20, 18, 5),
('Bookshelf', (SELECT id FROM categories WHERE name='Furniture'), (SELECT id FROM suppliers WHERE name='Furniture World'), 3999, 3199.20, 6, 3),
('Monitor 24 Inch', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='Computer World'), 8999, 7199.20, 7, 3),
('Gaming Keyboard', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='Computer World'), 1999, 1599.20, 10, 4),
('Gaming Mouse', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='Computer World'), 1499, 1199.20, 13, 5),
('Laptop Cooling Pad', (SELECT id FROM categories WHERE name='Accessories'), (SELECT id FROM suppliers WHERE name='Computer World'), 899, 719.20, 16, 5),
('SSD 500GB', (SELECT id FROM categories WHERE name='Computer Parts'), (SELECT id FROM suppliers WHERE name='Computer World'), 3999, 3199.20, 8, 3),
('RAM 8GB', (SELECT id FROM categories WHERE name='Computer Parts'), (SELECT id FROM suppliers WHERE name='Computer World'), 2299, 1839.20, 11, 4),
('Pendrive 32GB', (SELECT id FROM categories WHERE name='Storage'), (SELECT id FROM suppliers WHERE name='Tech World'), 499, 399.20, 30, 10),
('Pendrive 64GB', (SELECT id FROM categories WHERE name='Storage'), (SELECT id FROM suppliers WHERE name='Tech World'), 699, 559.20, 24, 8),
('Memory Card 64GB', (SELECT id FROM categories WHERE name='Storage'), (SELECT id FROM suppliers WHERE name='Mobile Hub'), 799, 639.20, 18, 6),
('External HDD 1TB', (SELECT id FROM categories WHERE name='Storage'), (SELECT id FROM suppliers WHERE name='Computer World'), 4999, 3999.20, 6, 3),
('Printer Ink Black', (SELECT id FROM categories WHERE name='Printer Supplies'), (SELECT id FROM suppliers WHERE name='Print Solutions'), 899, 719.20, 14, 5),
('Printer Ink Color', (SELECT id FROM categories WHERE name='Printer Supplies'), (SELECT id FROM suppliers WHERE name='Print Solutions'), 999, 799.20, 10, 4),
('A4 Paper Ream', (SELECT id FROM categories WHERE name='Office Supplies'), (SELECT id FROM suppliers WHERE name='Office Mart'), 350, 280.00, 40, 10),
('File Folder', (SELECT id FROM categories WHERE name='Office Supplies'), (SELECT id FROM suppliers WHERE name='Stationery Hub'), 45, 36.00, 90, 20),
('Document Folder', (SELECT id FROM categories WHERE name='Office Supplies'), (SELECT id FROM suppliers WHERE name='Stationery Hub'), 80, 64.00, 60, 15),
('Calculator Scientific', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='ABC Electronics'), 699, 559.20, 9, 5),
('Power Strip', (SELECT id FROM categories WHERE name='Electrical'), (SELECT id FROM suppliers WHERE name='Electrical Hub'), 599, 479.20, 21, 8),
('Phone Stand', (SELECT id FROM categories WHERE name='Accessories'), (SELECT id FROM suppliers WHERE name='Mobile Hub'), 299, 239.20, 34, 10),
('Screen Cleaning Kit', (SELECT id FROM categories WHERE name='Accessories'), (SELECT id FROM suppliers WHERE name='Tech World'), 199, 159.20, 40, 10),
('Smartphone Tripod', (SELECT id FROM categories WHERE name='Accessories'), (SELECT id FROM suppliers WHERE name='Mobile Hub'), 899, 719.20, 12, 5),
('Ring Light', (SELECT id FROM categories WHERE name='Electronics'), (SELECT id FROM suppliers WHERE name='Mobile Hub'), 1499, 1199.20, 7, 5);
