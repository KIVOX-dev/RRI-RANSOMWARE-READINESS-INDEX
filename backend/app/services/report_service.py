"""D3 — Report Generator. Jinja2 -> HTML -> WeasyPrint -> PDF, stored in
MinIO, with a ledger entry referencing the report's checksum."""
import hashlib
from pathlib import Path

from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader

from app.core.storage import ensure_buckets, presigned_get_url, put_object
from app.repositories.base import now_utc
from app.repositories.collections import (
    answers_repo,
    assessments_repo,
    backup_resilience_repo,
    evidence_repo,
    log_sources_repo,
    organisations_repo,
    probe_checks_repo,
    probe_runs_repo,
    questions_repo,
    remediation_items_repo,
    reports_repo,
)
from app.services import charts_service, cis_cdm_service, detection_service, ledger_service, regulatory_compliance_service, regulatory_service, remediation_service

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def _build_control_rows(assessment_id: str) -> list[dict]:
    answers = answers_repo.find({"assessment_id": assessment_id})
    questions = {q["control_id"]: q for q in questions_repo.find({})}
    evidence_by_control: dict[str, list[dict]] = {}
    for ev in evidence_repo.find({"assessment_id": assessment_id}):
        evidence_by_control.setdefault(ev["control_id"], []).append(ev)

    probe_checks_by_control: dict[str, dict] = {}
    latest_runs = probe_runs_repo.find({"assessment_id": assessment_id, "verification_status": "verified"}, sort=[("created_at", -1)], limit=1)
    if latest_runs:
        checks = probe_checks_repo.find({"probe_run_id": latest_runs[0]["id"]})
        for c in checks:
            if c.get("control_id"):
                probe_checks_by_control[c["control_id"]] = c

    rows = []
    for answer in answers:
        question = questions.get(answer["control_id"], {})
        domain = question.get("domain", "")
        evidence_status = "verified" if any(e["verification_status"] == "verified" for e in evidence_by_control.get(answer["control_id"], [])) else (
            "submitted" if evidence_by_control.get(answer["control_id"]) else "none"
        )
        probe_check = probe_checks_by_control.get(answer["control_id"])
        probe_status = probe_check["result"] if probe_check else "not_probed"
        rows.append(
            {
                "control_id": answer["control_id"],
                "domain": domain,
                "answer": str(answer.get("answer")),
                "score": answer.get("score"),
                "impact_level": answer.get("impact_level"),
                "evidence_status": evidence_status,
                "probe_status": probe_status,
            }
        )
    return rows


def _next_version(assessment_id: str, report_type: str) -> int:
    existing = reports_repo.find({"assessment_id": assessment_id, "report_type": report_type})
    return len(existing) + 1


def generate_report(assessment_id: str, report_type: str = "executive") -> dict:
    assessment = assessments_repo.get_by_id(assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    if assessment["status"] != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assessment must be completed before generating a report")

    organisation = organisations_repo.get_by_id(assessment["organisation_id"])
    remediation_items = remediation_service.generate_remediation_items(assessment_id)
    detection_matrix = [d.model_dump(mode="json") for d in detection_service.compute_detection_matrix(assessment_id)]
    version = _next_version(assessment_id, report_type)

    if report_type == "executive":
        html_str = jinja_env.get_template("executive_report.html").render(
            organisation=organisation,
            assessment=assessment,
            is_synthetic=organisation.get("is_synthetic", False),
            version=version,
            domain_scores=assessment.get("domain_scores", []),
            high_impact_gaps=assessment.get("high_impact_gaps", []),
            top_remediation=remediation_items[:8],
            detection_matrix=detection_matrix,
            radar_chart=charts_service.radar_chart(assessment.get("domain_scores", [])),
            gauge_chart=charts_service.assurance_gauge(assessment.get("assurance_score", 0)),
            quadrant_chart=charts_service.impact_effort_quadrant(remediation_items),
            regulatory_summary=regulatory_service.get_regulatory_summary(),
            regulatory_disclaimer=regulatory_service.DISCLAIMER,
            regulatory_compliance=[
                {**f.model_dump(), "met_count": sum(1 for r in f.requirements if r.met)}
                for f in regulatory_compliance_service.compute_compliance(assessment["organisation_id"], assessment_id).frameworks
            ],
            cis_cdm_headline=cis_cdm_service.get_full_reference()["headline"],
            generated_at=str(now_utc()),
            ledger_reference="generated after report is stored",
        )
    elif report_type == "technical":
        latest_runs = probe_runs_repo.find({"assessment_id": assessment_id}, sort=[("created_at", -1)])
        probe_run_rows = []
        for run in latest_runs:
            checks = probe_checks_repo.find({"probe_run_id": run["id"]})
            probe_run_rows.append(
                {**run, "pass_count": sum(1 for c in checks if c["result"] == "pass"), "total_count": len(checks)}
            )
        html_str = jinja_env.get_template("technical_annexure.html").render(
            organisation=organisation,
            assessment=assessment,
            version=version,
            control_rows=_build_control_rows(assessment_id),
            probe_runs=probe_run_rows,
            detection_matrix=detection_matrix,
            log_sources=log_sources_repo.find({"assessment_id": assessment_id}),
            backup=backup_resilience_repo.find_one({"assessment_id": assessment_id}),
            remediation_items=remediation_items,
        )
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown report_type")

    try:
        from weasyprint import HTML
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "PDF rendering is unavailable: WeasyPrint's native libraries (Pango/Cairo/GDK-Pixbuf) are not "
                "installed on this host. This works out of the box inside the project's Docker image."
            ),
        ) from exc

    pdf_bytes = HTML(string=html_str, base_url=str(TEMPLATE_DIR)).write_pdf()
    checksum = hashlib.sha256(pdf_bytes).hexdigest()

    ensure_buckets()
    from app.core.config import get_settings

    settings = get_settings()
    object_key = f"{assessment['organisation_id']}/{assessment_id}/{report_type}_v{version}.pdf"
    put_object(settings.minio_bucket_reports, object_key, pdf_bytes, "application/pdf")

    report_id = reports_repo.insert(
        {
            "assessment_id": assessment_id,
            "organisation_id": assessment["organisation_id"],
            "report_type": report_type,
            "version": version,
            "object_key": object_key,
            "checksum": checksum,
            "generated_at": now_utc(),
            "status": "generated",
        }
    )

    ledger_service.create_ledger_entry(
        assessment["organisation_id"],
        {"report_id": report_id, "assessment_id": assessment_id, "checksum": checksum, "report_type": report_type},
        assessment_id=assessment_id,
        report_id=report_id,
    )

    return get_report(report_id)


def get_report(report_id: str) -> dict:
    from app.core.config import get_settings

    settings = get_settings()
    report = reports_repo.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    report["download_url"] = presigned_get_url(settings.minio_bucket_reports, report["object_key"])
    return report


def list_reports(assessment_id: str) -> list[dict]:
    from app.core.config import get_settings

    settings = get_settings()
    reports = reports_repo.find({"assessment_id": assessment_id}, sort=[("generated_at", -1)])
    for r in reports:
        r["download_url"] = presigned_get_url(settings.minio_bucket_reports, r["object_key"])
    return reports
