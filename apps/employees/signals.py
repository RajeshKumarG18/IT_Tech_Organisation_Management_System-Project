from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.employees.models import Employee

User = get_user_model()


@receiver(post_save, sender=Employee)
def employee_created(sender, instance, created, **kwargs):
    if created:
        if not instance.employee_id:
            last_emp = Employee.objects.order_by('-id').first()
            new_id = int(last_emp.employee_id[3:]) + 1 if last_emp and last_emp.employee_id else 1001
            instance.employee_id = f'EMP{new_id:04d}'
            instance.save(update_fields=['employee_id'])
        
        if instance.user and not instance.user.employee:
            instance.user.employee = instance
            instance.user.save(update_fields=['employee'])


@receiver(post_delete, sender=Employee)
def employee_deleted(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()