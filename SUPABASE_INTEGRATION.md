# Supabase Integration - Complete Setup

## Overview

The Zillow Scraper API now automatically saves all scraped property data to Supabase in addition to JSON files. Data is stored in a `properties` table with full history and query capabilities.

## Database Schema

### Properties Table

```sql
CREATE TABLE properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Property details
    address TEXT,
    monthly_rent TEXT,
    bedrooms TEXT,
    bathrooms TEXT,
    area TEXT,

    -- Zillow URL (unique identifier)
    zillow_url TEXT NOT NULL UNIQUE,

    -- Images stored as JSON array
    images JSONB DEFAULT '[]'::jsonb,

    -- Metadata
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Indexes

- `idx_properties_zillow_url` - Fast lookups by URL
- `idx_properties_address` - Search by address
- `idx_properties_scraped_at` - Chronological queries

## Setup Instructions

### 1. Environment Variables

Your `.env` file already contains the necessary Supabase credentials:

```
SUPABASE_URL=https://esdkkyekfnpmwifyohac.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
POSTGRES_URL_NON_POOLING=postgres://postgres.esdkkyekfnpmwifyohac:...
```

### 2. Create/Fix the Database Table

The table has already been created. If you need to recreate it:

```bash
python fix_table.py
```

This will:
- Drop the existing table (if any)
- Create a new table with the correct schema
- Add indexes for performance
- Enable Row Level Security
- Set up access policies

### 3. Start the API

```bash
python api.py
```

You should see:
```
✅ Connected to Supabase: https://esdkkyekfnpmwifyohac.supabase.co
```

## Features

### Automatic Saving

Every time you scrape a property, the data is:
1. ✅ Saved to a timestamped JSON file
2. ✅ Saved to Supabase database

### Upsert Behavior

- **New Property**: Inserted into database
- **Existing Property**: Updated with latest data
- Uniqueness determined by `zillow_url`

### Example Success Log

```
Starting scrape for: https://www.zillow.com/homedetails/...
✓ Found address: 9255 Swallow Dr, Los Angeles, CA 90069
✓ Found price: $90,000
✓ Found bedrooms: 7
✓ Found bathrooms: 12
✓ Found area: 12,237 sqft
✓ Found 37 unique images
✅ Data saved to scraped_property_20251107_134622.json
✅ Data saved to Supabase (ID: d9c5ef7c-3399-4dd3-ada8-1d8f293ca1f3)
```

## Querying Data

### Using Supabase Dashboard

1. Go to https://supabase.com/dashboard
2. Select your project
3. Navigate to Table Editor
4. View the `properties` table

### Using Supabase SQL Editor

```sql
-- Get all properties
SELECT * FROM properties ORDER BY scraped_at DESC;

-- Search by address
SELECT * FROM properties WHERE address ILIKE '%Los Angeles%';

-- Count properties
SELECT COUNT(*) FROM properties;

-- Get latest scraped properties
SELECT address, monthly_rent, bedrooms, bathrooms, scraped_at
FROM properties
ORDER BY scraped_at DESC
LIMIT 10;

-- Get properties with images
SELECT address, jsonb_array_length(images) as image_count
FROM properties
WHERE images IS NOT NULL
ORDER BY jsonb_array_length(images) DESC;
```

### Using Python Supabase Client

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Get all properties
response = supabase.table('properties').select('*').execute()
properties = response.data

# Search by address
response = supabase.table('properties')\
    .select('*')\
    .ilike('address', '%Los Angeles%')\
    .execute()

# Get specific property by URL
response = supabase.table('properties')\
    .select('*')\
    .eq('zillow_url', 'https://www.zillow.com/...')\
    .single()\
    .execute()

property_data = response.data
```

## API Response

When you scrape a property via the API, you get:

```json
{
  "address": "9255 Swallow Dr, Los Angeles, CA 90069",
  "monthly_rent": "90,000",
  "bedrooms": "7",
  "bathrooms": "12",
  "area": "12,237 sqft",
  "images": ["https://photos.zillowstatic.com/...", ...],
  "url": "https://www.zillow.com/homedetails/...",
  "scraped_at": "2025-11-07 13:46:04"
}
```

This same data is automatically saved to your Supabase database!

## Files Created

### Database Setup
- `create_table.sql` - Initial SQL schema (reference)
- `setup_database.py` - Initial setup script
- `fix_table.py` - Table recreation script (used)

### Integration
- `api.py` - Updated with Supabase integration
- `.env` - Contains Supabase credentials

## Benefits

### 1. Persistent Storage
- Data survives beyond JSON files
- Centralized database for all scraped properties
- Easy backups via Supabase

### 2. Query Capabilities
- Search by address, price, beds, baths
- Filter and sort data
- Aggregate statistics

### 3. Data History
- Track when properties were first scraped
- Track when data was last updated
- See price changes over time

### 4. Scalability
- Handle thousands of properties
- Fast indexed queries
- JSON storage for flexible image arrays

### 5. Integration
- Access data from any application
- Use Supabase REST API
- Build dashboards and analytics

## Data Flow

```
1. API receives scrape request
   ↓
2. Scraper extracts property data
   ↓
3. Data saved to JSON file ✅
   ↓
4. Data saved to Supabase ✅
   ↓
5. API returns response
```

## Troubleshooting

### Issue: "Column does not exist"

Run the fix script:
```bash
python fix_table.py
```

### Issue: "Connection failed"

Check your `.env` file has correct credentials:
```bash
cat .env | grep SUPABASE
```

### Issue: "Permission denied"

Verify RLS policies in Supabase dashboard:
- Go to Authentication > Policies
- Ensure "Enable all operations" policy exists

### Check Connection

```python
python -c "from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY')); print('✅ Connected!'); result = client.table('properties').select('count').execute(); print(f'Properties in database: {len(result.data)}')"
```

## Example: Building a Property Dashboard

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# Get summary statistics
response = supabase.table('properties').select('*').execute()
properties = response.data

total_properties = len(properties)
avg_rent = sum(int(p['monthly_rent'].replace(',', '')) for p in properties if p['monthly_rent']) / total_properties
avg_bedrooms = sum(int(p['bedrooms']) for p in properties if p['bedrooms']) / total_properties

print(f"Total Properties: {total_properties}")
print(f"Average Rent: ${avg_rent:,.2f}")
print(f"Average Bedrooms: {avg_bedrooms:.1f}")

# Get properties by city
from collections import Counter
cities = Counter(p['address'].split(',')[-2].strip() for p in properties if p['address'])
print("\nProperties by City:")
for city, count in cities.most_common(5):
    print(f"  {city}: {count}")
```

## Next Steps

1. ✅ Database is set up and working
2. ✅ API saves to both JSON and Supabase
3. ✅ Data is queryable via SQL or Python

You can now:
- Build analytics dashboards
- Create property comparison tools
- Track price changes over time
- Export data for analysis
- Integrate with other applications

## Support

- Supabase Dashboard: https://supabase.com/dashboard
- Supabase Docs: https://supabase.com/docs
- Python Client Docs: https://github.com/supabase-community/supabase-py

---

**Status**: ✅ Fully Operational
**Last Updated**: 2025-11-07
**Table**: `properties`
**Records**: View in Supabase dashboard
