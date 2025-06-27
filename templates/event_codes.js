// Science Olympiad Event Codes
// This file contains all event codes for attendance tracking

const EVENT_CODES = {
    // Math & Physics Events
    "MP01": "Air Trajectory",
    "MP02": "Optics",
    "MP03": "Wind Power",
    "MP04": "Bungee Drop",
    "MP05": "Codebusters",
    "MP06": "Experimental Design",
    
    // Earth Science Events
    "ES01": "Astronomy",
    "ES02": "Dynamic Planet",
    "ES03": "Fossils",
    "ES04": "Geologic Mapping",
    
    // Chemistry Events
    "CH01": "Chem Lab",
    "CH02": "Forensics",
    "CH03": "Materials Science",
    
    // Biology Events
    "BIO01": "Anatomy and Physiology",
    "BIO02": "Disease Detectives",
    "BIO03": "Ecology",
    "BIO04": "Entomology",
    "BIO05": "Microbe Mission",
    
    // Build Events
    "BE01": "Electric Vehicle",
    "BE02": "Helicopter",
    "BE03": "Robot Tour",
    "BE04": "Tower",
    
    // General Events
    "GEN01": "Team Meeting",
    "GEN02": "Workshop",
    "GEN03": "Competition",
    "GEN04": "Practice Session"
};

// Function to get event name from code
function getEventName(code) {
    return EVENT_CODES[code] || "Unknown Event";
}

// Function to get all event codes
function getAllEventCodes() {
    return Object.keys(EVENT_CODES);
}

// Function to get all events with their codes
function getAllEvents() {
    const events = [];
    for (const [code, name] of Object.entries(EVENT_CODES)) {
        events.push({ code, name });
    }
    return events;
}

// Export functions if using modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EVENT_CODES,
        getEventName,
        getAllEventCodes,
        getAllEvents
    };
} 