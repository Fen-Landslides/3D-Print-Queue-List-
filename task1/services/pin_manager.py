class PinManager:
    def __init__(self, repository):
        self.repository = repository

    def verify_pin(self, pin: str) -> bool:
        config = self.repository.load_config()
        if not config.admin_pin:
            return True
        return config.admin_pin == pin

    def require_valid_pin(self, pin: str):
        if not self.verify_pin(pin):
            raise ValueError("Invalid admin PIN.")

    def update_pin(self, old_pin: str, new_pin: str | None):
        config = self.repository.load_config()
        if config.admin_pin and old_pin != config.admin_pin:
            raise ValueError("Old PIN is incorrect.")
        if new_pin:
            if not new_pin.isdigit() or not 4 <= len(new_pin) <= 8:
                raise ValueError("PIN must be 4-8 digits.")
        config.admin_pin = new_pin
        self.repository.save_config(config)

    def has_pin(self) -> bool:
        return bool(self.repository.load_config().admin_pin)
