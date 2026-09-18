"""Built-in SRE Production Readiness Review (PRR) rubric.

Sourced from this org's G-CAF-092 (Go-Live Gateway) exit criteria and
G-CAF-073 (NFR Contract) mandatory checks, so a change team can run an
assessment without first authoring a standards doc. Teams with their own
SRE readiness checklist should instead run `prr-readiness normalize-criteria`
against it and pass the resulting rubric to `assess --rubric`.
"""
from __future__ import annotations

from arch_compliance.rubric import RubricItem

DEFAULT_RUBRIC: list[RubricItem] = [
    # Implementation compliance
    RubricItem("IMP-1", "Deployed implementation matches the approved design from the Design Gateway", "implementation", True, 4),
    RubricItem("IMP-2", "Deployed technology stack matches approved specs; no Containment/Retired tech in production without an ARB exception", "implementation", True, 4),
    # Security
    RubricItem("SEC-1", "Penetration test / vulnerability assessment completed and passed", "security", True, 5),
    RubricItem("SEC-2", "Zero Trust and other required security controls validated", "security", True, 5),
    RubricItem("SEC-3", "Encryption at rest and in transit verified; authentication/authorization functional; audit logging operational", "security", True, 5),
    RubricItem("SEC-4", "SAST, DAST, dependency scanning, container scanning, and runtime protection tools integrated and operational", "security", True, 4),
    # NFR / SLO validation
    RubricItem("NFR-1", "Availability target for the service's criticality tier is validated (e.g. 99.95%/99.9%/99.5%/99.0%)", "reliability", True, 5),
    RubricItem("NFR-2", "Performance targets validated (interactive APIs <500ms p95, real-time <100ms, batch per PBC)", "reliability", True, 4),
    RubricItem("NFR-3", "Scalability validated for the service's criticality tier (auto-scaling verified or capacity plan documented)", "reliability", True, 4),
    RubricItem("NFR-4", "Recovery tested against RTO/RPO targets for the criticality tier", "reliability", True, 5),
    RubricItem("NFR-5", "Error budget and SLO burn-rate status reviewed; no active release freeze from budget exhaustion", "reliability", True, 5),
    # Monitoring / observability / alerting
    RubricItem("MON-1", "Monitoring and observability tooling operational for the service", "observability", True, 5),
    RubricItem("MON-2", "SLA/SLO-based alerting configured and routed to the owning team", "observability", True, 5),
    RubricItem("MON-3", "Structured logging with correlation IDs and distributed tracing operational", "observability", True, 3),
    RubricItem("MON-4", "Dashboards published for key SLIs (latency, errors, saturation, traffic)", "observability", False, 2),
    # Support model / on-call / runbooks
    RubricItem("SUP-1", "Support RACI documented and agreed, with clear L1/L2/L3 responsibilities", "operations", True, 4),
    RubricItem("SUP-2", "Runbooks published AND tested (not just written) for known failure modes", "operations", True, 5),
    RubricItem("SUP-3", "Escalation procedures defined", "operations", True, 3),
    RubricItem("SUP-4", "On-call rotation established for the service", "operations", True, 4),
    RubricItem("SUP-5", "Knowledge transfer completed where a vendor provides L3 support", "operations", False, 2),
    # Rollout / rollback
    RubricItem("ROL-1", "Staged or canary rollout plan defined with automated health checks against SLIs", "rollout", True, 4),
    RubricItem("ROL-2", "Automated rollback mechanism defined and tested", "rollout", True, 5),
    # Dependencies / integration
    RubricItem("DEP-1", "GovDX APIs (or equivalent internal APIs) registered and discoverable/functional", "dependencies", True, 3),
    RubricItem("DEP-2", "Event schemas registered in the schema registry", "dependencies", True, 3),
    RubricItem("DEP-3", "Anti-corruption layer (ACL) operational and consumer-driven contract tests passing, where applicable (Buy/Outsource PBCs)", "dependencies", False, 3),
    # Testing artifacts
    RubricItem("TST-1", "Performance test report available as an artifact", "testing", True, 3),
    RubricItem("TST-2", "Availability/chaos test report available as an artifact", "testing", True, 3),
    RubricItem("TST-3", "DR/BC test results available as an artifact", "testing", True, 3),
    # Cost / SLA / vendor
    RubricItem("SLA-1", "External/internal SLA targets defined, measurable, and dashboarded", "commercial", False, 2),
    RubricItem("SLA-2", "Cost allocation model approved for the service", "commercial", False, 2),
    RubricItem("SLA-3", "Vendor onboarding checklist complete and contract SLA alignment confirmed, where applicable", "commercial", False, 2),
    # Documentation
    RubricItem("DOC-1", "Deployment documentation, technology/version compliance confirmation, and security validation report published", "documentation", True, 3),
]
