import type { LogSource } from "@/types";

// Starting point shown before an assessment has ever saved its own log
// sources — shared by the Log Gaps page (full editable form) and the
// Detection Matrix page (quick-toggle buttons) so both start from the same
// baseline and don't drift into inconsistent source sets.
export const DEFAULT_LOG_SOURCES: LogSource[] = [
  { source_name: "Endpoint/EDR telemetry", enabled: false, retention_days: 0, monitored: false, covered_stages: ["Discovery", "Shadow Copy Deletion"] },
  { source_name: "Authentication logs", enabled: false, retention_days: 0, monitored: false, covered_stages: ["Credential Access"] },
  { source_name: "Network flow logs", enabled: false, retention_days: 0, monitored: false, covered_stages: ["Lateral Movement", "Exfiltration"] },
  { source_name: "Firewall logs", enabled: false, retention_days: 0, monitored: false, covered_stages: ["Exfiltration"] },
  { source_name: "DNS logs", enabled: false, retention_days: 0, monitored: false, covered_stages: ["Exfiltration"] },
  { source_name: "Backup system logs", enabled: false, retention_days: 0, monitored: false, covered_stages: ["Shadow Copy Deletion"] },
];
