from .models import Account, Positions, Transaction

def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
				# return classmodel.objects.filter(**kwargs).first()
    except classmodel.DoesNotExist:
        return None
