from sqlalchemy import create_engine, inspect, text
from analyzer import scan_text_for_pii # Re-using your existing logic!

def scan_live_database(connection_string):
    """
    Connects to a live database, iterates through all text columns,
    and hunts for PII.
    """
    findings = []
    
    try:
        # 1. Establish Connection
        print(f"[*] Connecting to database...")
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        
        # 2. Get list of all tables
        tables = inspector.get_table_names()
        print(f"[*] Found tables: {tables}")

        # 3. Crawl each table
        with engine.connect() as conn:
            for table in tables:
                print(f"[*] Scanning table: {table}...")
                
                # SAFETY CHECK: Only fetch first 100 rows for MVP (to prevent crashing)
                # In production, you would use pagination.
                query = text(f"SELECT * FROM {table} LIMIT 100") 
                result = conn.execute(query)
                
                # Get column names to help identify where the leak is
                columns = result.keys()

                for row_idx, row in enumerate(result):
                    # Convert the whole row to a string so we can regex it
                    # row_data example: "('Raj', '9876543210', 'Mumbai')"
                    row_text = str(row) 
                    
                    # 4. The "Hacker" Logic (Reuse your Analyzer)
                    leaks = scan_text_for_pii(row_text, line_number=f"Row {row_idx+1}")
                    
                    # Add context (Which table did this come from?)
                    for leak in leaks:
                        leak['line'] = f"Table '{table}' -> Row {row_idx+1}"
                        findings.extend([leak])

    except Exception as e:
        return {"error": str(e)}

    return findings