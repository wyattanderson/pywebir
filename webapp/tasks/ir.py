from webapp.tasks import celery

@celery.task
def send_ir_command(irdata):
    print 'what'
    return
