from logger import log_info, log_error
import time
from ingest import (
    dealer_ingest,
    product_ingest,
    inventory_ingest,
    sales_logs_ingest
)

from transform import (
    transform_dealer,
    transform_product,
    transform_inventory,
    transform_sales_logs
)

from load import (
    insert_dealer,
    insert_product,
    insert_inventory,
    load_tracking
)


def main():
    try:
        log_info("Pipeline Started")
        start = time.time()

        # PIPELINE FOR DEALER 
        log_info("Starting Pipeline for DEALER TABLE")
        stage_start = time.time()
        dealer_processed, dealer_hash,file_name = dealer_ingest()
        if dealer_processed:
            log_info("Dealer file already processed. Skipping.")
        else:
            transform_dealer()
            insert_dealer()
            load_tracking(file_name,dealer_hash)
        

        log_info("Running pipeline completed for dealers")
        log_info(f"[TIMER] DEALER PIPELINE: {time.time() - stage_start:.2f}s")
        
        # PIPELINE FOR PRODUCTS
        log_info("Starting Pipeline for PRODUCTS TABLE")
        stage_start = time.time()
        product_processed, product_hash,file_name = product_ingest()
        if product_processed:
            log_info("Product file already processed. Skipping.")
        else:
            transform_product()
            insert_product()
            load_tracking(product_hash,file_name)
        

        log_info("Running pipeline completed for products")
        log_info(f"[TIMER] PRODUCT PIPELINE: {time.time() - stage_start:.2f}s")
        
        # PIPELINE FOR INVENTORY
        log_info("Starting Pipeline for INVENTORY TABLE")
        stage_start = time.time()
        inventory_processed, inventory_hash,file_name = inventory_ingest()
        if inventory_processed:
            log_info("Inventory file already processed. Skipping.")
        else:
            transform_inventory()
            insert_inventory()
            load_tracking(inventory_hash,file_name)
        
        log_info("Running pipeline completed for inventory")
        log_info(f"[TIMER] INVENTORY TABLE: {time.time() - stage_start:.2f}s")
        
        # PIPELINE FOR SALES LOGS
        sales_logs_ingest()
        transform_sales_logs()

        log_info("[INFO] PIPELINE COMPLETED SUCCESSFULLY")
        total = time.time() - start
        log_info(f"[TIMER] Total execution: {total:.2f}s")

    except Exception as e:
        log_error(f"Pipeline Failed : {e}")
        raise


if __name__ == "__main__":
    main()