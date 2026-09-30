from app.pii import hash_user_id, scrub_text, summarize_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_cccd() -> None:
    out = scrub_text("CCCD: 012345678901")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card() -> None:
    cards = (
        "4111111111111111",
        "4111-1111-1111-1111",
        "4111 1111 1111 1111",
    )
    for card in cards:
        out = scrub_text(f"Card: {card}")
        assert card not in out
        assert "REDACTED_CREDIT_CARD" in out


def test_scrub_passport() -> None:
    out = scrub_text("Passport: B1234567")
    assert "B1234567" not in out
    assert "REDACTED_PASSPORT" in out


def test_scrub_cmt() -> None:
    out = scrub_text("CMT: 123456789")
    assert "123456789" not in out
    assert "REDACTED_CMT" in out


def test_scrub_multiple_pii_in_one_text() -> None:
    text = "User student@test.com called from 0901234567 with CCCD 012345678901"
    out = scrub_text(text)
    assert "student@test.com" not in out
    assert "0901234567" not in out
    assert "012345678901" not in out
    assert "REDACTED_EMAIL" in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_CCCD" in out


def test_scrub_no_pii() -> None:
    text = "This is a normal message with no PII"
    assert scrub_text(text) == text


def test_summarize_text_truncates() -> None:
    long_text = "a" * 200
    out = summarize_text(long_text, max_len=80)
    assert len(out) == 83  # 80 + "..."
    assert out.endswith("...")


def test_summarize_text_scrubs_pii() -> None:
    out = summarize_text("Contact student@vinuni.edu.vn for details")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_hash_user_id_deterministic() -> None:
    h1 = hash_user_id("u_student_01")
    h2 = hash_user_id("u_student_01")
    assert h1 == h2
    assert len(h1) == 12


def test_hash_user_id_different_for_different_users() -> None:
    h1 = hash_user_id("u_student_01")
    h2 = hash_user_id("u_student_02")
    assert h1 != h2
