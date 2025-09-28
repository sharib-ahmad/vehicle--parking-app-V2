export const formatTimestampToIST = (utcTimestamp) => {
  if (!utcTimestamp) return '';

  let date;
  // If the timestamp is a string (from the backend), ensure it's parsed as UTC.
  if (typeof utcTimestamp === 'string') {
    // The format 'YYYY-MM-DD HH:MM:SS' is interpreted as local time by many browsers.
    // To treat it as UTC, we replace the space with 'T' and append 'Z'.
    const compliantTimestamp = utcTimestamp.includes('Z') ? utcTimestamp : utcTimestamp.replace(' ', 'T') + 'Z';
    date = new Date(compliantTimestamp);
  } else {
    // If it's already a Date object (like the 'leavingTime'), use it directly.
    date = new Date(utcTimestamp);
  }

  // Check for an invalid date after parsing
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }

  const options = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
    hour12: true,
    timeZone: 'Asia/Kolkata' // Specify the target timezone
  };

  return date.toLocaleString('en-IN', options);
};

export const formatTime = (timeStr) => {
  if (!timeStr) return '';
  const [hourStr, minute] = timeStr.split(':');
  let hour = parseInt(hourStr, 10);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  hour = hour % 12 || 12;
  return `${hour}:${minute} ${ampm}`;
};