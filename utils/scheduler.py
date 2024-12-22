from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.start()
    return scheduler

def schedule_daily_task(scheduler, func, hour=3, minute=0, id=None):
    """
    Programa una tarea para que se ejecute diariamente a una hora específica.
    :param scheduler: Instancia de BackgroundScheduler.
    :param func: Función a ejecutar.
    :param hour: Hora del día en formato 24 horas.
    :param minute: Minuto de la hora.
    :param id: Identificador único para la tarea.
    """
    trigger = CronTrigger(hour=hour, minute=minute)
    scheduler.add_job(func, trigger, id=id, replace_existing=True)
