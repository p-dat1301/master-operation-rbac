class DomainError(Exception):
    pass

class PermissionDenied(DomainError):
    pass

class ScopeViolation(DomainError):
    pass

class ResourceNotFound(DomainError):
    pass

class BusinessRuleViolation(DomainError):
    pass