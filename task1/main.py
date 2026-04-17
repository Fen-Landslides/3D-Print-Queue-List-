from repositories.factory import create_repository
from services.queue_manager import QueueManager
from services.pin_manager import PinManager
from services.export_service import ExportService
from services.notification_service import TkinterNotifier
from interfaces.tk_app import QueueApp


def main():
    repo = create_repository()
    notifier = TkinterNotifier()
    queue_manager = QueueManager(repo, notifier)
    pin_manager = PinManager(repo)
    export_service = ExportService(repo)
    app = QueueApp(queue_manager, pin_manager, export_service)
    app.run()


if __name__ == "__main__":
    main()
