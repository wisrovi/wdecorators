"""Example: notify_on_error decorator - callback on error."""

from wdecorators import notify_on_error

alerts = []


def send_alert(error):
    alerts.append(str(error))
    print(f"Alert sent: {error}")


@notify_on_error(send_alert)
def critical_operation():
    raise RuntimeError("System failure")


try:
    critical_operation()
except RuntimeError:
    print("Exception re-raised after notification")

print(f"Alerts collected: {alerts}")
