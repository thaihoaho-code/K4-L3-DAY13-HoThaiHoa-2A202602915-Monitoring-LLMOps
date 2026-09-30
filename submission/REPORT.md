# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

> Mỗi học viên hoàn thiện một file duy nhất này. Khi dẫn evidence, dùng đường dẫn tương đối, ví dụ `evidence/07-trace-waterfall.png`.

## 1. Thông tin học viên

- **Họ và tên:** Hồ Thái Hòa
- **MSSV:** 2A202602915
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/thaihoaho-code/K4-L3-DAY13-HoThaiHoa-2A202602915-Monitoring-LLMOps
- **Commit SHA cuối:** a2735cd47bf555dfbd9eaf7127f40da5a7a33028
- **Challenge ID:** `rag_slow`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602915` 
- (các screenshot em quên đổi tên project, nhưng có thể hiện rõ tên "Hồ Thái Hòa" và gmail cá nhân phía dưới góc trái màn hình)

## 2. Evidence index

Điền đúng đường dẫn tới evidence thực tế. Có thể đổi tên hoặc dùng nhiều ảnh nếu cần.

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | `evidence/01-pytest.png` |
| Log validator | `evidence/02-log-validator.png` |
| Dashboard validator | `evidence/03-dashboard-validator.png` |
| Structured log | `evidence/04-structured-log.png` |
| PII redaction | `evidence/05-pii-redaction.png` |
| Trace list | `evidence/06-trace-list.png` |
| Trace waterfall | `evidence/07-trace-waterfall.png` |
| Trace metadata | `evidence/08-trace-metadata.png` |
| Prompt versions | `evidence/09-prompt-versions.png` |
| Prompt rollback | `evidence/10-prompt-rollback.png` |
| Dashboard runtime | `evidence/11-dashboard-overview.png` |
| Incident metric | `evidence/12-incident-metric.png` |
| Incident log | `evidence/13-incident-log.png` |
| Incident trace | `evidence/14-incident-trace.png` |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | 30/100 | 100/100 | Đã sửa cấu trúc JSON, gỡ bỏ log rác, scrub PII chuẩn xác. |
| `validate_dashboard.py` | 6/6 | 6/6 | Hoàn thiện 6 panel UI bằng Chart.js |
| `pytest` | 22 passed | 22 passed | Pass toàn bộ unit test sau khi tái cấu trúc. |
| Số traces hợp lệ | 0 | >10 | Tích hợp thành công OpenTelemetry via Langfuse `@observe`. |
| Số PII leak | 0 | 0 | Chạy mask regex thành công. |
| Latency P95 / TTFT P95 | 1428 ms / 50 ms | ~200 ms / 50 ms | Tối ưu logic giảm đáng kể độ trễ. |
| Retrieval success rate | 100% (10/10) | 100% | RAG chạy mượt. |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** Sử dụng `CorrelationIdMiddleware` tự động sinh UUID. ID này được bind vào `structlog` để đi theo toàn bộ vòng đời log.
- **Các metadata được ghi vào structured log:** `user_id_hash`, `session_id`, `feature`, `model`, `env`, `correlation_id`, `latency_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`.
- **Cách bảo đảm PII được scrub trước khi ghi:** Xây dựng hàm `summarize_text` sử dụng regex mask các chuỗi nhạy cảm (email, credit card, phone).
- **Cách kiểm chứng kết quả:** Chạy script `validate_logs.py` lấy kết quả 100/100, kết hợp rà soát bằng mắt file `logs.jsonl`.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** `correlation_id` trong Terminal/Logs ở máy local khớp 100% với Trace ID trên Langfuse; Tên project trên Langfuse ban đầu quên sửa "My Project", có thể check bằng tên "Hồ Thái Hòa" bên góc dưới bên trái screenshot;
- **Cấu trúc root/retrieval/generation observations:** Trace gốc được Langfuse tự tạo ẩn, bên dưới chứa 2 child-span: `retrieve` (Vector Search, định nghĩa bằng `@observe(as_type="span")`) và `generate` (LLM Call, định nghĩa bằng `@observe(as_type="generation")`).
- **Cách nối trace với log:** Sinh `correlation_id` ở Middleware, truyền nó vào `structlog` để in ra file, đồng thời truyền nó cho Langfuse client để 2 hệ thống dùng chung 1 ID.
- **Prompt name:** `day13-chat`
- **Version/label baseline:** Version 1 (label: `production`)
- **Version/label candidate:** Version 2 (label: `candidate`)
- **Trace ID của mỗi version:** Trace `0857a65bd469b3210ebd9bf948e21765` (Version 1, correlation: req-7f94429c) và Trace `48e3924e9aff4cab0693584c19e882e0` (Version 2, correlation: req-ad719731).
- **Cách promote và rollback `production`:** Lên UI Langfuse -> Prompts -> Chọn version muốn rollback -> Edit Labels -> Gỡ nhãn `production` ở bản lỗi và gán lại `production` cho bản ổn định.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** Code file `dashboard.html` sử dụng Chart.js. Có cơ chế Auto-refresh Live 5 giây/lần. Đầy đủ 6 panel: Latency, Traffic, Error Rate, Cost, Tokens In/Out, Quality.
- **SLO và lý do chọn:** SLO 99% cho "Fast Successful Requests" (Latency < 3s & No Error). Lý do: AI Chatbot phản hồi trên 3s sẽ làm người dùng khó chịu, mức 99% là đủ chặt chẽ.
- **Cách tính error budget:** SLO 99% => Error Budget 1%. Nếu có 20,000 request/tháng, ta có quỹ 200 request lỗi/chậm. Nếu cạn quỹ, ngưng feature mới, tập trung fix bugs.
- **Ba alert và runbook tương ứng:**
  1. HighLatencyP99: Alert khi P99 > 3000ms. Runbook: Lên Langfuse tìm Trace ID -> kiểm tra node RAG hay LLM.
  2. ErrorRateSpike: Alert khi Error > 2%. Runbook: Lọc log file bằng request_failed để lấy stacktrace.
  3. CostSpike: Alert khi Cost > 2.5$. Runbook: Soi token_out, nếu xả rác thì Rollback Prompt.

> Ví dụ cách viết error budget: "SLO 99.5% trong 28 ngày nghĩa là error budget 0.5%. Nếu workload có 10,000 request thì tối đa 50 request được phép lỗi hoặc chậm hơn ngưỡng SLO."

## 7. Điều tra challenge

- **Challenge ID:** `rag_slow`
- **Khoảng thời gian điều tra:** Khoảng 13:18:40 (06:18:40 UTC)
- **Triệu chứng từ metrics:** Dashboard Panel 1 (Latency) hiển thị đỉnh spike P99 vọt lên mức ~2,700ms (so với baseline chỉ khoảng 150-200ms).
- **Log line và correlation ID liên quan:** Bắt được log có latency 2655ms: `{"service": "api", "latency_ms": 2655, "correlation_id": "req-c8c4b66f", ...}`
- **Trace ID và span gây ảnh hưởng:** Trace `req-c8c4b66f` trên Langfuse cho thấy Span `retrieve` kéo dài bất thường (>2.5s).
- **Root cause:** Khâu truy xuất Vector Database (RAG) bị chậm, gây thắt cổ chai làm treo toàn bộ request phía sau.
- **Fix action:** Scale up resource cho DB, hoặc rollback bản cập nhật DB gây lỗi.
- **Preventive measure:** Set timeout cứng (max 500ms) cho hàm `retrieve()`, nếu lố thì Fallback (Fail-fast) về cache thay vì treo toàn bộ hệ thống.

> Gợi ý cách viết ngắn, không thay cho evidence thực tế: "Metric cho thấy `[latency/error/cost/quality]` bất thường trong `[khoảng thời gian]`. Log line `[event]` có `correlation_id=[...]` đại diện cho request bị ảnh hưởng. Trace cùng `correlation_id` cho thấy span `[retrieval/generation/prompt/tool]` có dấu hiệu `[chậm/lỗi/token tăng]`. Root cause là `[nguyên nhân suy ra từ evidence]`. Fix action là `[hành động khôi phục]`; preventive measure là `[alert/runbook/test/guardrail để ngăn tái diễn]`."

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** Quyết định sử dụng Chart.js thuần thay vì thư viện Python để render Dashboard. Lý do: Frontend JS hỗ trợ fetch live update 5 giây/lần mượt mà không cần tải lại trang.
- **Một lỗi/blocker đã gặp:** Gặp lỗi Read Timeout và Deadlock Event Loop khi tích hợp Langfuse SDK v4 vào FastAPI.
- **Cách tìm nguyên nhân và xử lý:** Phát hiện do Langfuse dùng thư viện `httpx` đồng bộ. Cách xử lý: Đổi endpoint từ `async def chat` sang `def chat` để FastAPI đẩy tiến trình vào threadpool riêng, giải phóng main loop.
- **Cách hiểu luồng Metrics -> Logs -> Traces:** Metrics báo hiệu (đỉnh nhọn), Logs định vị request (cấp correlation_id), Traces dùng ID đó để mổ xẻ nội tạng request.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** Prompt versioning cho phép quản lý chặt chẽ nội dung LLM. Khi có sự cố xả rác tốn Cost, tính năng Rollback giúp khôi phục lập tức về version ổn định, bảo vệ Error Budget không bị thủng.
- **Điều quan trọng nhất đã học:** Tư duy Observability 3 chiều (Metrics-Logs-Traces) đồng bộ qua Correlation ID, và nguyên tắc bảo mật dữ liệu PII trước khi log.
- **Hạn chế hoặc phần chưa hoàn thành, nếu có:** Đã hoàn thành 100% các tiêu chí thực hành.

## 9. Checklist trước khi nộp

- [x] Kết quả và evidence thuộc commit SHA cuối.
- [x] Tất cả ảnh/output mở được bằng đường dẫn tương đối.
- [x] Incident evidence nối đúng metric -> log -> trace.
- [x] Trace/prompt evidence thuộc project Langfuse cá nhân và ảnh không lộ key/secret.
- [x] Repository chạy lại được theo README.
- [x] Không có secret, API key, PII thật hoặc evidence của người khác/lớp khác.
- [x] URL repo và commit SHA cuối đã được nộp trên LMS/Codelabs.


