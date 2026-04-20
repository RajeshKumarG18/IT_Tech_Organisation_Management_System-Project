from apps.employees.models import OrganizationSettings


def organization_settings(request):
    """Add organization settings to all templates"""
    settings = OrganizationSettings.get_settings()
    return {
        'org_settings': settings,
        'organization_name': settings.organization_name,
        'organization_short_name': settings.organization_short_name,
    }
