# Báo cáo Kiến trúc Phần mềm — MLOps

> 🇬🇧 **[English version](README.en.md)**  
> **Môn học:** Kiến trúc Phần mềm (Software Architecture)  
> **Nhóm:** 7 thành viên  
> **Báo cáo:** Kiến trúc MLOps: Thiết kế, Cơ sở Lý luận và Mô hình Phân tầng

[![Build LaTeX PDF](../../actions/workflows/build-pdf.yml/badge.svg)](../../actions/workflows/build-pdf.yml)

---

## Mục lục

- [Cấu trúc Repository](#cấu-trúc-repository)
- [Phân công File](#phân-công-file)
- [Thiết lập Repository](#thiết-lập-repository)
- [Quy tắc Commit & Branch](#quy-tắc-commit--branch)
- [Build PDF trên máy (Locally)](#build-pdf-trên-máy-locally)
- [Kiểm tra PDF qua GitHub Actions](#kiểm-tra-pdf-qua-github-actions)
- [Hướng dẫn nhanh: Clone → Sửa → Push](#hướng-dẫn-nhanh-clone--sửa--push)
- [Demo MLOps](#demo-mlops)
- [Liên hệ](#liên-hệ)

---

## Cấu trúc Repository

```
SoftwareArchitectureReport/
├── main.tex                        ← File chính (CHỈ Nhóm trưởng sửa)
├── references.bib                  ← Tài liệu tham khảo (mọi người có thể THÊM)
├── hcmut-report.cls                ← HCMUT LaTeX class (không sửa)
├── codespace.sty                   ← Style định dạng code (không sửa)
├── sections/
│   ├── 01-introduction.tex         ← Member B
│   ├── 02-mlops-concepts.tex       ← Member C
│   ├── 03-design-rationale.tex     ← Member D
│   ├── 04-pros-cons.tex            ← Member E
│   ├── 05-layered-architecture.tex ← Member F
│   └── 06-conclusion.tex           ← Member A
├── figures/                        ← Hình ảnh (PNG/PDF/SVG) — mọi người có thể thêm
├── graphics/
│   └── hcmut.png                   ← Logo HCMUT (không sửa)
├── demo/                           ← Demo MLOps stack (Member G phụ trách)
│   ├── README.md
│   ├── docker-compose.yml
│   ├── train_demo.py
│   └── serve_demo.py
└── .github/
    └── workflows/
        └── build-pdf.yml           ← GitHub Actions — tự động build PDF
```

---

## Phân công File

| File | Người phụ trách | Ghi chú |
|---|---|---|
| `main.tex` | **Member A** | Nhóm trưởng — KHÔNG ai khác được sửa |
| `sections/01-introduction.tex` | **Member B** | Giới thiệu |
| `sections/02-mlops-concepts.tex` | **Member C** | Khái niệm MLOps |
| `sections/03-design-rationale.tex` | **Member D** | Cơ sở lý luận thiết kế |
| `sections/04-pros-cons.tex` | **Member E** | Đánh giá ưu nhược điểm |
| `sections/05-layered-architecture.tex` | **Member F** | Kiến trúc phân tầng |
| `sections/06-conclusion.tex` | **Member A** | Kết luận |
| `demo/` | **Member G** | MLOps Demo stack |
| `references.bib` | **Mọi người** | Chỉ THÊM entry mới, không xoá entry cũ |
| `figures/` | **Mọi người** | Đặt tên rõ ràng: `memberX-diagram-name.png` |

> ⚠️ **Quy tắc vàng:** Mỗi người **chỉ sửa file của mình**.  
> Nếu cần thay đổi file của người khác, vui lòng tạo **GitHub Issue** và thảo luận trước.

---

## Thiết lập Repository

### Bảo vệ nhánh `main` (khuyến nghị)

1. **Settings** → **Branches** → **Add branch protection rule**
2. Branch name pattern: `main`
3. ✅ **Require a pull request before merging**
4. ✅ **Require status checks to pass** → chọn `build-pdf`
5. Nhấn **Create**

---

## Quy tắc Commit & Branch

### Format message commit

```
<type>(<file or section>): <short description>
```

**Ví dụ hợp lệ:**
```
feat(02-mlops-concepts): add maturity levels table
fix(03-design-rationale): fix compile error missing end{table}
fig(figures): add layered architecture diagram for section 05
ref(references): add Google MLOps whitepaper 2023
demo(demo): update docker-compose to add PostgreSQL
```

**Các loại commit:**

| Type | Khi nào dùng |
|---|---|
| `feat` | Thêm nội dung mới |
| `fix` | Sửa lỗi nội dung hoặc compile |
| `fig` | Thêm/sửa hình ảnh |
| `ref` | Thêm tài liệu tham khảo |
| `demo` | Liên quan đến thư mục `demo/` |
| `style` | Sửa định dạng, không đổi nội dung |
| `docs` | Sửa tài liệu README |

### Đặt tên Branch

```
<member-name>/<short-description>
```

**Ví dụ:**
```
memberB/introduction-draft
memberC/mlops-concepts-tables
memberG/demo-docker-setup
```

**Quy trình làm việc:**

1. Tạo branch mới từ `main`
2. Commit và push lên branch của mình
3. Mở **Pull Request** vào `main`
4. Chờ **ít nhất 1 người** approve trước khi merge

---

## Build PDF trên máy (Locally)

### Yêu cầu cài đặt

Cài đặt một trong hai bộ công cụ sau:

**Lựa chọn A — TeX Live (khuyến nghị)**
```bash
# Linux / Ubuntu / Debian
sudo apt install texlive-full

# macOS
brew install --cask mactex

# Windows: tải TeX Live tại https://tug.org/texlive/
```

**Lựa chọn B — MiKTeX**
- Tải tại: https://miktex.org/download
- Khi build lần đầu, MiKTeX sẽ tự động tải các package còn thiếu.

### Lệnh build

```bash
# Từ thư mục gốc của repo:
latexmk -pdf -interaction=nonstopmode main.tex
```

File PDF kết quả sẽ được tạo tại `main.pdf`.

```bash
# Dọn dẹp file tạm:
latexmk -c

# Dọn dẹp hoàn toàn (bao gồm cả file PDF):
latexmk -CA
```

### Sử dụng VS Code + LaTeX Workshop

1. Cài extension **LaTeX Workshop** (`james-yu.latex-workshop`)
2. Mở file `main.tex`
3. Nhấn `Ctrl+Alt+B` để build &nbsp;|&nbsp; Nhấn `Ctrl+Alt+V` để xem PDF trực tiếp

---

## Kiểm tra PDF qua GitHub Actions

Mỗi khi push commit hoặc tạo Pull Request, GitHub Actions sẽ **tự động build file PDF**.

**Cách xem kết quả:**

1. Vào tab **Actions** trên repo GitHub
2. Chọn run mới nhất
3. ✅ **Build thành công** → tải PDF từ mục **Artifacts** > `report-pdf`
4. ❌ **Build thất bại** → xem log tại bước "Compile LaTeX document" để sửa lỗi

> 💡 **Mẹo:** Trước khi push, nên chạy `latexmk -pdf main.tex` trên máy để phát hiện lỗi sớm.

---

## Hướng dẫn nhanh: Clone → Sửa → Push

### Lần đầu tiên (clone repo)

```bash
# 1. Clone repo về máy
git clone https://github.com/Tuelord/Seminar.git
cd Seminar

# 2. Tạo branch làm việc riêng
git checkout -b memberX/your-task-name
# Ví dụ: git checkout -b memberB/introduction-draft
```

### Mỗi phiên làm việc

```bash
# 1. Cập nhật code mới nhất từ main
git fetch origin
git rebase origin/main

# 2. Sửa file được phân công
#    (ví dụ: sections/01-introduction.tex)

# 3. Kiểm tra build trên máy
latexmk -pdf -interaction=nonstopmode main.tex

# 4. Stage và commit thay đổi
git add sections/01-introduction.tex
git commit -m "feat(01-introduction): add motivation subsection"

# 5. Push branch lên GitHub
git push origin memberX/your-task-name

# 6. Mở Pull Request trên GitHub
```

### Thêm hình ảnh

```bash
# Đặt file hình ảnh vào thư mục figures/
cp my-diagram.png figures/memberX-diagram-name.png
git add figures/memberX-diagram-name.png
git commit -m "fig(figures): add layered architecture diagram"
git push
```

**Chèn hình vào file LaTeX:**
```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=0.8\linewidth]{memberX-diagram-name}
  \caption{Mô tả hình ảnh.}
  \label{fig:your-label}
\end{figure}
```

### Thêm tài liệu tham khảo

**Bước 1: Thêm mục trích dẫn vào `references.bib`:**
```bibtex
@article{authorkey2024,
  author  = {Author, Name},
  title   = {Title of the Paper},
  journal = {Journal Name},
  year    = {2024},
  volume  = {1},
  pages   = {1--10}
}
```

**Bước 2: Trích dẫn trong file `.tex`:**
```latex
Theo nghiên cứu của \cite{authorkey2024}, ...
```

---

## Demo MLOps

Xem [`demo/README.md`](demo/README.md) để biết hướng dẫn chi tiết cách chạy demo stack MLOps.

**Yêu cầu:** Docker Desktop, Python 3.10+

```bash
cd demo

# Khởi động Docker containers
docker compose up -d

# Chạy demo training
python train_demo.py
# → Giao diện MLflow UI: http://localhost:5000

# Khởi động API serving
python serve_demo.py
# → Giao diện API Swagger Docs: http://localhost:8000/docs
```

---

## Liên hệ

| Thành viên | Vai trò | File phụ trách |
|---|---|---|
| Member A | Nhóm trưởng | `main.tex`, `06-conclusion.tex` |
| Member B | Thành viên | `01-introduction.tex` |
| Member C | Thành viên | `02-mlops-concepts.tex` |
| Member D | Thành viên | `03-design-rationale.tex` |
| Member E | Thành viên | `04-pros-cons.tex` |
| Member F | Thành viên | `05-layered-architecture.tex` |
| Member G | Kỹ thuật | `demo/`, GitHub setup |

---

*Cập nhật lần cuối: 24/10/2026*
