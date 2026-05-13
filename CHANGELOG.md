# AvtoBaholash — O'zgarishlar jurnali

## v1.1 — Bug Fix Release

### 🔴 Kritik tuzatishlar
- **Dashboard routing** — barcha foydalanuvchilar o'z dashboardiga yo'naltiriladi
  (`dashboard_router` view qo'shildi, `/dashboard/` endi umumiy kirish nuqtasi)
- **DOCX import** — savollar import qilингanda A/B/C/D variantlari to'g'ri ustunlardan olinadi (cells[3,4,5,6])
- **Xavfsizlik** — `.env` faylidan haqiqiy kalitlar o'chirildi, `.gitignore` kuchaytirildi

### 🟠 Muhim tuzatishlar
- **Takroriy sozlamalar** — `LOGIN_URL` ikki marta yozilgan edi, bittasi o'chirildi
- **Hardcoded URL** — `grade_book` da to'g'ridan-to'g'ri path o'rniga `reverse()` ishlatiladi
- **Test POST/GET tartib** — savollar tartibi session da saqlanadi, POST da bir xil keladi
- **JSON parsing** — AI javobidan JSON ajratish `re.search` bilan mustahkamlandi

### 🟡 O'rtacha tuzatishlar
- **Guruhsiz talaba** — dashboard da ogohlantirish xabari ko'rsatiladi
- **Silent except** — `except: pass` o'rniga `logger.warning(...)` ishlatiladi
- **PDF kirish huquqi** — o'qituvchi faqat o'z topshirig'ini yuklab olishi mumkin
- **O'qituvchi o'chirish** — topshiriqlar cascade o'chirilishi haqida ogohlantirish
- **Race condition** — parallel submission `try/except IntegrityError` bilan himoyalandi

### 🔵 Kichik tuzatishlar
- **Hardcoded parol** — `'Edulens2024!'` o'rniga `settings.DEFAULT_STUDENT_PASSWORD`
- **bleach** — `requirements.txt` dan ishlatilmayotgan kutubxona o'chirildi

### Sidebar (foydalanuvchi bildirgan muammo)
- **Double active** — JS va template ikkalasi active qo'shib qo'yardi → tuzatildi
- **Yo'qoladigan linklar** — har bir sahifada sidebar alohida yozilgan edi, ba'zisi to'liq emas
- **O'zgaruvchan matn** — `templates/includes/sidebar_*.html` yaratildi, barcha sahifalarda bir xil
- Barcha 31 ta template `{% include 'includes/sidebar_XXX.html' %}` ga o'tkazildi

## v1.0 — Dastlabki chiqarilish
- 4 ta rol, 3 tur topshiriq, AI baholash
- PDF, Excel, Word export
- Telegram, dark mode, TTS, analytics

## v1.2 — Bug Fix

### 🔴 Kritik
- `analytics/empty.html` — fayl yo'q edi, `TemplateDoesNotExist` chiqardi.
  Endi `kafedra_analytics.html` bo'sh context bilan render qilinadi va ogohlantirish ko'rsatiladi.

### 🟠 Muhim
- `_import_bank_docx` — `option_d` noto'g'ri `cells[5]` dan olinardi (option_c bilan bir xil).
  Tuzatildi: `cells[6]` va minimum `len(cells) >= 4` tekshiruvi.
- Yozma/fayl topshirishda race condition — `sub.save()` `try/except` bilan himoyalandi,
  yuborishdan oldin `Submission.objects.filter(...).exists()` tekshiruvi qo'shildi.
- Excel import — kafedra mudiri kafedraga biriktirilmagan bo'lsa xabar ko'rsatiladi.

## v1.3 — Test oynasi yangilandi

### Asosiy o'zgarishlar
- **Test oynasi dizayni** — to'liq qayta yozildi: gradient kartalar, progress bar, navigatsiya dots
- **Vaqt persistence** — sahifa yangilansa yoki qayta kirilsa vaqt davom etadi
- **Javoblar persistence** — berilgan javoblar o'chib ketmaydi
- **Har talabaga har xil tartib** — talaba ID + topshiriq ID asosida deterministik shuffle
- **TTS faqat inklyuziv** — `is_accessible=True` bo'lgan talabalar uchun
- **O'zbek TTS** — edge-tts `uz-UZ-SardorNeural` ovozi
- **Ovozdan javob** — tuut signali → mikrofon → A/B/C → avtomatik keyingi savol
- **Klaviatura** — A/B/C, →/←, R (qayta o'qi)

### Word import yangilandi
- **To'g'ri javob matn sifatida** yoziladi (harf emas), tizim aralashtirib harfini belgilaydi
- **Formulali testlar** — LibreOffice orqali WMF → GIF, rasmlar savollarga biriktiriladi

### Boshqa
- 5 ballik tizim (5/4/3/2/1)
- Inklyuziv talaba qo'shilayotganda belgilash imkoni
- Universal Excel import (barcha rollar)
- Sidebar muammolari (double active, yo'qoladigan linklar) bartaraf etildi

## v2.0 — Katta yangilanish

### Tizim nomi
- **EduLens → AvtoBaholash** — barcha 20 ta faylda o'zgartirildi

### 1. Inklyuziv ta'lim
- ✅ TTS faqat `is_accessible=True` talabalar uchun (test + yozma ish)
- ✅ Yozma ish ko'rsatmasini ham ovoz bilan o'qish tugmasi
- ✅ Grade book jadvalida inklyuziv talabalar ♿ belgisi bilan ko'rsatiladi
- ✅ AI test savollarini TTS uchun mosligini tekshiradi (formula/rasm/LaTeX aniqlash)

### 2. Yozma ish sillabus baholash
- ✅ AIAnalysisLog ga yozma ish uchun ham log yoziladi
- ✅ AI izoh va sabab bazaga saqlanadi

### 3. AI baholash bazaga yozish
- ✅ `ai_strengths`, `ai_improvements`, `ai_syllabus_fb` yangi maydonlar
- ✅ Migration: `0004_ai_detailed_fields`
- ✅ Natija sahifasida kuchli tomonlar (yashil) va yaxshilash kerak (to'q sariq) alohida ko'rsatiladi

### 4. Word import — LaTeX, formula, rasm
- ✅ `docx_importer.py` — BaseDocxParser asosida, bizning modellarimizga moslashtirilgan
- ✅ OMML formulalar → LaTeX → MathJax orqali brauzerda ko'rsatiladi
- ✅ Inline rasmlar savolga biriktiriladi
- ✅ Aralash (matn + formula + rasm) savollar qo'llab-quvvatlanadi
- ✅ TTS mosligi avtomatik aniqlanadi (formulasiz savollar accessible=True)

### 5. MathJax integratsiyasi
- ✅ `\( ... \)` va `$ ... $` formulalar brauzerda chiroyli ko'rsatiladi

### 6. Responsive dizayn
- ✅ Barcha jadvallarda `overflow-x-auto` — mobilda gorizontal scroll
- ✅ `main.css` ga mobil stillar qo'shildi
- ✅ Modal lar mobilga moslashtirildi

### 7. Texnik tuzatishlar
- ✅ `tts_audio` funksiyasi 2 marta aniqlangan edi — biri o'chirildi
- ✅ `bleach` requirements dan olib tashlandi

## v2.1 — Audit tuzatishlari

### 🔴 Kritik
- `docx_parser.py` — mavjud bo'lmagan modellar import qilinar edi, stub ga aylantirilib `docx_importer.py` ga yo'naltirildi
- `bleach` requirements dan o'chirilgan, `docx_importer.py` da `html.escape` bilan almashtirildi
- Rate limiting — `_request_counts` dict o'rniga `Django cache` backend (Redis bilan ham ishlaydi)
- `DEFAULT_STUDENT_PASSWORD` — `settings.py` da hardcoded emas, `.env` dan olinadi

### 🟠 Muhim
- `settings_railway.py` — `DATABASE_URL` yo'q bo'lsa ogohlantirish, Email SMTP sozlandi, Redis ixtiyoriy
- Anti-cheat kuchaytirildi — blur, copy/paste, focus lost vaqti ham yoziladi
- Media fayl yuklashda MIME type tekshiruvi va path traversal himoyasi
- N+1 query — `select_related('subject','department')`, `prefetch_related('groups')` qo'shildi
- O'lik gTTS funksiyasi (`tts_audio` 1-versiyasi) o'chirildi — faqat edge-tts qoldi

## v2.2 — Yakuniy to'liqlashtirish

### Inklyuziv ta'lim
- ✅ Kafedra mudiri: talabalar ro'yxatida ♿ tugmasini bosib inklyuziv/oddiy ga o'tkazish
- ✅ Admin: foydalanuvchilar ro'yxatida talabalar uchun inklyuziv toggle
- ✅ Grade book da inklyuziv talabalar ♿ belgisi bilan ko'rsatiladi
- ✅ `toggle_accessible` view va URL qo'shildi
- ✅ `kafedra_edit_student`, `admin_edit_user` viewlar qo'shildi

### AI baholash ko'rsatish
- ✅ Feedback sahifasida AI baho, strengths, improvements ko'rsatiladi
- ✅ O'qituvchi har bir talaba javobida AI izohni ko'ra oladi

### Xavfsizlik va UX
- ✅ Test oynasida `beforeunload` ogohlantirish — tasodifan chiqmaslik uchun
- ✅ Anti-cheat: `blur` event ham kuzatiladi

### Texnik
- ✅ 404 va 500 xato sahifalari yaratildi
- ✅ `handler404`, `handler500` urls.py ga qo'shildi
- ✅ `gtts` requirements dan olib tashlandi (faqat edge-tts qoldi)

## v2.2 — Inklyuziv ta'lim va UX yaxshilandi

### Yangi funksiyalar
- **Admin/Kafedra: talabani tahrirlash** — foydalanuvchi ma'lumotlarini va inklyuziv statusini o'zgartirish modal'i
- **Kafedra students**: har bir talabada ✏️ Edit tugmasi — inklyuziv, guruh, parol o'zgartirish
- **Admin users**: har bir foydalanuvchida ✏️ Edit tugmasi — barcha maydonlar + inklyuziv
- **Student result**: AI feedback to'liq — izoh + kuchli tomonlar (yashil) + yaxshilash (to'q sariq)
- **Demo login tugmalari** olib tashlandi (production uchun)

## v2.3 — Production audit fix

### 🔴 Kritik
- **AI baholash sinxron edi** — endi `threading` orqali background da ishlaydi. Talaba darhol javob oladi, AI baho keyin keladi.
- **AI sillabus tekshiruvi** — topshiriq aktivlashtirilganda ham background ga o'tkazildi
- **SECRET_KEY** production tekshiruvi qo'shildi — DEBUG=False bo'lsa `django-insecure` qiymatda bo'lsa server ishga tushmaydi
- **filetype** kutubxonasi haqiqatan ishlatilmoqda — fayl yuklashda server tomonida MIME tekshiruvi

### 🟠 Muhim
- Sentry SDK ixtiyoriy integratsiyasi (production xatolarini kuzatish)
- 47/47 template OK
- 29/29 URL OK (admin/kafedra/teacher/student barcha sahifalar)
- 35/35 unit test OK

## v2.4 — UX yaxshilandi, DOCX import to'liq

### Tuzatishlar
- **Bildirishnomalar** — sidebar to'liq ko'rsatadi (avval faqat 2 link bor edi)
- **Edit qalamcha** — `yesno:"true,false"` quote muammosi tuzatildi
- **Word import tugmasi** — chiroyli modal + drag&drop + progress bar
- **DOCX import** — to'liq qayta yozildi:
  - OMML formulalar → LaTeX → MathJax
  - Inline rasmlar (savol va variantlar uchun alohida)
  - WMF/EMF (Microsoft Equation Editor) ham qo'llab-quvvatlanadi
  - 37 ta savol Amaliy_matematika_test.docx dan muvaffaqiyatli import qilindi
- **Variant rasmlari** — `image_a/b/c/d` maydonlari Question modeliga qo'shildi
- **Test sahifasi** — variant rasmlarini matn yonida ko'rsatadi
- **Kafedra → Fanlar** — har fanga o'qituvchi biriktirish modal:
  - O'qituvchi tanlash
  - Guruhlar tanlash (multi-select)
  - Biriktirilgan o'qituvchilar pillar sifatida ko'rinadi
  - Olib tashlash tugmasi

### Yangi maydonlar
- `Question.image_a`, `image_b`, `image_c`, `image_d` (variant rasmlari)
- Migration: `0005_question_image_a_question_image_b_..._and_more`

## v2.5 — Production-grade kengaytmalar

### Anti-cheat (server-side)
- `tab_switches` + `copy_count` + `paste_count` server tomonida tahlil qilinadi
- Severity (medium/high) avtomatik aniqlanadi
- Grade book da ⚠ shubhali belgi
- O'qituvchi shubhali submissionlarni darhol ko'radi

### Question modeli kuchaytirildi
- `topic` — savol mavzusi
- `difficulty` — easy / medium / hard
- `points` — savol uchun ball
- Form ham yangilandi

### Appeal system (bahoga e'tiroz)
- Talaba result sahifasidan e'tiroz bildiradi (kamida 20 belgi)
- Appeal status: pending → reviewing → accepted/rejected
- O'qituvchi review_appeal sahifasida qaror qabul qiladi
- Yangi baho qo'yish imkoni
- Avtomatik bildirishnoma har 2 tomonga
- Appeal tarixi result sahifasida ko'rinadi

### Notification scheduling (deadline reminder)
- `send_reminders` command qayta yozildi
- 24 soat qolganda eslatma
- 1 soat qolganda eslatma
- O'tib ketgan topshiriqlar avtomatik 'closed' holatga
- Takroriy eslatma yuborilmaydi

### Yangi maydonlar
- `Submission.appeal_status`, `appeal_reason`, `appeal_response`, `appealed_at`
- `Question.difficulty`, `points`
- Migration: `0006`, `0007`
