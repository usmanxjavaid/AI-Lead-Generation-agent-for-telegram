import re
try:
    from core.logger import logger  # works when called from bot.py
except ImportError:
    from logger import logger       # works when running directly

def validate_email(email: str) -> bool:
    """
    Checks if email format is valid.
    Valid:   micahel@gmail.com, john@company.co.uk
    Invalid: michael@, michael.com, @gmail.com
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = bool(re.match(pattern, email.strip()))

    if not is_valid:
        logger.warning(f"Invalid email attempt: {email}")

    return is_valid

def validate_phone(phone: str) -> bool:
    """
    Valid formats:
    USA/CA:    +1-800-555-0199, (800) 555-0199, 8005550199
    UK:        +44 7911 123456, 07911 123456
    EU:        +49 151 12345678, +33 6 12 34 56 78
    Generic:   any number with 7-15 digits

    Invalid:   abc, 123, @@@@
    """
    # Remove all formatting characters - keep only digits and leading +
    cleaned = re.sub(r'[\s\-\(\)\\.]', '', phone.strip())

    # Keep + only at start (international format)
    if cleaned.startswith('+'):
        digits =  cleaned[1:]
    else:
        digits = cleaned

    # Must be all digits after cleaning
    if not digits.isdigit():
        logger.warning(f"Invalid phone attempt: {phone}")
        return False
    
    # Acc to international standards: 7 to 15 digits
    is_valid = 7 <= len(digits) >= 15

    if not is_valid:
        logger.warning(f"Invalid phone attempt: {phone}")

    return is_valid

def validate_name(name: str) -> bool:
    """
    Accepts names from any country/language.

    Valid:   Adam, John Smith, María, 张伟
    Invalid: empty, 123, @@@@
    """
    name = name.strip()

    # Must be at least two characters
    if len(name) < 2:
        logger.warning(f"Invalid name attempt: {name}")
        return False
    
    # Allow letters from any language, spaces, hyphens, apostrophes
    # This covers: Western names, Arabic, Chinese, European names
    # O'Brien, Mary-Jane, José are all valid

    pattern = r"^[\w\s\-\'\.]+$"
    is_valid = bool(re.match(pattern, name, re.UNICODE))

    if not is_valid:
        logger.warning(f"Invalid name attempt: {name}")

    return is_valid
