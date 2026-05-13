# AvtoBaholash — AI yordamida Akademik Baholash Platformasi
### v1.0 Final — To'liq Yakunlangan

---

## Ishga tushirish

```bash
unzip edulens_final.zip && cd edulens_s3
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

**→ http://127.0.0.1:8000** · **Admin: http://127.0.0.1:8000/admin/**

### Demo loginlar

| Rol            | Login     | Parol    |
|----------------|-----------|----------|
| Admin          | admin     | admin123 |
| Kafedra mudiri | kafedra1  | admin123 |
| O'qituvchi     | teacher1  | admin123 |
| Talaba         | student1  | admin123 |

---

## Barcha funksiyalar

### Admin
| | |
|---|---|
| Dashboard | Statistika, foydalanuvchilar, kafedralar |
| CRUD | Kafedralar, Foydalanuvchilar, Fanlar |
| Tahlil | Chart.js grafiklari |
| Hisobotlar | Kafedra bo'yicha ko'rsatkichlar |
| Sozlamalar | Tizim va AI kalitlari |

### Kafedra Mudiri
| | |
|---|---|
| Dashboard | O'qituvchilar reytingi, imtihon jadvali, AI jurnal, Chart.js grafigi |
| O'qituvchilar | CRUD, fanlarga biriktirish |
| Talabalar | CRUD + **Excel (.xlsx) import** |
| Fanlar | CRUD, guruhlar yaratish |
| Imtihon jadvali | CRUD, sanalar, xonalar |
| AI Tahlil jurnali | Topshiriq-sillabus moslik ballari (o'qituvchi bilmaydi) |
| Tahlil | O'qituvchi reytingi, mavzu xatolari, grafik |

### O'qituvchi
| | |
|---|---|
| Fanlarim | Sillabus yuklash (PDF/DOCX yoki matn) |
| Topshiriq yaratish | Test / Yozma ish / Fayl (3 tur) |
| Word import | `.docx` fayldan savollar import |
| **Savol banki** | Saqlash, import, AI takroriy tekshiruv, topshiriqqa ko'chirish |
| **Mavzu kvota** | Har mavzudan nechta savol tushishini belgilash |
| Faollashtirish | AI sillabus tekshiruvi + accessibility belgilash + talabalarga xabarnoma |
| Baholash jurnali | AI baho + qo'lda tasdiqlash |
| Excel export | Ranglar + statistika varag'i |
| PDF export | Offline tarqatish uchun |
| Feedback | Shikoyatlarga javob berish |
| Statistika | Baho taqsimoti, fan bo'yicha o'rtacha, Chart.js |

### Talaba
| | |
|---|---|
| Test yechish | Timer, anti-cheat (tab log), sahifa bloklash |
| **Ko'zi ojiz (TTS)** | Ovoz bilan o'qish, A/B/C klaviatura, "R" qayta o'qish, tugma toggle |
| Yozma ish | Matn yozish, rasm yuklash |
| Fayl topshirish | Hajm va tur validatsiyasi |
| Natijalar | AI izoh, savol tahlili, o'qituvchi izohi |
| Feedback | Shikoyat → 24 soat javob yo'q → kafedra mudiriga auto-escalation |
| Progress | Fanlar bo'yicha statistika, tarix |
| Rivojlanish | Vaqt dinamikasi, eng kuchli/zaif fan, Chart.js |

### AI (Anthropic Claude)
| | |
|---|---|
| Sillabus tekshiruvi | Topshiriq mavzularga 0-100% moslik — **faqat kafedra mudiriga ko'rinadi** |
| Test baholash | To'g'ri/noto'g'ri hisoblash + O'zbek tilida izoh |
| Yozma ish baholash | 100 ball + kuchli/zaif tomonlar |
| Accessibility | TTS uchun mos savollarni belgilash |
| Savol banki | Takroriy savollarni aniqlash |
| **Demo rejim** | API kalit bo'lmasa ham ishlaydi |

### Tizim
| | |
|---|---|
| Bildirishnomalar | Tizim ichki xabarnomalar |
| Telegram | Webhook + profilda Chat ID kiritish |
| **send_reminders** | Cron: deadline eslatmasi + feedback 24-soat escalation |
| Parol tiklash | Email orqali (Django built-in) |
| **Dark mode** | Toggle tugma, localStorage da saqlanadi |
| **Mobil moslashuv** | Responsive sidebar toggle |
| Rate limiting | AI so'rovlar uchun |
| Session lock | Test vaqtida bir joydan kirish |
| Fayl validatsiyasi | Hajm (MB) va tur (.pdf, .docx ...) tekshiruvi |
| 35 unit test | Modellar, viewlar, AI, export, rol izolyatsiyasi |
| Production config | gunicorn, nginx, systemd, cron, settings_prod.py |

---

## Tizim talablari

```
Python 3.10+
Django 4.2
```

## .env sozlamalari

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# AI baholash (ixtiyoriy — demo rejim ham bor)
ANTHROPIC_API_KEY=sk-ant-...

# Telegram (ixtiyoriy)
TELEGRAM_BOT_TOKEN=...
```

## Testlar

```bash
python manage.py test assessment   # 35 ta test, ~90 soniya
python manage.py check             # Tizim tekshiruvi
```

## Cron (server da)

```bash
# Har 6 soatda: deadline eslatmasi + feedback escalation
0 */6 * * * python manage.py send_reminders
```

## Production

```bash
# To'liq yo'riqnoma: DEPLOY.md
pip install gunicorn psycopg2-binary
DJANGO_SETTINGS_MODULE=edulens.settings_prod gunicorn edulens.wsgi
```

---

**AvtoBaholash v1.0** · Django 4.2 · Anthropic Claude · Chart.js · Tailwind CSS
