"""
Fix the properties table in Supabase by dropping and recreating it
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def fix_table():
    """Drop and recreate the properties table with correct schema"""

    postgres_url = os.getenv("POSTGRES_URL_NON_POOLING")

    if not postgres_url:
        print("❌ Error: POSTGRES_URL_NON_POOLING not found in .env")
        return False

    try:
        conn = psycopg2.connect(postgres_url)
        cursor = conn.cursor()

        print("Dropping existing properties table...")
        cursor.execute("DROP TABLE IF EXISTS properties CASCADE;")
        conn.commit()
        print("✅ Table dropped")

        print("\nCreating new properties table...")

        # Create table
        cursor.execute("""
            CREATE TABLE properties (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                address TEXT,
                monthly_rent TEXT,
                bedrooms TEXT,
                bathrooms TEXT,
                area TEXT,
                zillow_url TEXT NOT NULL,
                images JSONB DEFAULT '[]'::jsonb,
                scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(zillow_url)
            );
        """)
        conn.commit()
        print("✅ Table created")

        # Create indexes
        print("\nCreating indexes...")
        cursor.execute("CREATE INDEX idx_properties_zillow_url ON properties(zillow_url);")
        cursor.execute("CREATE INDEX idx_properties_address ON properties(address);")
        cursor.execute("CREATE INDEX idx_properties_scraped_at ON properties(scraped_at DESC);")
        conn.commit()
        print("✅ Indexes created")

        # Enable RLS
        print("\nEnabling Row Level Security...")
        cursor.execute("ALTER TABLE properties ENABLE ROW LEVEL SECURITY;")
        conn.commit()

        # Create policy
        cursor.execute("""
            CREATE POLICY "Enable all operations for all users" ON properties
            FOR ALL
            USING (true)
            WITH CHECK (true);
        """)
        conn.commit()
        print("✅ RLS enabled with policy")

        cursor.close()
        conn.close()

        print("\n✅ Table fixed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("Fixing Supabase Properties Table")
    print("=" * 70)
    print()

    success = fix_table()

    if success:
        print()
        print("=" * 70)
        print("✅ All done! Table is ready to use.")
        print("=" * 70)
    else:
        print()
        print("=" * 70)
        print("❌ Fix failed. Please check the error messages above.")
        print("=" * 70)
