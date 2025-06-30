# Database Schema Fix

## Problem
The error `column user.is_admin does not exist` occurs when the existing database table doesn't match the current User model definition. This typically happens when:

1. The database was created before the `is_admin` field was added to the User model
2. Database migrations weren't run after model changes

## Solutions

### Option 1: Reset Database (Quick Fix)
**Warning: This will delete all existing data**

Run the main application with the reset flag:
```bash
cd backend/src
python main.py --reset-db
```

### Option 2: Use the Reset Script
```bash
cd backend
python reset_database.py
```

### Option 3: Manual Database Reset (using Docker)
If using Docker Compose:
```bash
# Stop the containers
docker-compose down

# Remove the database volume (this deletes all data)
docker volume prune

# Start again
docker-compose up --build
```

### Option 4: Manual SQL Fix (Advanced)
If you want to preserve existing data, you can manually add the missing column:

```sql
ALTER TABLE "user" ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
```

## Prevention
To avoid this issue in the future:
1. Use proper database migration tools like Alembic
2. Always backup data before schema changes
3. Test schema changes in development first

## Admin User
After fixing the database, an admin user will be created with:
- Username: `admin`
- Password: `ad123`
- Email: `adminof@mindtoon.com`

## Verification
After fixing, the API should start successfully and you should see:
- "Database models created successfully"
- "Created admin user successfully" (if creating for the first time) 