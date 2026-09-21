"""
VoiceShield-AI Risk Engine

Combines voice authenticity signals with transaction
and verification context to produce a security risk.
"""


def calculate_risk(
    ai_score: float,
    fake_chunk_percentage: float,
    transaction_sensitivity: str = "LOW",
    caller_verified: bool = False,
):
    """
    Calculate a prototype security risk score.

    Parameters
    ----------
    ai_score:
        Average synthetic/AI voice score from the detector (0-100).

    fake_chunk_percentage:
        Percentage of analyzed chunks classified as suspicious (0-100).

    transaction_sensitivity:
        LOW / MEDIUM / HIGH

    caller_verified:
        Whether the caller has passed an independent verification step.

    Returns
    -------
    dict
        Risk score, level and recommended security actions.
    """

    # --------------------------------------------------
    # 1. Normalize incoming values
    # --------------------------------------------------

    ai_score = max(0.0, min(float(ai_score), 100.0))
    fake_chunk_percentage = max(
        0.0,
        min(float(fake_chunk_percentage), 100.0)
    )

    transaction_sensitivity = (
        transaction_sensitivity or "LOW"
    ).upper()

    # --------------------------------------------------
    # 2. Voice authenticity component
    # --------------------------------------------------

    # AI detector score carries the largest weight.
    #
    # Chunk consistency provides a second signal.
    #
    # This is a prototype rule-based risk engine,
    # not a statistically calibrated probability.

    voice_risk = (
        0.70 * ai_score
        + 0.30 * fake_chunk_percentage
    )

    # --------------------------------------------------
    # 3. Transaction sensitivity
    # --------------------------------------------------

    transaction_risk = {
        "LOW": 0.0,
        "MEDIUM": 10.0,
        "HIGH": 20.0,
    }.get(transaction_sensitivity, 0.0)

    # --------------------------------------------------
    # 4. Independent caller verification
    # --------------------------------------------------

    verification_adjustment = 0.0

    if caller_verified:
        verification_adjustment = -20.0

    # --------------------------------------------------
    # 5. Final risk score
    # --------------------------------------------------

    risk_score = (
        voice_risk
        + transaction_risk
        + verification_adjustment
    )

    risk_score = max(
        0.0,
        min(risk_score, 100.0)
    )

    # --------------------------------------------------
    # 6. Risk classification
    # --------------------------------------------------

    if risk_score >= 75:
        risk_level = "HIGH"

    elif risk_score >= 45:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    # --------------------------------------------------
    # 7. Security recommendation
    # --------------------------------------------------

    if risk_level == "HIGH":

        recommended_action = "BLOCK_AND_VERIFY"

        security_actions = [
            "HOLD_TRANSACTION",
            "VERIFY_CALLER",
            "REQUEST_MFA",
            "SECURITY_REVIEW",
        ]

    elif risk_level == "MEDIUM":

        recommended_action = "VERIFY_CALLER"

        security_actions = [
            "VERIFY_CALLER",
            "REQUEST_MFA",
        ]

    else:

        recommended_action = "ALLOW_WITH_MONITORING"

        security_actions = [
            "CONTINUE_MONITORING",
        ]

    # --------------------------------------------------
    # 8. Return structured result
    # --------------------------------------------------

    return {
        "risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "recommended_action": recommended_action,
        "security_actions": security_actions,
    }