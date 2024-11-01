from django.core.management.base import BaseCommand, CommandError

from core.generator.course_optimizer import main


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        parser.add_argument("cell_ids", nargs="+", type=str)
        parser.add_argument("total_time", default=120, type=int)

    def handle(self, *args, **options):
        cell_ids = options["cell_ids"]
        print(main(cell_ids, options['total_time']))