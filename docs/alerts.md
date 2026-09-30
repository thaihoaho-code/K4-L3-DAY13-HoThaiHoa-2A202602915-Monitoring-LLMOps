# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Primary SLO `latency_ms <= 3000`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` duy trì trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng phải chờ quá 3 giây để nhận câu trả lời, gây trải nghiệm chậm chạp.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra dashboard Latency để xác nhận P95 có thực sự tăng không, hay chỉ là do một vài request cá biệt.
  2. Lọc `data/logs.jsonl` tìm các request có `latency_ms > 3000` và lấy `correlation_id`.
  3. Mở Langfuse trace bằng `correlation_id` đó, kiểm tra xem độ trễ nằm ở span `retrieve` (rag_slow) hay `generate` (LLM chậm).
- Mitigation tạm thời: Nếu do RAG chậm, scale up vector DB hoặc bật bộ nhớ đệm (cache). Nếu do LLM, cân nhắc đổi model fallback hoặc liên hệ provider.
- Owner: `student-2A202602915`

## Alert 2

- Tên: `HighErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Guardrail `error_rate_pct_max: 2`
- Điều kiện và thời gian duy trì: Tỷ lệ lỗi `error_rate_pct > 2%` duy trì trong 5 phút
- Ảnh hưởng tới người dùng: Người dùng nhận được phản hồi HTTP 500 hoặc thông báo lỗi, không thể sử dụng chatbot.
- Ba bước kiểm tra đầu tiên:
  1. Xem dashboard Errors để xác định `error_type` phổ biến (VD: `RuntimeError`).
  2. Mở file log để lấy stack trace của `request_failed` tương ứng thông qua `error_type`.
  3. Lấy `correlation_id` và vào Langfuse kiểm tra xem lỗi ném ra từ tool/span nào (VD: `retrieve` bị timeout).
- Mitigation tạm thời: Rollback code nếu vừa có đợt deploy. Tắt tính năng đang lỗi hoặc kích hoạt fallback mode để bot trả lời không cần context.
- Owner: `student-2A202602915`

## Alert 3

- Tên: `CostSpikeDetected`
- Severity: `warning`
- Duration: `1h`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: Guardrail `daily_cost_usd_max: 2.5`
- Điều kiện và thời gian duy trì: Tổng chi phí `sum(cost_usd) > 2.5$` trong vòng 1 giờ
- Ảnh hưởng tới người dùng: Không ảnh hưởng trực tiếp tới người dùng, nhưng gây rủi ro tài chính cho doanh nghiệp vì chi phí LLM vượt ngân sách.
- Ba bước kiểm tra đầu tiên:
  1. Kiểm tra dashboard Cost và Tokens xem chi phí tăng do số lượng request (traffic) tăng hay do số token/request tăng.
  2. Lọc log để tìm các request có `tokens_out` cao bất thường và lấy `correlation_id`.
  3. Tra cứu `correlation_id` trên Langfuse để xem prompt nào đang gây ra generation quá dài.
- Mitigation tạm thời: Cập nhật prompt (ví dụ đổi version về v1) ép LLM trả lời ngắn gọn hơn. Áp dụng giới hạn `max_tokens` trên API LLM.
- Owner: `student-2A202602915`
