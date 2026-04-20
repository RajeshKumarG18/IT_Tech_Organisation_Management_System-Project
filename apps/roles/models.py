from django.db import models


class Role(models.Model):
    LEVEL_CHOICES = [
        ('EXECUTIVE', 'Executive Leadership'),
        ('UPPER_MANAGEMENT', 'Upper Management'),
        ('MIDDLE_MANAGEMENT', 'Middle Management'),
        ('SENIOR_PROFESSIONAL', 'Senior Professional'),
        ('JUNIOR_PROFESSIONAL', 'Junior Professional'),
        ('SUPPORT', 'Support Function'),
    ]

    title = models.CharField(max_length=100)
    level = models.CharField(max_length=30, choices=LEVEL_CHOICES)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, related_name='roles')
    description = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['title', 'department']
        ordering = ['level', 'title']

    def __str__(self):
        return f"{self.title} - {self.department.name}"

    @property
    def employee_count(self):
        return self.employees.count()