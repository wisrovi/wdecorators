from wdecorators import Periodic_task_sched

# Inicializar el controlador
controller = Periodic_task_sched()
controller.set_database(None)  # Usar SQLite por defecto

@controller.periodic_execution(interval=5, priority="alta", enable_api=True)
def task_primary():
    print("Tarea principal ejecutándose...")

@controller.periodic_execution(interval=10, priority="media", dependent_task="task_primary")
def task_dependent():
    print("Tarea dependiente ejecutándose tras la tarea principal...")

task_primary()
task_dependent()

controller.start_api()
