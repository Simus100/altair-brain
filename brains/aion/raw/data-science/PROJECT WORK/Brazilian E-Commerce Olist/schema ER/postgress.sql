CREATE TABLE "olist_customers_dataset" (
  "customer_id" varchar PRIMARY KEY,
  "customer_unique_id" varchar,
  "customer_zip_code_prefix" int,
  "customer_city" varchar,
  "customer_state" varchar
);

CREATE TABLE "olist_orders_dataset" (
  "order_id" varchar PRIMARY KEY,
  "customer_id" varchar,
  "order_status" varchar,
  "order_purchase_timestamp" timestamp,
  "order_approved_at" timestamp,
  "order_delivered_carrier_date" timestamp,
  "order_delivered_customer_date" timestamp,
  "order_estimated_delivery_date" timestamp
);

CREATE TABLE "olist_order_items_dataset" (
  "order_id" varchar,
  "order_item_id" int,
  "product_id" varchar,
  "seller_id" varchar,
  "shipping_limit_date" timestamp,
  "price" decimal,
  "freight_value" decimal,
  PRIMARY KEY ("order_id", "order_item_id")
);

CREATE TABLE "olist_products_dataset" (
  "product_id" varchar PRIMARY KEY,
  "product_category_name" varchar,
  "product_name_lenght" int,
  "product_description_lenght" int,
  "product_photos_qty" int,
  "product_weight_g" int,
  "product_length_cm" int,
  "product_height_cm" int,
  "product_width_cm" int
);

CREATE TABLE "product_category_name_translation" (
  "product_category_name" varchar PRIMARY KEY,
  "product_category_name_english" varchar
);

CREATE TABLE "olist_sellers_dataset" (
  "seller_id" varchar PRIMARY KEY,
  "seller_zip_code_prefix" int,
  "seller_city" varchar,
  "seller_state" varchar
);

CREATE TABLE "olist_order_payments_dataset" (
  "order_id" varchar,
  "payment_sequential" int,
  "payment_type" varchar,
  "payment_installments" int,
  "payment_value" decimal,
  PRIMARY KEY ("order_id", "payment_sequential")
);

CREATE TABLE "olist_order_reviews_dataset" (
  "review_id" varchar PRIMARY KEY,
  "order_id" varchar,
  "review_score" int,
  "review_comment_title" varchar,
  "review_comment_message" text,
  "review_creation_date" timestamp,
  "review_answer_timestamp" timestamp
);

CREATE TABLE "olist_geolocation_dataset" (
  "geolocation_zip_code_prefix" int PRIMARY KEY,
  "geolocation_lat" decimal,
  "geolocation_lng" decimal,
  "geolocation_city" varchar,
  "geolocation_state" varchar
);

COMMENT ON TABLE "olist_customers_dataset" IS 'customer_unique_id identifica il cliente reale; customer_id identifica l’istanza cliente collegata all’ordine.';

COMMENT ON TABLE "olist_order_items_dataset" IS 'La chiave primaria è composta: order_id identifica l’ordine, order_item_id identifica la riga dentro quell’ordine.';

COMMENT ON TABLE "olist_products_dataset" IS 'Nel CSV grezzo alcune categorie sono mancanti o non presenti nella tabella di traduzione; la FK va applicata dopo pulizia.';

COMMENT ON TABLE "olist_order_payments_dataset" IS 'La chiave primaria è composta: un ordine può avere più pagamenti.';

COMMENT ON TABLE "olist_order_reviews_dataset" IS 'Nel CSV grezzo review_id presenta duplicati; nel modello finale viene trattato come PK dopo deduplicazione in fase di staging.';

COMMENT ON TABLE "olist_geolocation_dataset" IS 'Nel CSV grezzo geolocation_zip_code_prefix non è univoco. Questa tabella rappresenta la versione normalizzata, con una sola riga per CAP.';

ALTER TABLE "olist_customers_dataset" ADD FOREIGN KEY ("customer_zip_code_prefix") REFERENCES "olist_geolocation_dataset" ("geolocation_zip_code_prefix") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "olist_orders_dataset" ADD FOREIGN KEY ("customer_id") REFERENCES "olist_customers_dataset" ("customer_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "olist_order_items_dataset" ADD FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "olist_order_items_dataset" ADD FOREIGN KEY ("product_id") REFERENCES "olist_products_dataset" ("product_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "olist_order_items_dataset" ADD FOREIGN KEY ("seller_id") REFERENCES "olist_sellers_dataset" ("seller_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "olist_products_dataset" ADD FOREIGN KEY ("product_category_name") REFERENCES "product_category_name_translation" ("product_category_name") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "olist_sellers_dataset" ADD FOREIGN KEY ("seller_zip_code_prefix") REFERENCES "olist_geolocation_dataset" ("geolocation_zip_code_prefix") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "olist_order_payments_dataset" ADD FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "olist_order_reviews_dataset" ADD FOREIGN KEY ("order_id") REFERENCES "olist_orders_dataset" ("order_id") DEFERRABLE INITIALLY IMMEDIATE;
