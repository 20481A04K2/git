import pyodbc

DATABASE_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',  # Make sure this driver is installed
    'SERVER': '35.192.101.149',  # Cloud SQL Server IP
    'DATABASE': 'test01',  # Your database name
    'UID': 'sqlserver',  # Your SQL Server username
    'PWD': 'svamsi123'  # Your SQL Server password
}

try:
    conn = pyodbc.connect(
        f"DRIVER={DATABASE_CONFIG['DRIVER']};"
        f"SERVER={DATABASE_CONFIG['SERVER']};"
        f"DATABASE={DATABASE_CONFIG['DATABASE']};"
        f"UID={DATABASE_CONFIG['UID']};"
        f"PWD={DATABASE_CONFIG['PWD']};"
        "Encrypt=no;"
    )
    print("✅ Database Connection Successful!")
except Exception as e:
    print(f"❌ Database Connection Failed: {e}")
