# User Account Deletion System

## Overview

The MindToon platform now supports **complete user account deletion** with comprehensive data cleanup. This feature allows users to permanently delete their accounts and all associated data with proper safeguards and confirmation requirements.

## 🔐 Security Features

### **Authentication Required**
- Users must be logged in with a valid JWT token
- Only users can delete their own accounts
- No admin or cross-user deletion capability

### **Multi-Step Confirmation**
- Explicit boolean confirmation required
- Username must be typed exactly
- Understanding acknowledgment phrase required
- Prevents accidental deletions

## 📋 API Endpoints

### **1. Get Deletion Information**
```http
GET /api/auth/deletion-info
Authorization: Bearer <jwt_token>
```

**Purpose**: Shows user what will be deleted before they confirm

**Response**:
```json
{
  "user_info": {
    "username": "john_doe",
    "email": "john@example.com",
    "account_created": "2024-01-15T10:30:00Z",
    "full_name": "John Doe"
  },
  "data_to_be_deleted": {
    "comics": 15,
    "detailed_scenarios": 15,
    "collections": 3,
    "world_statistics": 3,
    "images_in_storage": 12
  },
  "warning": {
    "message": "Account deletion is PERMANENT and IRREVERSIBLE",
    "consequences": [
      "All your comics will be permanently deleted",
      "All your detailed stories will be permanently deleted",
      "All your collections will be permanently deleted",
      "All your uploaded images will be permanently deleted from storage",
      "Your account and login credentials will be permanently deleted",
      "This action cannot be undone"
    ]
  },
  "deletion_endpoint": "DELETE /api/auth/delete-account"
}
```

### **2. Delete User Account**
```http
DELETE /api/auth/delete-account
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "confirm_deletion": true,
  "username_confirmation": "john_doe",
  "understanding_acknowledgment": "I understand this action is permanent and irreversible"
}
```

**Response** (on success):
```json
{
  "success": true,
  "username": "john_doe",
  "message": "Account 'john_doe' and all associated data have been permanently deleted.",
  "deletion_summary": {
    "user_id": 123,
    "username": "john_doe",
    "comics_deleted": 15,
    "scenarios_deleted": 15,
    "images_deleted": 12,
    "collections_deleted": 3,
    "collection_items_deleted": 8,
    "world_stats_deleted": 3,
    "storage_cleanup_errors": []
  },
  "warning": "This action was irreversible. All your comics, stories, and account data have been permanently removed."
}
```

## 🗑️ What Gets Deleted

### **1. Supabase Storage Cleanup**
- All comic images uploaded by the user
- Files are permanently removed from cloud storage
- Any storage errors are logged but don't stop the deletion

### **2. Database Cleanup (in order)**
1. **Collection Items** - Junction table entries
2. **Collections** - User's comic collections
3. **Detailed Scenarios** - Rich narrative stories
4. **Comics** - Comic metadata and panel data
5. **World Statistics** - User's world-specific stats
6. **User Account** - The user record itself

### **3. Relationship Handling**
- Foreign key constraints properly handled
- Cascade deletion prevents orphaned records
- Transaction-based (all-or-nothing) approach

## 🛡️ Safety Features

### **Confirmation Requirements**
All three fields are required and validated:

```json
{
  "confirm_deletion": true,  // Must be exactly true
  "username_confirmation": "exact_username",  // Must match exactly
  "understanding_acknowledgment": "I understand this action is permanent and irreversible"  // Must be exact phrase
}
```

### **Error Handling**
- Storage deletion errors don't stop account deletion
- Database errors trigger rollback (nothing gets deleted)
- Comprehensive logging for debugging
- Detailed error messages for users

### **Transaction Safety**
- Single database transaction for all deletions
- If any step fails, entire deletion is rolled back
- Prevents partial account deletion scenarios

## 💻 Frontend Integration Examples

### **React/JavaScript Example**
```javascript
// Step 1: Get deletion info
const getDeletionInfo = async () => {
  const response = await fetch('/api/auth/deletion-info', {
    headers: {
      'Authorization': `Bearer ${userToken}`
    }
  });
  const info = await response.json();
  
  // Show user what will be deleted
  console.log(`You have ${info.data_to_be_deleted.comics} comics that will be deleted`);
  return info;
};

// Step 2: Confirm and delete account
const deleteAccount = async (username) => {
  const confirmation = {
    confirm_deletion: true,
    username_confirmation: username,
    understanding_acknowledgment: "I understand this action is permanent and irreversible"
  };
  
  const response = await fetch('/api/auth/delete-account', {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${userToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(confirmation)
  });
  
  if (response.ok) {
    const result = await response.json();
    console.log(`Account deleted: ${result.message}`);
    // Redirect to login or goodbye page
    window.location.href = '/goodbye';
  } else {
    const error = await response.json();
    console.error('Deletion failed:', error.detail);
  }
};
```

### **Swift/iOS Example**
```swift
struct DeletionConfirmation: Codable {
    let confirmDeletion: Bool
    let usernameConfirmation: String
    let understandingAcknowledgment: String
    
    enum CodingKeys: String, CodingKey {
        case confirmDeletion = "confirm_deletion"
        case usernameConfirmation = "username_confirmation"
        case understandingAcknowledgment = "understanding_acknowledgment"
    }
}

func deleteAccount(username: String) async {
    let confirmation = DeletionConfirmation(
        confirmDeletion: true,
        usernameConfirmation: username,
        understandingAcknowledgment: "I understand this action is permanent and irreversible"
    )
    
    // Make DELETE request to /api/auth/delete-account
    // Handle response and navigate to appropriate screen
}
```

## 📊 Logging and Monitoring

### **Log Levels**
- **INFO**: Successful deletion steps
- **WARNING**: Storage cleanup issues (non-critical)
- **ERROR**: Critical failures that stop deletion

### **Log Format**
```
🗑️ Starting account deletion for user: john_doe (ID: 123)
🗑️ Step 1: Deleting comic images from Supabase Storage...
✅ Deleted image: https://supabase.co/storage/comics/user123/comic456.png
✅ Deleted 12 images from storage
🗑️ Step 2: Deleting collection items...
✅ Deleted 8 collection items
🗑️ Step 3: Deleting collections...
✅ Deleted 3 collections
🗑️ Step 4: Deleting detailed scenarios...
✅ Deleted 15 scenarios
🗑️ Step 5: Deleting comics...
✅ Deleted 15 comics
🗑️ Step 6: Deleting world stats...
✅ Deleted 3 world stats
🗑️ Step 7: Deleting user account...
✅ Account deletion completed successfully for user: john_doe
```

## ⚠️ Important Considerations

### **Data Recovery**
- **No recovery possible** after deletion
- **No backup retention** of deleted user data
- **Immediate permanent removal** from all systems

### **Session Handling**
- User's JWT token becomes invalid immediately
- Any active sessions should be terminated
- Frontend should redirect to login/goodbye page

### **Rate Limiting**
Consider implementing rate limiting on deletion endpoint to prevent abuse:
```python
# Example: Max 1 deletion attempt per hour per IP
@limiter.limit("1/hour")
@router.delete("/delete-account")
```

### **Audit Trail**
Consider logging deletion events to a separate audit system:
```python
# Log to audit system (outside main database)
audit_logger.info({
    "action": "account_deletion",
    "user_id": user.id,
    "username": user.username,
    "timestamp": datetime.utcnow(),
    "deletion_stats": deletion_stats
})
```

## 🧪 Testing

### **Check Supabase Status Before Deletion**
```bash
curl -X GET "http://localhost:8000/api/auth/supabase-status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

This shows you:
- Whether Supabase is properly configured
- How many comics would be deleted from storage
- Environment variable status
- Connection test results

### **Test the Deletion Info Endpoint**
```bash
curl -X GET "http://localhost:8000/api/auth/deletion-info" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### **Test Account Deletion** (be careful!)
```bash
curl -X DELETE "http://localhost:8000/api/auth/delete-account" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "confirm_deletion": true,
    "username_confirmation": "your_username",
    "understanding_acknowledgment": "I understand this action is permanent and irreversible"
  }'
```

### **Test Validation Errors**
```bash
# Test wrong username
curl -X DELETE "http://localhost:8000/api/auth/delete-account" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "confirm_deletion": true,
    "username_confirmation": "wrong_username",
    "understanding_acknowledgment": "I understand this action is permanent and irreversible"
  }'
```

### **Diagnose Supabase Issues**
```bash
# Run the diagnostic script
cd backend
python test_supabase_deletion.py
```

This comprehensive test checks:
- Environment variables
- Supabase connection
- Storage bucket existence
- Comics in database
- URL format validation

## 🔧 Troubleshooting

### **Supabase Storage Not Deleting**

**Symptoms**: Logs show "Step 1: Deleting comic images from Supabase Storage..." but no deletion messages follow.

**Causes & Solutions**:

1. **Supabase Client Not Initialized**
   ```bash
   # Check status
   curl -X GET "http://localhost:8000/api/auth/supabase-status" -H "Authorization: Bearer YOUR_TOKEN"
   
   # Run diagnostic
   python test_supabase_deletion.py
   ```
   
   **Fix**: Check environment variables in `.env`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_key
   ```

2. **No Comics with Supabase URLs**
   - Comics might only have base64 data (no cleanup needed)
   - Check logs for "Comics with Supabase URLs: 0"

3. **Missing Storage Bucket**
   - Create 'comics' bucket in Supabase dashboard
   - Make bucket public for read access

4. **Permission Issues**
   - Use service role key instead of anon key
   - Check bucket policies in Supabase

### **Environment Variable Issues**

**Check Variables**:
```bash
# In backend directory
grep -E "(SUPABASE_|DATABASE_)" .env
```

**Common Issues**:
- Placeholder values not replaced
- Missing service role key
- Incorrect project URL

### **Database Connection Issues**

**Symptoms**: Other steps work but database operations fail

**Solutions**:
- Verify DATABASE_URL in `.env`
- Check PostgreSQL connection
- Ensure tables exist: `python src/main.py --reset-db`

### **Partial Deletion**

**Symptoms**: Some data deleted but errors occurred

**Recovery**:
- Check `deletion_summary` in response
- Review `storage_cleanup_errors` array
- Manually clean up remaining Supabase files if needed

### **Log Analysis**

**Key Log Messages**:
```
✅ Found X total comics for user username
📁 Comics with Supabase URLs: X
❌ Supabase client not available!
✅ Successfully deleted image X: url
```

**Debug Mode**:
```bash
# Set debug logging
export LOG_LEVEL=DEBUG
# Check detailed logs in Docker or console
```

## 🚀 Deployment Checklist

- [ ] Test deletion in development environment
- [ ] Verify Supabase storage cleanup works (`python test_supabase_deletion.py`)
- [ ] Test all validation error cases
- [ ] Set up proper logging/monitoring
- [ ] Add rate limiting if needed
- [ ] Update frontend to use new endpoints
- [ ] Create user-facing deletion flow
- [ ] Test with various data volumes
- [ ] Verify transaction rollback works
- [ ] Document any deployment-specific configurations
- [ ] Check Supabase status endpoint works
- [ ] Verify environment variables in production

---

## Support

For questions about the user deletion system:

### **Quick Diagnostics**
1. Check Supabase status: `GET /api/auth/supabase-status`
2. Run diagnostic script: `python test_supabase_deletion.py`
3. Check deletion info: `GET /api/auth/deletion-info`

### **Common Issues**
- **No Supabase deletion**: Environment variables not set
- **Partial deletion**: Storage permissions or bucket missing
- **Database errors**: Connection issues or missing tables

### **Debug Steps**
1. Verify environment variables
2. Test Supabase connection
3. Check storage bucket exists
4. Verify comics have URLs vs base64 only
5. Test storage permissions

**Remember**: User deletion is permanent and irreversible. Use with caution! 🚨 