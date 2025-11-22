from datetime import timezone, timedelta

# Common timezones:
# UTC: timezone.utc
# IST (India): timezone(timedelta(hours=5, minutes=30))
# EST: timezone(timedelta(hours=-5))
# PST: timezone(timedelta(hours=-8))
USER_TIMEZONE = timezone(timedelta(hours=5, minutes=30))  # IST by default

YOUTUBE_CHANNELS = [
    "UCn8ujwUInbJkBhffxqAPBVQ",  # Dave Ebbelaar
    "UCawZsQWqfGSbCI5yjkdVkTA",  # Matthew Berman
]