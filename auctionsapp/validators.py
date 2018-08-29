from django.core.exceptions import ValidationError
from datetime import date, timedelta


def validate_3_days_from_now(value):
    min_date = date.today() + timedelta(days=3)
    if min_date > value:
        raise ValidationError(
            '%(value)s must be at least 3 days from now',
            params={'value': date.strftime(value, "%d/%m/%Y")},
        )