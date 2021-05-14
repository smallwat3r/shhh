# pylint: disable=line-too-long

def add_security_headers(response):
    """Add required security headers."""
    response.headers.add("X-Frame-Options", "SAMEORIGIN")
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-XSS-Protection", "1; mode=block")
    response.headers.add("Referrer-Policy", "no-referrer-when-downgrade")
    response.headers.add(
        "Strict-Transport-Security", "max-age=63072000; includeSubdomains; preload"
    )
    response.headers.add(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self'; object-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    )
    response.headers.add(
        "feature-policy",
        "accelerometer 'none'; camera 'none'; geolocation 'none'; gyroscope 'none'; magnetometer 'none'; microphone 'none'; payment 'none'; usb 'none'",
    )
    return response
