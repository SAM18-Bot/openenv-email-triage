from __future__ import annotations

import random
import uuid
from typing import Dict, List

import numpy as np


CATEGORY_CONFIG = {
    "support": {
        "urgency": (0.5, 1.0),
        "senders": ["customer@acme.com", "support-ticket@client.io", "user@startup.dev"],
        "subjects": [
            "Cannot log in to dashboard",
            "500 error on checkout",
            "Data export missing records",
            "Account locked after password reset",
            "API integration failed in production",
        ],
    },
    "billing": {
        "urgency": (0.4, 0.9),
        "senders": ["accounts@client.io", "billing@enterprise.org", "finance@customer.co"],
        "subjects": [
            "Invoice dispute for March",
            "Refund request for duplicate charge",
            "Payment failed for subscription renewal",
            "Need updated PO for enterprise plan",
            "Chargeback notice received",
        ],
    },
    "internal": {
        "urgency": (0.0, 0.5),
        "senders": ["manager@company.com", "teammate@company.com", "hr@company.com"],
        "subjects": [
            "Weekly planning update",
            "Meeting invite: roadmap sync",
            "Can you review this draft?",
            "Quarterly OKR progress",
            "Team offsite logistics",
        ],
    },
    "spam": {
        "urgency": (0.0, 0.1),
        "senders": ["promo@offers.biz", "newsletter@deals.net", "noreply@growthhackers.ai"],
        "subjects": [
            "You won a gift card",
            "Limited-time promo just for you",
            "Increase leads by 10x",
            "SEO package discount",
            "Unbeatable newsletter bundle",
        ],
    },
    "urgent_alert": {
        "urgency": (0.8, 1.0),
        "senders": ["alerts@monitoring.io", "pager@infra.net", "security@company.com"],
        "subjects": [
            "Production outage detected",
            "SLA breach in EU region",
            "Critical security alert",
            "Database replication lag critical",
            "Latency spike above threshold",
        ],
    },
    "vendor": {
        "urgency": (0.2, 0.6),
        "senders": ["sales@vendor.com", "renewals@saas.io", "legal@partner.org"],
        "subjects": [
            "Contract renewal reminder",
            "Updated pricing proposal",
            "New terms for data processing",
            "Q2 roadmap from vendor",
            "Implementation support availability",
        ],
    },
}

BODY_SNIPPETS = [
    "Please help as soon as possible.",
    "This impacts multiple users.",
    "Could you confirm next steps?",
    "We need an update by EOD.",
    "Attaching logs and screenshots.",
]


class EmailGenerator:
    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._np_rng = np.random.default_rng(seed)
        self.templates = self._build_templates()

    def _build_templates(self) -> List[Dict[str, str]]:
        templates: List[Dict[str, str]] = []
        for category, cfg in CATEGORY_CONFIG.items():
            for sender in cfg["senders"]:
                for subject in cfg["subjects"]:
                    for body in BODY_SNIPPETS:
                        templates.append(
                            {
                                "category": category,
                                "sender": sender,
                                "subject": subject,
                                "body": f"{subject}. {body}",
                            }
                        )
        return templates

    def sample_email(self) -> Dict[str, str | float]:
        template = self._rng.choice(self.templates)
        urgency_min, urgency_max = CATEGORY_CONFIG[template["category"]]["urgency"]
        urgency = float(self._np_rng.uniform(urgency_min, urgency_max))
        return {
            "email_id": str(uuid.uuid4()),
            "sender": template["sender"],
            "subject": template["subject"],
            "body": template["body"][:512],
            "urgency": round(urgency, 3),
            "category": template["category"],
        }

    def poisson_new_emails(self, lam: float = 1.3, cap: int = 3) -> List[Dict[str, str | float]]:
        count = int(min(self._np_rng.poisson(lam=lam), cap))
        return [self.sample_email() for _ in range(count)]
