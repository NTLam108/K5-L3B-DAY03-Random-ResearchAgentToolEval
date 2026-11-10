# Team

## Thông tin nhóm

- Tên nhóm: Random
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Random-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: (điền sau khi push)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Trọng Lâm (nhóm trưởng) | 2A202603817 |  |  | Setup, baseline v0 + phân tích lỗi, vòng v1 |
|   2 | Trần Gia Bảo | 2A202603914 |  |  | Tool mới (`tool.py`, `TOOL.md`, đăng ký) + unit test |
|   3 | Vũ Xuân Hiếu | 2A202603860 | vuhieu3205@gmail.com | vuhieuvh | 10 case eval nhóm, vòng v2/v3 |
|   4 | Trịnh Hưng Thịnh | 2A202603907 |  |  | UI, chat live + transcript, báo cáo nhóm |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

## Nguyễn Trọng Lâm - 2A202603817

### Phần việc phụ trách

- Setup môi trường, `.env`, preflight; chạy baseline v0 và phân tích lỗi (B2); vòng v1.

### Đóng góp cụ thể

-

### Bằng chứng

-

## Trần Gia Bảo - 2A202603914

### Phần việc phụ trách

- Tool mới: `tools/<tên>/tool.py`, `TOOL.md`, đăng ký trong `tools/__init__.py` và `tools.yaml`; ≥ 3 unit test.

### Đóng góp cụ thể

-

### Bằng chứng

-

## Vũ Xuân Hiếu - 2A202603860

### Phần việc phụ trách

- 10 case trong `data/eval_group.json` (5 single + 5 multi turn); vòng v2, v3; chạy `--suite group`.

### Đóng góp cụ thể

- Thiết kế và cài đặt đủ 10 case trong `starter_v0/data/eval_group.json` gồm 5 single-turn và 5 multi-turn, bao quát 6 loại failure types (`wrong_tool`, `wrong_arg_value`, `wrong_boundary`, `unnecessary_tool`, `out_of_scope`, `missing_info`).
- Tích hợp kiểm thử tool mới `cite` ở cả single-turn (`G01_cite_paper_apa`), multi-turn (`M_G01_papers_then_cite_bibtex`), và kiểm thử thiếu metadata (`G03_clarify_missing_paper_title`).
- Chạy benchmark `--suite group` qua OpenRouter (`gpt-4o-mini`), phân tích chi tiết lỗi lần chạy đầu (6/10) về cơ chế default argument và multi-turn context, sau đó tinh chỉnh đạt **10/10 PASS (100%)**.
- Cập nhật mục B3 trong `report/team/group_report.md` và hoàn thiện báo cáo cá nhân `report/team/2A202603860_VuXuanHieu.md`.

### Bằng chứng

- File bộ test: `starter_v0/data/eval_group.json` (10 test cases hợp lệ theo schema).
- Run file bằng chứng: `starter_v0/runs/v3_B_group_openrouter_20261110T192054234552.json` (10/10 PASS, `provider_error_cases: 0`, độ chính xác 1.0).
- Bảng B3 trong `report/team/group_report.md` và báo cáo cá nhân `report/team/2A202603860_VuXuanHieu.md`.

## Trịnh Hưng Thịnh - 2A202603907

### Phần việc phụ trách

- UI (Streamlit/Vercel) + link dùng thử; chat live ≥ 3 lượt và transcript; `group_report.md`.

### Đóng góp cụ thể

-

### Bằng chứng

-
