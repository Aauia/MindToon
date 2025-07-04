# Supabase Setup Guide for MindToon

This guide will help you connect your MindToon project to Supabase for database and storage.

## Prerequisites

1. Create a Supabase account at [supabase.com](https://supabase.com)
2. Create a new Supabase project

## Step 1: Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy the following values:
   - **Project URL** (e.g., `https://your-project-ref.supabase.co`)
   - **Anon key** (public key for client-side operations)
   - **Service role key** (private key for server-side operations)

4. Navigate to **Settings** → **Database**
5. Copy the **Connection string** under "Connection pooling" or "Direct connection"

## Step 2: Configure Environment Variables

1. Open `backend/.env` file
2. Replace the placeholder values with your actual Supabase credentials:

```env
# Your Supabase project URL
SUPABASE_URL=https://your-project-ref.supabase.co

# Your Supabase anon key (for client-side operations)
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Your Supabase service role key (for server-side operations)
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Your Supabase PostgreSQL database URL
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

## Step 3: Set Up Supabase Storage

1. In your Supabase dashboard, go to **Storage**
2. Create a new bucket called `comics`
3. Set the bucket to **Public** (for serving comic images)
4. Configure the bucket policies:

```sql
-- Allow authenticated users to upload files
INSERT INTO storage.policies (name, bucket_id, policy)
VALUES (
  'Users can upload comic images',
  'comics',
  'bucket_id = ''comics'' AND auth.role() = ''authenticated'''
);

-- Allow public access to read files
INSERT INTO storage.policies (name, bucket_id, policy)
VALUES (
  'Public can view comic images',
  'comics',
  'bucket_id = ''comics'''
);
```

## Step 4: Set Up Database Tables

The project uses SQLModel which will automatically create tables. Run:

```bash
cd backend
python src/main.py --reset-db
```

This will create all necessary tables including:
- `user` (authentication)
- `comicspage` (user comics)
- `worldstats` (world statistics)
- `comiccollection` (comic collections)
- `comicCollectionitem` (collection items)

## Step 5: Test the Connection

1. Start your backend server:
```bash
cd backend
uvicorn src.main:app --reload
```

2. Visit `http://localhost:8000/health` to verify the API is running
3. Check the logs for any database connection errors

## Step 6: Verify Supabase Integration

1. **Database**: Check that tables are created in your Supabase dashboard under **Table Editor**
2. **Storage**: Verify the `comics` bucket exists under **Storage**
3. **API**: Test user registration and comic generation to ensure full integration

## Current Supabase Features

Your project already includes:

### ✅ Storage Integration
- Comic image uploads to Supabase Storage
- Automatic file organization by user ID
- Public URL generation for comic images

### ✅ Database Models
- User authentication system
- Comic creation and management
- World-based organization (Dream, Mind, Imagination worlds)
- Comic collections and favorites

### ✅ API Endpoints
- User registration/login
- Comic generation and storage
- World statistics tracking

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Your Supabase project URL | `https://abc123.supabase.co` |
| `SUPABASE_ANON_KEY` | Public API key | `eyJhbGciOiJIUzI1NiIs...` |
| `SUPABASE_SERVICE_ROLE_KEY` | Private API key | `eyJhbGciOiJIUzI1NiIs...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:pass@db.abc123.supabase.co:5432/postgres` |

## Troubleshooting

### Connection Issues
- Verify your environment variables are correct
- Check that your Supabase project is active
- Ensure your database password is correct

### Storage Issues
- Verify the `comics` bucket exists and is public
- Check bucket policies for proper permissions
- Ensure your Supabase project has sufficient storage quota

### Database Issues
- Run `python src/main.py --reset-db` to recreate tables
- Check Supabase logs for any SQL errors
- Verify your database URL includes the correct password

## Next Steps

After successful setup:
1. Test user registration via `/api/auth/register`
2. Generate a comic via `/api/chats/scenario/comic/sheet/`
3. Verify images are stored in Supabase Storage
4. Check user data in Supabase Table Editor

For iOS integration, see `ios_integration_guide.md`. 