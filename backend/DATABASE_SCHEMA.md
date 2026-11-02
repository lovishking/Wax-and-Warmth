# Database schema

The Django apps use a normalized relational schema intended for PostgreSQL. The local development settings continue to use SQLite. `manage.py migrate` applies the same logical schema in either database.

```mermaid
erDiagram
    USER ||--o| CART : owns
    CART ||--o{ CART_ITEM : contains
    PRODUCT ||--o{ CART_ITEM : selected
    CATEGORY o|--o{ PRODUCT : classifies
    PRODUCT ||--|| INVENTORY : tracks
    PRODUCT ||--o{ INVENTORY_TRANSACTION : records
    USER o|--o{ INVENTORY_TRANSACTION : records
    USER ||--o{ ORDER : places
    ORDER ||--o{ ORDER_ITEM : contains
    PRODUCT o|--o{ ORDER_ITEM : references
    PRODUCT ||--o{ PRODUCT_FACET_ASSIGNMENT : tagged
    PRODUCT_FACET ||--o{ PRODUCT_FACET_ASSIGNMENT : assigned
    PRODUCT ||--o| CANDLE_KNOWLEDGE : describes

    USER {
        bigint id PK
        string email UK
        string role
        string phone
        string address
    }
    CATEGORY {
        bigint id PK
        string name UK
        string slug UK
        boolean is_active
    }
    PRODUCT {
        bigint id PK
        bigint category_id FK
        string slug UK
        decimal price
        string scent_family
        string size
        boolean is_active
        boolean is_featured
    }
    PRODUCT_FACET {
        bigint id PK
        string kind
        string value
        string normalized_value
    }
    PRODUCT_FACET_ASSIGNMENT {
        bigint id PK
        bigint product_id FK
        bigint facet_id FK
        int position
    }
    INVENTORY {
        bigint id PK
        bigint product_id FK_UK
        int quantity
        int reserved_quantity
        int reorder_level
    }
    INVENTORY_TRANSACTION {
        bigint id PK
        bigint product_id FK
        bigint created_by_id FK
        string transaction_type
        int quantity
        string reference_id
    }
    CART {
        bigint id PK
        bigint user_id FK_UK
    }
    CART_ITEM {
        bigint id PK
        bigint cart_id FK
        bigint product_id FK
        int quantity
    }
    ORDER {
        bigint id PK
        bigint user_id FK
        decimal total_amount
        string status
        datetime created_at
    }
    ORDER_ITEM {
        bigint id PK
        bigint order_id FK
        bigint product_id FK
        string product_name_snapshot
        int quantity
        decimal unit_price_snapshot
    }
    CANDLE_KNOWLEDGE {
        bigint id PK
        bigint product_id FK_UK
        text document
        json embedding
    }
```

Newsletter subscriptions and the singleton storefront settings are independent records and are not tied to a customer account:

- `newsletter_subscriptions`: unique normalized email, active state, unsubscribe token, subscription/update timestamps, and optional request metadata.
- `site_settings`: site name, description, contact email and phone. The primary key is constrained to `1`, so the table can hold only the singleton settings row.

`User` extends Django's `AbstractUser`, so the standard authentication group and permission tables and their many-to-many join tables are also part of the database. Django's password hasher stores credentials; the `role` field controls the application's customer/admin access checks.

## Integrity rules

- Prices and order item unit prices must be positive. Cart and order item quantities must be positive. Order totals cannot be negative.
- Inventory reserved quantity cannot exceed physical quantity; zero-value inventory transactions are rejected.
- Product facet values are unique within a facet kind after case folding. A product cannot receive the same facet twice, and the assignment position preserves display order.
- Cart has one row per user and one row per product per cart. Orders cannot be duplicated for the same product within one order.
- User and newsletter email uniqueness is case insensitive. Roles, order states, inventory transaction types, and facet kinds are constrained to supported values.
- Orders protect their customer records. Product deletion through the API archives the product (`is_active = false`), preserving inventory history and purchase snapshots. Order item product references may become null while the saved product name and price remain available.

## Normalization and snapshots

Product scent notes, moods, recommended rooms, and occasions are stored as typed `product_facets` joined through `product_facet_assignments`. The API keeps its existing comma-separated fields and list fields as a compatibility layer. A data migration copied the current product values into these tables before removing the old text columns.

`order_items.product_name` and `unit_price` deliberately snapshot catalog data at purchase time. Shipping details and `orders.total_amount` are likewise order-time values. `order_items.subtotal` is computed from quantity and unit price instead of stored again. `inventory_transactions.reference_id` remains text because it may identify an order or another operational reference; it is not always an order foreign key.

`candle_knowledge.embedding` remains JSON so the current recommendation service works in both local SQLite and PostgreSQL. It does not currently use a PostgreSQL vector index; moving semantic search to `pgvector` should be a separate performance change once catalog size justifies it.

## Indexes

- Unique indexes cover user email, category name/slug, product slug, newsletter email, facet kind/value, cart ownership, and product/cart and product/facet pairs.
- Product indexes support scent family, price sorting/ranges, and active/featured catalog queries. Facet indexes support typed lookups and ordered product assignments.
- Order indexes support a user's newest orders and status filtering. Inventory transaction indexes support product history and transaction type filtering. Newsletter indexes support active-subscription admin views.

The migrations are in each app's `migrations/` directory. The normalized product migration is reversible and restores the legacy API text fields when reversed. Migration files were applied to the local SQLite database; production PostgreSQL instances should apply them during deployment.
