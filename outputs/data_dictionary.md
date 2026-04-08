# Unified Data Dictionary

This document describes the unified dataset fields, their meanings, source coverage, and transformation logic.

## unified_customers

### customer_id
- **Type:** string
- **Nullable:** No
- **Description:** Unified customer identifier.
- **Source coverage (schema):** A, B, C
- **Design reason:** Present with high confidence in all customer datasets and required as the core customer-level key.
- **Source mappings:**
  - client_a: `customers.cust_id` via `renaming`
  - client_b: `customers.id_pelanggan` via `renaming`
  - client_c: `customers.Kundennummer` via `renaming`
- **Transformation notes:**
  - client_a: customer_id = cust_id
  - client_b: customer_id = id_pelanggan
  - client_c: customer_id = Kundennummer

### full_name
- **Type:** string
- **Nullable:** Yes
- **Description:** Customer full name as a single displayable string.
- **Source coverage (schema):** A, B, C (A and B directly provide full_name; C can derive it by combining first_name and last_name)
- **Design reason:** Keep a unified full_name for broadest cross-client compatibility. Client C has separate first_name and last_name, but A and B only provide full names, so full_name should be the canonical shared field.
- **Source mappings:**
  - client_a: `customers.full_name` via `direct_mapping`
  - client_b: `customers.nama` via `renaming`
  - client_c: `customers.Vorname, Nachname` via `concatenation`
- **Transformation notes:**
  - client_a: full_name = full_name
  - client_b: full_name = nama
  - client_c: full_name = trim(concat(Vorname, ' ', Nachname))

### first_name
- **Type:** string
- **Nullable:** Yes
- **Description:** Customer given name.
- **Source coverage (schema):** C only
- **Design reason:** Included explicitly because one source provides structured name components. It should remain nullable since A and B do not provide reliable first-name parsing from full_name.
- **Source mappings:**
  - client_a: `customers.full_name` via `splitting`
  - client_b: `customers.nama` via `splitting`
  - client_c: `customers.Vorname` via `renaming`
- **Transformation notes:**
  - client_a: Split full_name on spaces; first_name = first token. If full_name is null or empty, set first_name = null.
  - client_b: Split nama by spaces; first_name = first token. If nama contains only one token, assign that token to first_name and set last_name to empty/null.
  - client_c: first_name = Vorname

### last_name
- **Type:** string
- **Nullable:** Yes
- **Description:** Customer family name or surname.
- **Source coverage (schema):** C only
- **Design reason:** Included explicitly because one source provides structured surname data. It should remain nullable since A and B do not provide reliable last-name parsing from full_name.
- **Source mappings:**
  - client_a: `customers.full_name` via `splitting`
  - client_b: `customers.nama` via `splitting`
  - client_c: `customers.Nachname` via `renaming`
- **Transformation notes:**
  - client_a: Split full_name on spaces; last_name = join all tokens after the first with a single space. If only one token exists, set last_name = null.
  - client_b: Split nama by spaces; last_name = all tokens after the first joined by a single space. If nama contains only one token, set last_name to empty/null.
  - client_c: last_name = Nachname

### email
- **Type:** string
- **Nullable:** Yes
- **Description:** Customer email address.
- **Source coverage (schema):** A, B, C
- **Design reason:** Available across all customer datasets and valuable for customer identity resolution and communication.
- **Source mappings:**
  - client_a: `customers.email_addr` via `renaming`
  - client_b: `customers.email` via `direct_mapping`
  - client_c: `customers.E-Mail` via `renaming`
- **Transformation notes:**
  - client_a: email = email_addr
  - client_b: email = email
  - client_c: email = E-Mail

### phone
- **Type:** string
- **Nullable:** Yes
- **Description:** Customer phone number in source-provided format.
- **Source coverage (schema):** A, B, C
- **Design reason:** Available across all customer datasets, but stored as string to preserve international formatting and source variability.
- **Source mappings:**
  - client_a: `customers.phone` via `direct_mapping`
  - client_b: `customers.no_hp` via `direct_mapping`
  - client_c: `customers.Telefon` via `format_cleanup`
- **Transformation notes:**
  - client_a: phone = phone
  - client_b: phone = no_hp
  - client_c: phone = if Telefon is null then null else normalize_phone(Telefon) by removing spaces, hyphens, and non-numeric separators while preserving a leading '+'; examples: '+49-30-12345' -> '+493012345', '+33-1-23456' -> '+33123456'

### registration_date
- **Type:** date
- **Nullable:** Yes
- **Description:** Date the customer registered or signed up.
- **Source coverage (schema):** A, B, C
- **Design reason:** Present in all customer datasets. Use date as the target type, with parsing/quality handling because some source values are malformed or inconsistently formatted.
- **Source mappings:**
  - client_a: `customers.signup_dt` via `date_format_conversion`
  - client_b: `customers.tgl_daftar` via `date_format_conversion`
  - client_c: `customers.Registrierungsdatum` via `date_format_conversion`
- **Transformation notes:**
  - client_a: Parse signup_dt as source format YYYY-MM-DD and output as target date format YYYY-MM-DD. If parsing fails, set registration_date = null.
  - client_b: Parse tgl_daftar using source formats 'DD/MM/YYYY' or 'DD-MM-YYYY'; convert to target format 'YYYY-MM-DD'. If parsing fails or date is invalid (e.g. 31/02/2024), set registration_date to null and flag for data quality review.
  - client_c: registration_date = parse_date(Registrierungsdatum, source_format='yyyy.MM.dd', target_format='yyyy-MM-dd'); if parsing fails, set to null

### city
- **Type:** string
- **Nullable:** Yes
- **Description:** Customer city.
- **Source coverage (schema):** B only
- **Design reason:** Include city because geography is useful at customer level and one client provides it explicitly. Nullable because A and C do not contain a customer-city field.
- **Source mappings:**
  - client_a: no direct source field via `default_value`
  - client_b: `customers.kota` via `renaming`
  - client_c: no direct source field via `default_value`
- **Transformation notes:**
  - client_a: city = null
  - client_b: city = kota
  - client_c: city = null

### country
- **Type:** string
- **Nullable:** Yes
- **Description:** Customer country, preferably as a standard country code when available.
- **Source coverage (schema):** C only
- **Design reason:** Include country because geography should support both city and country where available. Nullable because A and B do not contain a customer-country field.
- **Source mappings:**
  - client_a: no direct source field via `default_value`
  - client_b: no direct source field via `default_value`
  - client_c: `customers.Land` via `format_cleanup`
- **Transformation notes:**
  - client_a: country = null
  - client_b: country = null
  - client_c: country = upper(trim(Land))

### source_system
- **Type:** string
- **Nullable:** No
- **Description:** Identifier of the originating client dataset for the customer record.
- **Source coverage (schema):** A, B, C (derived from dataset context)
- **Design reason:** Needed for lineage, troubleshooting, and preserving source provenance across integrated customer records.
- **Source mappings:**
  - client_a: no direct source field via `default_value`
  - client_b: no direct source field via `default_value`
  - client_c: no direct source field via `default_value`
- **Transformation notes:**
  - client_a: source_system = 'client_a'
  - client_b: source_system = 'client_b'
  - client_c: source_system = 'client_c'

## unified_orders

### order_id
- **Type:** string
- **Nullable:** No
- **Description:** Unified order identifier.
- **Source coverage (schema):** A, B, C
- **Design reason:** Present with high confidence in all order datasets and required as the core order-level key.
- **Source mappings:**
  - client_a: `orders.order_no` via `renaming`
  - client_b: `orders.no_pesanan` via `renaming`
  - client_c: `orders.Bestellnummer` via `renaming`
- **Transformation notes:**
  - client_a: order_id = order_no
  - client_b: order_id = no_pesanan
  - client_c: order_id = Bestellnummer

### customer_id
- **Type:** string
- **Nullable:** No
- **Description:** Identifier of the customer associated with the order.
- **Source coverage (schema):** A, B, C
- **Design reason:** Present in all order datasets and required to relate orders to unified_customers.
- **Source mappings:**
  - client_a: `orders.cust_id` via `renaming`
  - client_b: `orders.id_pelanggan` via `renaming`
  - client_c: `orders.Kundennummer` via `renaming`
- **Transformation notes:**
  - client_a: customer_id = cust_id
  - client_b: customer_id = id_pelanggan
  - client_c: customer_id = Kundennummer

### order_date
- **Type:** date
- **Nullable:** Yes
- **Description:** Date the order was placed.
- **Source coverage (schema):** A, B, C
- **Design reason:** Present in all order datasets. Use date as the target type, with validation and parsing rules because some source values are malformed or use different date formats.
- **Source mappings:**
  - client_a: `orders.order_date` via `date_format_conversion`
  - client_b: `orders.tgl_pesan` via `date_format_conversion`
  - client_c: `orders.Bestelldatum` via `date_format_conversion`
- **Transformation notes:**
  - client_a: Attempt to parse order_date using source formats YYYY-MM-DD and YYYY/MM/DD; output as target date format YYYY-MM-DD. Validate calendar dates; if parsing or validation fails, set order_date = null.
  - client_b: Parse tgl_pesan using source formats 'DD-MM-YYYY' or 'DD/MM/YYYY'; convert to target format 'YYYY-MM-DD'. If parsing fails, set order_date to null.
  - client_c: order_date = parse_date(Bestelldatum, source_format='dd.MM.yyyy', target_format='yyyy-MM-dd'); if parsing fails or date is invalid (for example month 13), set to null

### amount
- **Type:** decimal(18,2)
- **Nullable:** Yes
- **Description:** Original order monetary amount in the source currency.
- **Source coverage (schema):** A, B, C
- **Design reason:** All sources provide an order total. Preserve the original numeric value as the canonical source amount.
- **Source mappings:**
  - client_a: `orders.total_amt` via `renaming`
  - client_b: `orders.total_harga` via `renaming`
  - client_c: `orders.Gesamtbetrag` via `renaming`
- **Transformation notes:**
  - client_a: amount = round(total_amt, 2)
  - client_b: amount = cast(total_harga as decimal(18,2))
  - client_c: amount = round(Gesamtbetrag, 2)

### currency
- **Type:** string
- **Nullable:** Yes
- **Description:** Original currency code for the order amount.
- **Source coverage (schema):** B, C directly; A not explicitly provided
- **Design reason:** Monetary values should preserve original currency. Even though client A lacks an explicit currency field, the unified schema should retain currency to support multi-currency processing.
- **Source mappings:**
  - client_a: no direct source field via `default_value`
  - client_b: `orders.mata_uang` via `renaming`
  - client_c: `orders.Währung` via `format_cleanup`
- **Transformation notes:**
  - client_a: currency = 'USD'
  - client_b: currency = mata_uang
  - client_c: currency = upper(trim(Währung))

### amount_usd
- **Type:** decimal(18,2)
- **Nullable:** Yes
- **Description:** Order amount normalized to USD using an agreed exchange-rate process.
- **Source coverage (schema):** None directly; derived for A, B, C when currency and exchange rates are available
- **Design reason:** Include a normalized USD amount in addition to original amount and currency to enable cross-client analytics. It is nullable because it must be derived and may be unavailable when source currency or conversion rates are missing.
- **Source mappings:**
  - client_a: `orders.total_amt` via `calculated_field`
  - client_b: `orders.total_harga` via `calculated_field`
  - client_c: `orders.Gesamtbetrag, Währung` via `calculated_field`
- **Transformation notes:**
  - client_a: If currency == 'USD' then amount_usd = round(total_amt, 2); otherwise amount_usd = round(total_amt * fx_rate_to_usd, 2). For client_a, currency defaults to 'USD', so amount_usd = round(total_amt, 2).
  - client_b: amount_usd = if mata_uang = 'USD' then cast(total_harga as decimal(18,2)) else if exchange_rate_to_usd exists for mata_uang and order_date then round(total_harga * exchange_rate_to_usd, 2) else null. Pseudocode: rate = lookup_fx_rate(mata_uang, order_date, 'USD'); if rate is not null then amount_usd = round(total_harga * rate, 2) else amount_usd = null.
  - client_c: amount_usd = if Gesamtbetrag is null or Währung is null then null else round(Gesamtbetrag * exchange_rate_to_usd(upper(trim(Währung)), order_date), 2); pseudocode: curr = upper(trim(Währung)); rate = exchange_rate_to_usd(curr, order_date); if rate is null then null else round(Gesamtbetrag * rate, 2)

### order_status
- **Type:** string
- **Nullable:** Yes
- **Description:** Order lifecycle status in source or mapped standardized form.
- **Source coverage (schema):** A, B, C
- **Design reason:** Present in all order datasets and useful for operational and analytical reporting, though multilingual values may require mapping to a controlled vocabulary.
- **Source mappings:**
  - client_a: `orders.status` via `value_translation`
  - client_b: `orders.status_pesanan` via `value_translation`
  - client_c: `orders.Bestellstatus` via `value_translation`
- **Transformation notes:**
  - client_a: Translate source status to standardized vocabulary: delivered -> delivered, pending -> pending, cancelled -> cancelled. If an unexpected value appears, retain the original trimmed lowercase value.
  - client_b: Translate status_pesanan to standardized vocabulary: 'terkirim' -> 'delivered', 'menunggu' -> 'pending', 'dibatalkan' -> 'cancelled'. If an unmapped value appears, preserve original value or route to review according to pipeline policy.
  - client_c: order_status = translate(Bestellstatus): 'Geliefert' -> 'delivered', 'Ausstehend' -> 'pending', 'Storniert' -> 'cancelled'; otherwise retain null for unmapped or missing values

### shipping_address
- **Type:** string
- **Nullable:** Yes
- **Description:** Shipping or delivery address associated with the order.
- **Source coverage (schema):** A, B, C
- **Design reason:** Present in all order datasets and correctly belongs at the order level because shipment destinations can vary across orders for the same customer.
- **Source mappings:**
  - client_a: `orders.shipping_addr` via `renaming`
  - client_b: `orders.alamat_kirim` via `renaming`
  - client_c: `orders.Lieferadresse` via `renaming`
- **Transformation notes:**
  - client_a: shipping_address = shipping_addr
  - client_b: shipping_address = alamat_kirim
  - client_c: shipping_address = Lieferadresse

### source_system
- **Type:** string
- **Nullable:** No
- **Description:** Identifier of the originating client dataset for the order record.
- **Source coverage (schema):** A, B, C (derived from dataset context)
- **Design reason:** Needed for lineage, traceability, and handling source-specific transformations in the integrated orders table.
- **Source mappings:**
  - client_a: no direct source field via `default_value`
  - client_b: no direct source field via `default_value`
  - client_c: no direct source field via `default_value`
- **Transformation notes:**
  - client_a: source_system = 'client_a'
  - client_b: source_system = 'client_b'
  - client_c: source_system = 'client_c'
