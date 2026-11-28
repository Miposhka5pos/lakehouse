-- Examples for the incremental-without-CDC scenario.
-- These statements update current-state rows; intermediate changes between polls
-- are intentionally not retained by this source model.

-- Insert a customer.
INSERT INTO source_incremental.customers (customer_name, email, country)
VALUES ('Test Customer', 'test.customer@example.invalid', 'Finland')
RETURNING customer_id, updated_at;

-- Update an order. The trigger advances updated_at automatically.
-- Replace 1 with an existing order_id.
UPDATE source_incremental.orders
SET status = 'SHIPPED'
WHERE order_id = 1;

-- Soft-delete an order item. Do not physically DELETE the row.
-- Replace 1 with an existing order_item_id.
UPDATE source_incremental.order_items
SET is_deleted = TRUE
WHERE order_item_id = 1;

-- Restore a logically deleted order item.
UPDATE source_incremental.order_items
SET is_deleted = FALSE
WHERE order_item_id = 1;

-- Incremental extraction must include both active rows and tombstones:
-- SELECT *
-- FROM source_incremental.order_items
-- WHERE updated_at >= :last_watermark - INTERVAL '5 minutes'
--   AND updated_at <= :current_watermark;
