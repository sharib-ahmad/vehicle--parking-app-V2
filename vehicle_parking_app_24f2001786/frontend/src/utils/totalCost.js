export const totalCost = (selectedReservation) => {
    if (!selectedReservation) return 0;
    
    const utcTimestamp = selectedReservation.parking_timestamp;
    
    // Ensure the timestamp from the backend is parsed as UTC for accurate calculation
    const compliantTimestamp = utcTimestamp.includes('Z') ? utcTimestamp : utcTimestamp.replace(' ', 'T') + 'Z';
    const parkingStartTime = new Date(compliantTimestamp).getTime();

    // Check for invalid date
    if (isNaN(parkingStartTime)) {
        console.error("Invalid parking_timestamp:", utcTimestamp);
        return 0;
    }

    const parkingEndTime = new Date().getTime();
    const durationInMilliseconds = parkingEndTime - parkingStartTime;

    // Handle cases where leaving time is before parking time
    if (durationInMilliseconds < 0) {
        console.warn("Parking duration is negative. Check system clocks.");
        return 0;
    }

    const durationInHours = durationInMilliseconds / (1000 * 60 * 60);

    // Charge for a minimum of 1 hour, and round up to the next hour
    const billedHours = Math.max(1,durationInHours);

    return billedHours * selectedReservation.parking_cost_per_hour;
};