import unittest
from datetime import datetime, timezone
from shinhan_alert_parser import parse

R = datetime(2026, 11, 13, 4, 8, 57, tzinfo=timezone.utc)
B1308 = "[Web발신]<br/>신한11/13-13:08<br/>180*425426[USD]<br/>입금 0.01<br/>잔액 3,357.71<br/>장준혁"
B1306 = "[Web발신]<br/>신한11/13-13:06<br/>180*425426[USD]<br/>입금 0.01<br/>잔액 3,357.70<br/>장준혁"

class T(unittest.TestCase):
    def test_real_1308(self):
        s, r = parse(B1308, R)
        self.assertEqual(s, "ok")
        self.assertEqual(r["날짜"], "2026-11-13T13:08:00+09:00")
        self.assertEqual((r["방향"], r["금액"], r["잔액"]), ("입금", 0.01, 3357.71))
        self.assertNotIn("425426", str(r))
    def test_two_same_minute_amount_differ_by_balance(self):
        a = parse(B1308, R)[1]["원본ID"]
        b = parse(B1308.replace("3,357.71", "3,357.72"), R)[1]["원본ID"]
        self.assertNotEqual(a, b)
    def test_same_message_same_key(self):
        self.assertEqual(parse(B1306, R)[1]["원본ID"], parse(B1306, R)[1]["원본ID"])
    def test_empty_and_no_usd(self):
        self.assertEqual(parse("\r\n", R)[0], "skip")
        self.assertEqual(parse("테스트", R)[0], "skip")
    def test_withdraw_negative_and_comma(self):
        s, r = parse(B1308.replace("입금 0.01", "출금 1,200.50"), R)
        self.assertEqual(r["금액"], -1200.50)
    def test_year_boundary(self):
        jan = datetime(2027, 1, 1, 0, 5, tzinfo=timezone.utc)  # KST 09:05 1/1
        r = parse(B1308.replace("11/13-13:08", "12/31-23:59"), jan)[1]
        self.assertEqual(r["날짜"], "2026-12-31T23:59:00+09:00")
    def test_utc_vs_kst_receive_date(self):
        # UTC 12/31 15:30 = KST 1/1 00:30 수신, 거래 1/1 00:29 → 2027
        rec = datetime(2026, 12, 31, 15, 30, tzinfo=timezone.utc)
        r = parse(B1308.replace("11/13-13:08", "01/01-00:29"), rec)[1]
        self.assertTrue(r["날짜"].startswith("2027-01-01"))
    def test_unknown_format_held(self):
        self.assertEqual(parse("[Web발신] 신한11/13-13:08 180*425426[USD] 해외송금 0.01", R)[0], "hold")

unittest.main(verbosity=1)
