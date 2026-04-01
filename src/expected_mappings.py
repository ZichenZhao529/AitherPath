# src/expected_mappings.py

EXPECTED_MAPPINGS = {
    "client_a_customers": {
        "cust_id": "customer_id",
        "full_name": "full_name",
        "email_addr": "email",
        "signup_dt": "registration_date",
        "phone": "phone",
    },
    "client_a_orders": {
        "order_no": "order_id",
        "cust_id": "customer_id",
        "order_date": "order_date",
        "total_amt": "amount",
        "status": "order_status",
        "shipping_addr": "shipping_address",
    },
    "client_b_customers": {
        "id_pelanggan": "customer_id",
        "nama": "full_name",
        "no_hp": "phone",
        "email": "email",
        "tgl_daftar": "registration_date",
        "kota": "city",   # 显示是unknown，因为当前 allowed semantic types 没有 city
    },
    "client_b_orders": {
        "no_pesanan": "order_id",
        "id_pelanggan": "customer_id",
        "tgl_pesan": "order_date",
        "total_harga": "amount",
        "mata_uang": "currency",
        "status_pesanan": "order_status",
        "alamat_kirim": "shipping_address",
    },
    "client_c_customers": {
        "Kundennummer": "customer_id",
        "Vorname": "first_name",
        "Nachname": "last_name",
        "E-Mail": "email",
        "Telefon": "phone",
        "Registrierungsdatum": "registration_date",
        "Land": "country",
    },
    "client_c_orders": {
        "Bestellnummer": "order_id",
        "Kundennummer": "customer_id",
        "Bestelldatum": "order_date",
        "Gesamtbetrag": "amount",
        "Währung": "currency",
        "Bestellstatus": "order_status",
        "Lieferadresse": "shipping_address",
    },
}