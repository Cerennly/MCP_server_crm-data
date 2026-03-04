"""
Seed Script — HuggingFace adityaswami89/Salesdata
3 katmanlı yükleme: datasets lib → HTTP → gömülü fallback
"""
from __future__ import annotations
import asyncio, hashlib, json, os, secrets, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import select, text
from src.db.models import (
    AsyncSessionLocal, create_tables,
    ApiKey, ApiKeyStatus, Customer, Contact, Deal, Activity,
    DealStatus, ActivityType,
)
from config.settings import settings

# ── Gömülü fallback veri (HF'den alınmış 20 gerçek kayıt) ────────────────────
FALLBACK = [
    {"CUSTOMERNAME":"Mini Gifts Distributors Ltd","CONTACTLASTNAME":"Nelson","CONTACTFIRSTNAME":"Susan","PHONE":"4155551450","ADDRESSLINE1":"5677 Strong St.","CITY":"San Rafael","STATE":"CA","POSTALCODE":"97562","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Motorcycles","ORDERNUMBER":"10107","QUANTITYORDERED":30,"PRICEEACH":95.70,"SALES":2871.00,"STATUS":"Shipped","QTR_ID":2,"MONTH_ID":2,"YEAR_ID":2003,"DEALSIZE":"Small","MSRP":95,"PRODUCTCODE":"S10_1678"},
    {"CUSTOMERNAME":"Land of Toys Inc.","CONTACTLASTNAME":"Yu","CONTACTFIRSTNAME":"Kwai","PHONE":"2125557818","ADDRESSLINE1":"897 Long Airport Avenue","CITY":"NYC","STATE":"NY","POSTALCODE":"10022","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Motorcycles","ORDERNUMBER":"10121","QUANTITYORDERED":34,"PRICEEACH":81.35,"SALES":2765.90,"STATUS":"Shipped","QTR_ID":2,"MONTH_ID":5,"YEAR_ID":2003,"DEALSIZE":"Small","MSRP":95,"PRODUCTCODE":"S10_1678"},
    {"CUSTOMERNAME":"Reims Collectables","CONTACTLASTNAME":"Henriot","CONTACTFIRSTNAME":"Paul","PHONE":"26.47.15.10","ADDRESSLINE1":"59 rue de l Abbaye","CITY":"Reims","STATE":"","POSTALCODE":"51100","COUNTRY":"France","TERRITORY":"EMEA","PRODUCTLINE":"Motorcycles","ORDERNUMBER":"10134","QUANTITYORDERED":41,"PRICEEACH":94.74,"SALES":3884.34,"STATUS":"Shipped","QTR_ID":3,"MONTH_ID":7,"YEAR_ID":2003,"DEALSIZE":"Medium","MSRP":95,"PRODUCTCODE":"S10_1678"},
    {"CUSTOMERNAME":"Lyon Souveniers","CONTACTLASTNAME":"Da Cunha","CONTACTFIRSTNAME":"Daniel","PHONE":"(0) 47.25.45.65","ADDRESSLINE1":"27 rue du Colonel Pierre Avia","CITY":"Paris","STATE":"","POSTALCODE":"75508","COUNTRY":"France","TERRITORY":"EMEA","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10145","QUANTITYORDERED":45,"PRICEEACH":83.26,"SALES":3746.70,"STATUS":"Shipped","QTR_ID":3,"MONTH_ID":8,"YEAR_ID":2003,"DEALSIZE":"Medium","MSRP":136,"PRODUCTCODE":"S18_1749"},
    {"CUSTOMERNAME":"Toys4GrownUps.com","CONTACTLASTNAME":"Young","CONTACTFIRSTNAME":"Julie","PHONE":"6265557265","ADDRESSLINE1":"78934 Hillside Dr.","CITY":"Pasadena","STATE":"CA","POSTALCODE":"90003","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10159","QUANTITYORDERED":49,"PRICEEACH":100.00,"SALES":4900.00,"STATUS":"Shipped","QTR_ID":4,"MONTH_ID":10,"YEAR_ID":2003,"DEALSIZE":"Medium","MSRP":136,"PRODUCTCODE":"S18_1749"},
    {"CUSTOMERNAME":"Dragon Souveniers, Ltd.","CONTACTLASTNAME":"Natividad","CONTACTFIRSTNAME":"Eric","PHONE":"+-65-221-7555","ADDRESSLINE1":"Bronz Sok.","CITY":"Singapore","STATE":"","POSTALCODE":"079903","COUNTRY":"Singapore","TERRITORY":"APAC","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10168","QUANTITYORDERED":36,"PRICEEACH":96.66,"SALES":3479.76,"STATUS":"Shipped","QTR_ID":4,"MONTH_ID":10,"YEAR_ID":2003,"DEALSIZE":"Medium","MSRP":136,"PRODUCTCODE":"S18_1749"},
    {"CUSTOMERNAME":"Technics Stores Inc.","CONTACTLASTNAME":"Hirano","CONTACTFIRSTNAME":"Juri","PHONE":"6505556388","ADDRESSLINE1":"9408 Furth Circle","CITY":"Burlingame","STATE":"CA","POSTALCODE":"94217","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Trucks and Buses","ORDERNUMBER":"10180","QUANTITYORDERED":29,"PRICEEACH":86.13,"SALES":2497.77,"STATUS":"Shipped","QTR_ID":4,"MONTH_ID":11,"YEAR_ID":2003,"DEALSIZE":"Small","MSRP":84,"PRODUCTCODE":"S18_2248"},
    {"CUSTOMERNAME":"Euro Shopping Channel","CONTACTLASTNAME":"Freyre","CONTACTFIRSTNAME":"Diego","PHONE":"(91) 555 94 44","ADDRESSLINE1":"C/ Moralzarzal, 86","CITY":"Madrid","STATE":"","POSTALCODE":"28034","COUNTRY":"Spain","TERRITORY":"EMEA","PRODUCTLINE":"Ships","ORDERNUMBER":"10201","QUANTITYORDERED":22,"PRICEEACH":98.57,"SALES":2168.54,"STATUS":"Shipped","QTR_ID":1,"MONTH_ID":1,"YEAR_ID":2004,"DEALSIZE":"Small","MSRP":62,"PRODUCTCODE":"S24_2840"},
    {"CUSTOMERNAME":"Diecast Collectables","CONTACTLASTNAME":"Franco","CONTACTFIRSTNAME":"Valarie","PHONE":"6175552555","ADDRESSLINE1":"6251 Ingle Ln.","CITY":"Boston","STATE":"MA","POSTALCODE":"51003","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Vintage Cars","ORDERNUMBER":"10211","QUANTITYORDERED":37,"PRICEEACH":100.00,"SALES":3700.00,"STATUS":"Shipped","QTR_ID":1,"MONTH_ID":1,"YEAR_ID":2004,"DEALSIZE":"Medium","MSRP":98,"PRODUCTCODE":"S18_3482"},
    {"CUSTOMERNAME":"Marta's Replicas Co.","CONTACTLASTNAME":"Hernandez","CONTACTFIRSTNAME":"Marta","PHONE":"6175558555","ADDRESSLINE1":"39323 Spinnaker Dr.","CITY":"Cambridge","STATE":"MA","POSTALCODE":"51003","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Planes","ORDERNUMBER":"10222","QUANTITYORDERED":38,"PRICEEACH":60.79,"SALES":2310.02,"STATUS":"Shipped","QTR_ID":1,"MONTH_ID":2,"YEAR_ID":2004,"DEALSIZE":"Small","MSRP":68,"PRODUCTCODE":"S700_1938"},
    {"CUSTOMERNAME":"AV Stores, Co.","CONTACTLASTNAME":"Bond","CONTACTFIRSTNAME":"Victoria","PHONE":"(171) 555-1555","ADDRESSLINE1":"Fauntleroy Circus","CITY":"Manchester","STATE":"","POSTALCODE":"EC2 5NT","COUNTRY":"UK","TERRITORY":"EMEA","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10237","QUANTITYORDERED":23,"PRICEEACH":107.38,"SALES":2469.74,"STATUS":"Shipped","QTR_ID":2,"MONTH_ID":4,"YEAR_ID":2004,"DEALSIZE":"Small","MSRP":136,"PRODUCTCODE":"S18_1749"},
    {"CUSTOMERNAME":"Gift Ideas Corp.","CONTACTLASTNAME":"Lewis","CONTACTFIRSTNAME":"Dan","PHONE":"2035554407","ADDRESSLINE1":"2440 Pompton St.","CITY":"Glendale","STATE":"CT","POSTALCODE":"97561","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10251","QUANTITYORDERED":40,"PRICEEACH":96.35,"SALES":3854.00,"STATUS":"Shipped","QTR_ID":2,"MONTH_ID":5,"YEAR_ID":2004,"DEALSIZE":"Medium","MSRP":136,"PRODUCTCODE":"S18_1749"},
    {"CUSTOMERNAME":"Saveley & Henriot, Co.","CONTACTLASTNAME":"Saveley","CONTACTFIRSTNAME":"Mary","PHONE":"78.32.5555","ADDRESSLINE1":"187 Rue Auxerre","CITY":"Lyon","STATE":"","POSTALCODE":"69004","COUNTRY":"France","TERRITORY":"EMEA","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10263","QUANTITYORDERED":28,"PRICEEACH":99.17,"SALES":2776.76,"STATUS":"Shipped","QTR_ID":2,"MONTH_ID":6,"YEAR_ID":2004,"DEALSIZE":"Small","MSRP":136,"PRODUCTCODE":"S18_1749"},
    {"CUSTOMERNAME":"Australian Collectors, Co.","CONTACTLASTNAME":"Ferguson","CONTACTFIRSTNAME":"Peter","PHONE":"03 9520 4555","ADDRESSLINE1":"636 St Kilda Road","CITY":"Melbourne","STATE":"Victoria","POSTALCODE":"3004","COUNTRY":"Australia","TERRITORY":"APAC","PRODUCTLINE":"Motorcycles","ORDERNUMBER":"10275","QUANTITYORDERED":49,"PRICEEACH":95.68,"SALES":4688.32,"STATUS":"Shipped","QTR_ID":3,"MONTH_ID":7,"YEAR_ID":2004,"DEALSIZE":"Medium","MSRP":95,"PRODUCTCODE":"S10_1678"},
    {"CUSTOMERNAME":"Danish Wholesale Imports","CONTACTLASTNAME":"Petersen","CONTACTFIRSTNAME":"Jytte","PHONE":"31 12 3555","ADDRESSLINE1":"Vinbltet 34","CITY":"Kobenhavn","STATE":"","POSTALCODE":"1734","COUNTRY":"Denmark","TERRITORY":"EMEA","PRODUCTLINE":"Motorcycles","ORDERNUMBER":"10287","QUANTITYORDERED":47,"PRICEEACH":100.00,"SALES":4700.00,"STATUS":"Shipped","QTR_ID":3,"MONTH_ID":9,"YEAR_ID":2004,"DEALSIZE":"Medium","MSRP":95,"PRODUCTCODE":"S10_1678"},
    {"CUSTOMERNAME":"Tokyo Collectables, Ltd","CONTACTLASTNAME":"Shimamura","CONTACTFIRSTNAME":"Akiko","PHONE":"+-81-3-4555-9901","ADDRESSLINE1":"2-2-8 Marunouchi","CITY":"Tokyo","STATE":"","POSTALCODE":"1-chome","COUNTRY":"Japan","TERRITORY":"Japan","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10300","QUANTITYORDERED":36,"PRICEEACH":107.38,"SALES":3865.68,"STATUS":"Shipped","QTR_ID":4,"MONTH_ID":10,"YEAR_ID":2004,"DEALSIZE":"Medium","MSRP":136,"PRODUCTCODE":"S18_1749"},
    {"CUSTOMERNAME":"Boards & Toys Co.","CONTACTLASTNAME":"Young","CONTACTFIRSTNAME":"Mary","PHONE":"3105552373","ADDRESSLINE1":"4097 Douglas Av.","CITY":"Glendale","STATE":"CA","POSTALCODE":"92561","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Vintage Cars","ORDERNUMBER":"10312","QUANTITYORDERED":48,"PRICEEACH":85.07,"SALES":4083.36,"STATUS":"Shipped","QTR_ID":4,"MONTH_ID":11,"YEAR_ID":2004,"DEALSIZE":"Medium","MSRP":98,"PRODUCTCODE":"S18_3482"},
    {"CUSTOMERNAME":"Alpha Cognac","CONTACTLASTNAME":"Roulet","CONTACTFIRSTNAME":"Annette","PHONE":"61.77.6555","ADDRESSLINE1":"1 rue Alsace-Lorraine","CITY":"Toulouse","STATE":"","POSTALCODE":"31000","COUNTRY":"France","TERRITORY":"EMEA","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10325","QUANTITYORDERED":35,"PRICEEACH":100.00,"SALES":3500.00,"STATUS":"Shipped","QTR_ID":4,"MONTH_ID":12,"YEAR_ID":2004,"DEALSIZE":"Medium","MSRP":136,"PRODUCTCODE":"S18_1749"},
    {"CUSTOMERNAME":"Herkku Gifts","CONTACTLASTNAME":"Oeztan","CONTACTFIRSTNAME":"Veysel","PHONE":"(0) 45-555-3555","ADDRESSLINE1":"Kuvvet sok 2/1 Levent","CITY":"Helsinki","STATE":"","POSTALCODE":"","COUNTRY":"Finland","TERRITORY":"EMEA","PRODUCTLINE":"Trains","ORDERNUMBER":"10337","QUANTITYORDERED":39,"PRICEEACH":30.87,"SALES":1203.93,"STATUS":"Shipped","QTR_ID":1,"MONTH_ID":3,"YEAR_ID":2005,"DEALSIZE":"Small","MSRP":34,"PRODUCTCODE":"S700_2047"},
    {"CUSTOMERNAME":"Signal Collectibles Ltd.","CONTACTLASTNAME":"Taylor","CONTACTFIRSTNAME":"Sue","PHONE":"4155554312","ADDRESSLINE1":"2793 Furth Circle","CITY":"Brisbane","STATE":"CA","POSTALCODE":"94217","COUNTRY":"USA","TERRITORY":"NA","PRODUCTLINE":"Classic Cars","ORDERNUMBER":"10351","QUANTITYORDERED":45,"PRICEEACH":100.00,"SALES":4500.00,"STATUS":"Shipped","QTR_ID":2,"MONTH_ID":4,"YEAR_ID":2005,"DEALSIZE":"Medium","MSRP":136,"PRODUCTCODE":"S18_1749"},
]

STATUS_MAP = {
    "Shipped": DealStatus.WON, "Resolved": DealStatus.WON,
    "In Process": DealStatus.PROPOSAL, "On Hold": DealStatus.NEGOTIATION,
    "Cancelled": DealStatus.LOST, "Disputed": DealStatus.LOST,
}
SIZE_MULT = {"Small": 1.0, "Medium": 3.0, "Large": 8.0}


def load_data(limit: int) -> list:
    """3 katmanlı yükleme: datasets → HTTP → fallback"""
    # 1) datasets kütüphanesi
    try:
        from datasets import load_dataset
        print("📦 HuggingFace datasets kütüphanesi ile yükleniyor...")
        ds = load_dataset(settings.HF_DATASET, split="train")
        rows = [dict(r) for r in ds]
        print(f"✅ HuggingFace'den {len(rows)} kayıt yüklendi")
        return rows[:limit]
    except Exception as e:
        print(f"⚠️  datasets başarısız: {e}")

    # 2) HTTP
    try:
        import requests
        url = f"https://huggingface.co/datasets/{settings.HF_DATASET}/resolve/main/sales_data_sample.csv"
        print(f"🌐 HTTP ile indiriliyor: {url}")
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        import csv, io
        reader = csv.DictReader(io.StringIO(resp.text))
        rows = list(reader)
        print(f"✅ HTTP ile {len(rows)} kayıt yüklendi")
        return rows[:limit]
    except Exception as e:
        print(f"⚠️  HTTP başarısız: {e}")

    # 3) Gömülü fallback
    print("📋 Gömülü fallback veri kullanılıyor (20 kayıt)")
    return FALLBACK[:limit]


def make_api_key(raw: str) -> ApiKey:
    return ApiKey(
        key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        key_prefix=raw[:12], name="",
        scopes="", status=ApiKeyStatus.ACTIVE,
    )


async def seed(limit: int = 50, force: bool = False):
    await create_tables()

    async with AsyncSessionLocal() as db:
        # Force temizlik
        if force:
            for tbl in ["activities", "tasks", "deals", "contacts", "customers", "api_keys"]:
                await db.execute(text(f"DELETE FROM {tbl}"))
            await db.commit()
            print("🗑  Eski veriler silindi")

        # API Key'ler
        existing = (await db.execute(select(ApiKey))).scalars().first()
        admin_raw = ro_raw = sales_raw = None
        if not existing:
            admin_raw = settings.API_KEY_PREFIX + secrets.token_urlsafe(24)
            ro_raw    = settings.API_KEY_PREFIX + secrets.token_urlsafe(24)
            sales_raw = settings.API_KEY_PREFIX + secrets.token_urlsafe(24)
            for raw, name, scopes in [
                (admin_raw, "Admin",     json.dumps(["*"])),
                (ro_raw,    "Read-Only", json.dumps(["customers:read","deals:read"])),
                (sales_raw, "Sales",     json.dumps(["customers:read","customers:write","deals:read","deals:write"])),
            ]:
                db.add(ApiKey(
                    key_hash=hashlib.sha256(raw.encode()).hexdigest(),
                    key_prefix=raw[:12], name=name,
                    scopes=scopes, status=ApiKeyStatus.ACTIVE,
                ))
            await db.commit()

        # Veri yükle
        rows = load_data(limit)

        # Deduplicate by CUSTOMERNAME — en yüksek SALES'lı satır
        best = {}
        for r in rows:
            name = str(r.get("CUSTOMERNAME", "")).strip()
            try:
                sales = float(r.get("SALES", 0))
            except:
                sales = 0
            if name not in best or sales > best[name]["_sales"]:
                r["_sales"] = sales
                best[name] = r

        customers_created = 0
        deals_created = 0

        for r in best.values():
            cname = str(r.get("CUSTOMERNAME", "")).strip()
            if not cname:
                continue

            # Customer
            cust = Customer(
                name=cname, company=cname,
                phone=str(r.get("PHONE", "") or "")[:60],
                address=str(r.get("ADDRESSLINE1", "") or ""),
                city=str(r.get("CITY", "") or ""),
                state=str(r.get("STATE", "") or ""),
                country=str(r.get("COUNTRY", "") or ""),
                territory=str(r.get("TERRITORY", "") or ""),
                industry=str(r.get("PRODUCTLINE", "") or ""),
                hf_source="adityaswami89/Salesdata",
            )
            db.add(cust)
            await db.flush()
            customers_created += 1

            # Contact
            fname = str(r.get("CONTACTFIRSTNAME", "") or "").strip()
            lname = str(r.get("CONTACTLASTNAME",  "") or "").strip()
            if fname or lname:
                db.add(Contact(
                    customer_id=cust.id,
                    first_name=fname or "N/A",
                    last_name=lname  or "N/A",
                    is_primary=True,
                ))

            # Deal
            hf_status = str(r.get("STATUS", "Shipped"))
            deal_size = str(r.get("DEALSIZE", "Small"))
            try:
                revenue = float(r.get("SALES", 0))
            except:
                revenue = 0.0
            value = revenue * SIZE_MULT.get(deal_size, 1.0)

            try:
                qty = int(r.get("QUANTITYORDERED", 0))
            except:
                qty = 0
            try:
                price = float(r.get("PRICEEACH", 0))
            except:
                price = 0.0
            try:
                msrp = float(r.get("MSRP", 0))
            except:
                msrp = 0.0
            try:
                year = int(r.get("YEAR_ID", 0))
            except:
                year = None
            try:
                qtr = int(r.get("QTR_ID", 0))
            except:
                qtr = None
            try:
                month = int(r.get("MONTH_ID", 0))
            except:
                month = None

            deal = Deal(
                customer_id=cust.id,
                title=f"{cname} — {r.get('PRODUCTLINE','Order')}",
                order_number=str(r.get("ORDERNUMBER", "") or ""),
                hf_status=hf_status,
                product_line=str(r.get("PRODUCTLINE", "") or ""),
                product_code=str(r.get("PRODUCTCODE", "") or ""),
                quantity_ordered=qty,
                price_each=price,
                msrp=msrp,
                revenue=revenue,
                deal_size=deal_size,
                quarter=qtr,
                order_month=month,
                order_year=year,
                status=STATUS_MAP.get(hf_status, DealStatus.WON),
                value=value,
            )
            db.add(deal)
            await db.flush()
            deals_created += 1

            # Activity
            db.add(Activity(
                customer_id=cust.id, deal_id=deal.id,
                type=ActivityType.ORDER,
                subject=f"Sipariş #{r.get('ORDERNUMBER','')} — {hf_status}",
            ))

        await db.commit()

        print()
        print("═" * 50)
        print(f"✅ Customers   : {customers_created}")
        print(f"✅ Deals       : {deals_created}")
        if admin_raw:
            print()
            print("🔑 API KEY'LER — ŞİMDİ KOPYALA!")
            print(f"   Admin    : {admin_raw}")
            print(f"   ReadOnly : {ro_raw}")
            print(f"   Sales    : {sales_raw}")
        else:
            print("ℹ️  API key'ler zaten mevcut (--force ile sıfırla)")
        print("═" * 50)
        print()
        print("🚀 Sunucu açıksa test et:")
        print("   http://localhost:8000/docs")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--force", action="store_true")
    args = p.parse_args()
    asyncio.run(seed(args.limit, args.force))
