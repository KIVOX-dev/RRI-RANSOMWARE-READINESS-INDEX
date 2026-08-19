from enum import Enum


class Sector(str, Enum):
    healthcare = "healthcare"
    education = "education"
    local_government = "local_government"
    finance = "finance"
    generic = "generic"


class RoleName(str, Enum):
    executive = "executive"
    it_administrator = "it_administrator"
    generalist = "generalist"


class UserRole(str, Enum):
    org_user = "org_user"
    org_admin = "org_admin"
    platform_admin = "platform_admin"


class Language(str, Enum):
    en = "en"
    hi = "hi"


class ImpactLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AnswerType(str, Enum):
    boolean = "boolean"
    scale = "scale"
    single_select = "single_select"
    multi_select = "multi_select"
    text = "text"


class AssessmentStatus(str, Enum):
    draft = "draft"
    in_progress = "in_progress"
    completed = "completed"


class AssessmentMode(str, Enum):
    """basic: a fixed ~24-control, plain-language, boolean-first subset aimed
    at non-technical users who want a fast readiness snapshot, not the full
    control catalogue. full: the complete sector/role-routed question set."""
    basic = "basic"
    full = "full"


class EvidenceStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class OrganisationVerificationStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class DetectionStatus(str, Enum):
    covered = "covered"
    partial = "partial"
    blind = "blind"


class KillChainStage(str, Enum):
    credential_access = "Credential Access"
    discovery = "Discovery"
    lateral_movement = "Lateral Movement"
    shadow_copy_deletion = "Shadow Copy Deletion"
    exfiltration = "Exfiltration"


class RemediationPriority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class EffortLevel(str, Enum):
    low = "low"
    high = "high"
