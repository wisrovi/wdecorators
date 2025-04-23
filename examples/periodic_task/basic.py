from wdecorators import Periodic_task_sched

# Inicializar el controlador
controller = Periodic_task_sched()
controller.set_database(None)  # Usar SQLite por defecto


@controller.periodic_execution(interval=5, priority="alta", enable_api=True)
def task_critical():
    print("Ejecutando tarea crítica...")


@controller.periodic_execution(interval=10, priority="media")
def task_secondary():
    print("Ejecutando tarea secundaria...")


task_critical()
task_secondary()

# Iniciar API si es necesario
controller.start_api()
