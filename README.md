# Shopify Insurance & Order Sync Service

## Overview
This microservice acts as a middleware between a **Shopify Store (Vertex Electronics)** and internal backend systems. It listens for real-time `orders/create` webhooks, parses transaction data, and prepares high-value shipments for insurance processing.

## System Architecture

```mermaid
graph LR
    A[Shopify Store] -- New Order Event --> B(Webhook)
    B -- JSON Payload --> C{Ngrok Tunnel}
    C -- Secure Forwarding --> D[Python Flask Service]
    D -- Extract Data --> E[Console Logs]
    D -- 200 OK --> A
    
    style A fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style D fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style C fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
