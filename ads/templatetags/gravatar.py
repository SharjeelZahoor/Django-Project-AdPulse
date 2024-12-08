import hashlib
from django import template

register = template.Library()

@register.filter
def gravatar(email, size=40):
    """Generate Gravatar URL based on the email."""
    if not email:
        return f"https://www.gravatar.com/avatar/?s={size}&d=identicon"
    hashed_email = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{hashed_email}?s={size}"
