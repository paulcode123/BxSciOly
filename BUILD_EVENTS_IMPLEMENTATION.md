# Build Events Implementation Summary

## Overview
Build events now have a flexible attendance system with weekly requirements that scale based on the number of events a student is enrolled in.

---

## Build Events Schedule

### Events
- Boomilever
- Helicopter
- Electric Vehicle
- Robot Tour
- Bungee Drop
- Hovercraft

### Meeting Times
**Days**: Tuesday, Wednesday, Thursday  
**Blocks**: Both Block 1 and Block 2 each day

Each build event has **2 meetings per day** (one in each block), totaling **6 possible meeting times per week** per event.

---

## Attendance Requirements

Students must attend a certain number of blocks per week based on how many build events they're in:

| # of Build Events | Required Blocks/Week |
|-------------------|---------------------|
| 1 event          | 2 blocks            |
| 2 events         | 3 blocks            |
| 3+ events        | 4 blocks            |

**Example**: A student in Helicopter and Boomilever (2 events) must attend 3 blocks total per week across those events.

---

## Backend Changes

### Code Generation (`routes/firebase_routes.py`)

**Updated**: `/api/Meeting/generate-today` endpoint

```python
# On Tues/Wed/Thurs, generates TWO meetings per build event
if today in ['Tuesday', 'Wednesday', 'Thursday']:
    for build_event in build_events:
        # Block 1 meeting
        todays_events.append({
            'eventName': build_event,
            'block': '1',
            'time': '3:45 - 4:20 PM'
        })
        # Block 2 meeting
        todays_events.append({
            'eventName': build_event,
            'block': '2',
            'time': '4:25 - 5:00 PM'
        })
```

**Result**: On build days, clicking "Generate Today's Codes" creates 12 build meetings (6 events × 2 blocks).

---

## Admin Portal Changes

### Today's Codes Display

**Updated**: `templates/admin_attendance.html`

1. **Separated Sections**: Academic events and build events now show in separate grids
2. **Visual Distinction**: Build events have a yellow/amber background (`#fef3c7`) with orange border
3. **Organized by Block**: Both sections grouped by Block 1 and Block 2
4. **Build Icon**: Build section has a tools icon (🔧)

**Layout**:
```
┌─────────────────────────────────┐
│ Academic Events                 │
│  ┌─ Block 1 ─────────────────┐ │
│  │ Anatomy, Circuit Lab, etc  │ │
│  └────────────────────────────┘ │
│  ┌─ Block 2 ─────────────────┐ │
│  │ Remote Sensing, etc        │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ 🔧 Build Events (Amber/Orange)  │
│  ┌─ Block 1 ─────────────────┐ │
│  │ Boomilever, Helicopter...  │ │
│  └────────────────────────────┘ │
│  ┌─ Block 2 ─────────────────┐ │
│  │ Boomilever, Helicopter...  │ │
│  └────────────────────────────┘ │
└─────────────────────────────────┘
```

### Panel Reorganization

**Moved**: "Create New Meeting" → Bottom of page, renamed to **"Create Unscheduled Meeting"**

**New Order**:
1. Today's Attendance Codes (top)
2. Event & Meeting Selection
3. Attendance Chart Panel
4. Meeting Details Panel
5. Member Lookup Panel
6. Create Unscheduled Meeting (bottom)

---

## User Portal Changes

### New Build Attendance Tracker

**Added**: `templates/user/meetings.html`

Students enrolled in build events see a new section at the top of their meetings page:

#### Features

1. **Auto-Detection**: Only shows if student is in at least one build event
2. **Weekly Requirement Display**: Shows required blocks based on number of events
3. **Progress Tracking**: Visual progress bar and count (e.g., "3/4 blocks this week")
4. **Status Colors**:
   - 🟢 Green: Met requirement
   - 🟡 Yellow: 1 block away from requirement
   - 🔴 Red: 2+ blocks away from requirement

5. **Per-Event Breakdown**: Shows each build event with individual meeting attendance
6. **Meeting Badges**: Shows each meeting as a badge with checkmark if attended

#### Example Display

```
┌──────────────────────────────────────────────┐
│ 🔧 Build Events Attendance (This Week)      │
├──────────────────────────────────────────────┤
│ Weekly Requirement                 3/4       │
│ You're in 3 build events: Boomilever,        │
│ Helicopter, Electric Vehicle                 │
│ ███████████░░░░░ 75%                         │
├──────────────────────────────────────────────┤
│ This Week's Meetings                         │
│                                              │
│ Boomilever                          2/6      │
│ [✓ Tue B1] [✓ Wed B1] [○ Thu B1]            │
│ [○ Tue B2] [○ Wed B2] [○ Thu B2]            │
│                                              │
│ Helicopter                          1/6      │
│ [✓ Tue B1] [○ Wed B1] [○ Thu B1]            │
│ [○ Tue B2] [○ Wed B2] [○ Thu B2]            │
│                                              │
│ Electric Vehicle                    0/6      │
│ [○ Tue B1] [○ Wed B1] [○ Thu B1]            │
│ [○ Tue B2] [○ Wed B2] [○ Thu B2]            │
└──────────────────────────────────────────────┘
```

#### Implementation Details

```javascript
// Calculate requirement
let requiredBlocks = 0;
if (userBuildEvents.length === 1) requiredBlocks = 2;
else if (userBuildEvents.length === 2) requiredBlocks = 3;
else if (userBuildEvents.length >= 3) requiredBlocks = 4;

// Get current week (Monday - Sunday)
const weekStart = getMondayOfWeek();
const weekEnd = getSundayOfWeek();

// Count attended blocks this week
const attendedCount = thisWeekBuildMeetings.filter(m => 
    m.attended && m.attended.includes(currentUserId)
).length;
```

**Auto-Refresh**: Updates automatically after student checks in with a code

---

## Database Schema

### Meeting Document Structure

Each build meeting follows standard Meeting structure:

```javascript
{
  id: "auto-generated",
  eventName: "Boomilever", // or other build event
  date: timestamp,         // Tuesday, Wednesday, or Thursday
  code: "XYZ",            // 3-letter code
  block: "1",             // or "2"
  room: "",               // optional
  attended: ["memberId1", "memberId2", ...]
}
```

**Note**: Build events use blocks "1" and "2" (not "Build") so they integrate seamlessly with the block-based display system.

---

## User Experience Flow

### For Admins

1. **Tuesday/Wednesday/Thursday morning**:
   - Open Attendance Management
   - Click "Generate Today's Codes"
   - 12 build meetings created (6 events × 2 blocks)
   - Share codes with students (post on board, announce, etc.)

2. **During/After meetings**:
   - Monitor real-time check-ins
   - See attendance counts update live
   - Build events highlighted in amber section

### For Students

1. **Check requirements**:
   - Open Meetings page
   - See build attendance tracker at top
   - Review weekly requirement

2. **Attend meetings**:
   - Show up to any available block
   - Enter code on Meetings page
   - See confirmation + tracker updates

3. **Track progress**:
   - Monitor progress bar throughout week
   - See which meetings attended
   - Stay on track to meet requirement

---

## Key Benefits

✅ **Flexible Schedule**: Students can choose which blocks to attend  
✅ **Clear Requirements**: No confusion about expectations  
✅ **Real-Time Tracking**: Students always know where they stand  
✅ **Easy Administration**: One click generates all codes  
✅ **Visual Feedback**: Color-coded status makes it obvious  
✅ **Scalable**: Works for students in 1-3+ events  
✅ **Weekly Reset**: Fresh start every Monday

---

## Testing Checklist

- [ ] Generate codes on Tuesday - verify 12 build meetings created
- [ ] Generate codes on Wednesday - verify no duplicates
- [ ] Student in 1 build event sees "2 blocks required"
- [ ] Student in 2 build events sees "3 blocks required"
- [ ] Student in 3 build events sees "4 blocks required"
- [ ] Progress bar updates after check-in
- [ ] Status color changes (green/yellow/red)
- [ ] Week resets on Monday
- [ ] Build events show in separate amber section
- [ ] Academic events show in separate blue section
- [ ] Create Unscheduled Meeting panel at bottom

---

## Future Enhancements (Optional)

- **Email Reminders**: Send reminder if student hasn't met requirement by Thursday
- **Historical Tracking**: Show build attendance over multiple weeks
- **Leaderboard**: Show which build teams have best attendance
- **Auto-Assignment**: Suggest which blocks to attend based on availability
- **Calendar Integration**: Add build meeting times to personal calendar

