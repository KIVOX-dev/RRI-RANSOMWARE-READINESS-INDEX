from app.repositories.base import Repository


class UsersRepo(Repository):
    collection_name = "users"


class OrganisationsRepo(Repository):
    collection_name = "organisations"


class SectorsRepo(Repository):
    collection_name = "sectors"


class RolesRepo(Repository):
    collection_name = "roles"


class QuestionsRepo(Repository):
    collection_name = "questions"


class AssessmentsRepo(Repository):
    collection_name = "assessments"


class AnswersRepo(Repository):
    collection_name = "answers"


class EvidenceRepo(Repository):
    collection_name = "evidence"


class ProbeRunsRepo(Repository):
    collection_name = "probe_runs"


class ProbeChecksRepo(Repository):
    collection_name = "probe_checks"


class ScoringConfigsRepo(Repository):
    collection_name = "scoring_configs"


class DetectionCoverageRepo(Repository):
    collection_name = "detection_coverage"


class LogSourcesRepo(Repository):
    collection_name = "log_sources"


class CanaryEventsRepo(Repository):
    collection_name = "canary_events"


class RemediationItemsRepo(Repository):
    collection_name = "remediation_items"


class AwarenessResultsRepo(Repository):
    collection_name = "awareness_results"


class ReportsRepo(Repository):
    collection_name = "reports"


class LedgerEntriesRepo(Repository):
    collection_name = "ledger_entries"


class AuditLogsRepo(Repository):
    collection_name = "audit_logs"


class BackupResilienceRepo(Repository):
    collection_name = "backup_resilience"


users_repo = UsersRepo()
organisations_repo = OrganisationsRepo()
sectors_repo = SectorsRepo()
roles_repo = RolesRepo()
questions_repo = QuestionsRepo()
assessments_repo = AssessmentsRepo()
answers_repo = AnswersRepo()
evidence_repo = EvidenceRepo()
probe_runs_repo = ProbeRunsRepo()
probe_checks_repo = ProbeChecksRepo()
scoring_configs_repo = ScoringConfigsRepo()
detection_coverage_repo = DetectionCoverageRepo()
log_sources_repo = LogSourcesRepo()
canary_events_repo = CanaryEventsRepo()
remediation_items_repo = RemediationItemsRepo()
awareness_results_repo = AwarenessResultsRepo()
reports_repo = ReportsRepo()
ledger_entries_repo = LedgerEntriesRepo()
audit_logs_repo = AuditLogsRepo()
backup_resilience_repo = BackupResilienceRepo()
