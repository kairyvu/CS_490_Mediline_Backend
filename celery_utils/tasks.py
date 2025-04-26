from celery import shared_task

@shared_task
def my_task(m1: str, m2: str):
    print(f'm1 is {m1}')
    print(f'm2 is {m2}')
    return ' '.join([m1, m2])