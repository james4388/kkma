from django.core.management.base import BaseCommand, CommandError
from kkma.models import Example

from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Clean up and vacuum table'

    def handle(self, *args, **options):
        cursor = connection.cursor()
    
        cursor.execute("VACUUM")
        transaction.commit()