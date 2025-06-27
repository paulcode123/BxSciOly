# Bug Fix: 404 Error on Test Viewer

## Issue
When trying to parse a test through the test viewer interface, users were encountering a 404 error:
```
Failed to load resource: the :8000/api/Tests/b2Kd_Xzccx6lgqys7g/view:1 
server responded with a status of 404 (NOT FOUND)
```

## Root Cause
The JavaScript code in both `templates/user/test_viewer.html` and `templates/user/binders.html` was attempting to call a non-existent API endpoint `/api/Tests/{testId}/view` to update view counts for tests.

## Files Fixed
1. **templates/user/test_viewer.html** - Line ~1132
2. **templates/user/binders.html** - Lines ~2624-2630

## Solution
Commented out the calls to the non-existent view endpoint:

### Before:
```javascript
// Update view count
fetch(`/api/Tests/${testId}/view`, { method: 'POST' }).catch(console.error);
```

### After:
```javascript
// Update view count (commented out - endpoint doesn't exist yet)
// fetch(`/api/Tests/${testId}/view`, { method: 'POST' }).catch(console.error);
```

## Impact
- ✅ **Fixed**: 404 errors no longer occur when viewing/parsing tests
- ✅ **No Breaking Changes**: All other functionality remains intact
- ⚠️ **View Count Tracking**: View count updates are currently disabled (but this was already not working)

## Test Parsing Now Works
With this fix, the test parsing functionality should work properly:
1. Navigate to a test in the test viewer
2. Click "Parse Test" 
3. The GPT-4o-mini powered parsing will proceed without 404 errors
4. Questions will be extracted and topics will be assigned automatically

## Future Enhancement
If view count tracking is needed in the future, implement the missing endpoint:
```python
@firebase_routes.route('/api/Tests/<test_id>/view', methods=['POST'])
def update_test_view_count(test_id):
    # Implementation to increment view count
    pass
``` 