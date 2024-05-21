from datetime import datetime, timedelta, timezone
import pytz
from config.config import TROPHIES_INTERVAL

def get_current_time():
    """
    Get the current time in UTC.

    Returns:
        A datetime object representing the current time in UTC.
    """
    return datetime.now(timezone.utc)

def delay_until_next_interval(interval_type):
    """
    A function to calculate the delay to start the task until the next interval.

    Args:
    - interval_type: Type of interval ('trophies', or other).

    Returns:
    Integer representing the delay in seconds until the next interval.
    """
    now = datetime.now()
    interval = TROPHIES_INTERVAL if interval_type == 'trophies' else 0
    minutes = (now.minute // interval + 1) * interval if interval != 0 else 0
    if minutes < 60:
        future = now.replace(minute=minutes, second=0, microsecond=0)
    else:
        future = now.replace(hour=(now.hour + 1) % 24, minute=0, second=0, microsecond=0)
        if future < now:
            future += timedelta(days=1)
    delta_s = (future - now).total_seconds()
    return round(delta_s)

def calculate_total_time(td):
    """
    Calculate the total time duration in years, weeks, days, hours, and minutes based on the input timedelta.

    Args:
        td: A timedelta object representing the duration to be calculated.

    Returns:
        A formatted string representing the total time duration in years, weeks, days, hours, and minutes.

    Examples:
        calculate_total_time(timedelta(days=380, hours=12, minutes=30))  # Returns '1 year, 1 week, 5 days, 12 hours and 30 minutes'
    """
    minutes, _ = divmod(td.seconds + td.days * 86400, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    years, weeks = divmod(weeks, 52)

    result = []
    if years:
        result.append(f"{years} year{'s' if years > 1 else ''}")
    if weeks:
        result.append(f"{weeks} week{'s' if weeks > 1 else ''}")
    if days:
        result.append(f"{days} day{'s' if days > 1 else ''}")
    if hours:
        result.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes:
        result.append(f"{minutes} minute{'s' if minutes > 1 else ''}")

    if len(result) > 1:
        last = result.pop()
        return ', '.join(result) + ' and ' + last
    elif result:
        return result[0]
    else:
        return ''

def format_date(date: datetime) -> str:
    """
    Formats the date to Amsterdam timezone.

    Parameters
    ----------
    date : datetime
        The date to be formatted.

    Returns
    -------
    str
        The formatted date.
    """
    amsterdam_tz = pytz.timezone('Europe/Amsterdam')
    date = date.astimezone(amsterdam_tz)
    return date.strftime("%d/%m/%y %H:%M:%S")