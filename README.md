# Vertex Electronics | Order Sync & Insurance Middleware

## Project Overview
This middleware microservice is designed for Vertex Electronics, a high-volume consumer tech retailer. It serves as the critical bridge between the Shopify e-commerce platform and internal Shipping Insurance Manifest systems.

The service listens for real-time `orders/create` events via Webhooks, parses sensitive customer and transaction data, and formats payloads for immediate insurance coverage on high-value shipments (laptops, monitors, peripherals).

## System Architecture

```mermaid
graph LR
    A[Shopify Store - Vertex Electronics] -- Webhook Event (JSON) --> B(Internet Gateway)
    B -- Secure POST --> C{AWS EC2 / Ngrok Middleware}
    C -- 1. HMAC Verification --> D[Python Flask Service]
    D -- 2. Parse & Extract --> E[Shipping Manifest Log / Database]
    D -- 200 OK --> A
    
    style A fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style C fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    style D fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
