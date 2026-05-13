"""
AvtoBaholash AI Service
Groq yoki Anthropic Claude — sozlamalarga qarab tanlanadi.

.env faylda qaysi kalit bo'lsa o'sha ishlatiladi:
  GROQ_API_KEY=gsk_...        ← bepul, tez
  ANTHROPIC_API_KEY=sk-ant-...← to'liq funksional

Ikkala kalit ham bo'lmasa — demo rejim ishlaydi.
"""
import json, logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_client():
    """
    Avval Groq, keyin Anthropic tekshiradi.
    Qaysi kalit .env da bo'lsa o'shani ishlatadi.
    """
    # 1. Groq (bepul, llama modellari)
    groq_key = getattr(settings, 'GROQ_API_KEY', '')
    if groq_key:
        try:
            from groq import Groq
            return ('groq', Groq(api_key=groq_key))
        except Exception as e:
            logger.error(f"Groq client xato: {e}")

    # 2. Anthropic Claude
    anthropic_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if anthropic_key:
        try:
            import anthropic
            return ('anthropic', anthropic.Anthropic(api_key=anthropic_key))
        except Exception as e:
            logger.error(f"Anthropic client xato: {e}")

    return None  # demo rejim


def _call_ai(prompt, max_tokens=800):
    """
    Umumiy AI chaqiruvi — Groq yoki Anthropic formatini avtomatik tanlaydi.
    """
    result = get_client()
    if not result:
        return None

    provider, client = result

    try:
        if provider == 'groq':
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Groq bepul modeli
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()

        elif provider == 'anthropic':
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text.strip()

    except Exception as e:
        logger.error(f"AI chaqiruv xato ({provider}): {e}")
        return None


def _parse_json(text):
    """AI javobidan JSON ajratib oladi."""
    if not text:
        return None
    try:
        if '```' in text:
            parts = text.split('```')
            for part in parts:
                part = part.strip()
                if part.startswith('json'):
                    part = part[4:]
                part = part.strip()
                if part.startswith('{'):
                    return json.loads(part)
        return json.loads(text)
    except Exception:
        # JSON ichidan qidirish
        start = text.find('{')
        end   = text.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass
    return None


# ─────────────────────────────────────────────────────────
# 1. Sillabus moslik tekshiruvi
# ─────────────────────────────────────────────────────────
def check_syllabus_compliance(title, description, questions_text, topics):
    topics_str = "\n".join(f"- {t}" for t in topics) if topics else "Mavzular kiritilmagan"

    prompt = f"""Sen ta'lim sifatini nazorat qiluvchi mutaxassissan. O'zbek tilida javob ber.
Topshiriq: {title}
Tavsif: {description}
Savollar:
{questions_text[:1500]}
Sillabus mavzulari:
{topics_str}

Topshiriqning sillabusga mosligini baholang (0-100). FAQAT JSON qaytaring:
{{"score": 85, "feedback": "...", "topics_covered": ["..."], "topics_missing": ["..."], "topics_extra": ["..."]}}"""

    text = _call_ai(prompt, max_tokens=800)
    result = _parse_json(text)

    if result and 'score' in result:
        return result

    return {
        'score': 75.0,
        'feedback': "Demo rejim. GROQ_API_KEY yoki ANTHROPIC_API_KEY ni .env ga qo'shing.",
        'topics_covered': topics[:3],
        'topics_missing': [],
        'topics_extra': [],
    }


# ─────────────────────────────────────────────────────────
# 2. Test baholash
# ─────────────────────────────────────────────────────────
def grade_test(title, qwa):
    total = len(qwa)
    if not total:
        return {'score': 0, 'feedback': "Savol topilmadi.", 'correct_count': 0, 'details': []}

    correct = sum(
        1 for q in qwa
        if str(q.get('student_answer', '')).upper().strip() ==
           str(q.get('correct_answer', '')).upper().strip()
    )
    score   = round(correct / total * 100, 1)
    details = [{
        'text':       q['text'][:80],
        'is_correct': str(q.get('student_answer','')).upper().strip() ==
                      str(q.get('correct_answer','')).upper().strip(),
        'student':    q.get('student_answer', '—'),
        'correct':    q.get('correct_answer', '—'),
    } for q in qwa]

    # Noto'g'ri javoblar uchun AI izohi
    wrong = [d for d in details if not d['is_correct']][:4]
    feedback = ""

    if wrong:
        wt = "\n".join(
            f"- {w['text']} (Javob: {w['student']}, To'g'ri: {w['correct']})"
            for w in wrong
        )
        prompt = f"""Fan: {title}. Natija: {correct}/{total} ({score}%).
Xatolar:
{wt}
Talabaga O'zbek tilida qisqa (2 jumla) konstruktiv izoh yoz. Faqat izoh matni, boshqa narsa yo'q."""

        ai_text = _call_ai(prompt, max_tokens=300)
        if ai_text:
            feedback = ai_text.strip()

    if not feedback:
        if score >= 90:   feedback = f"Ajoyib! {total} dan {correct} tasiga to'g'ri javob berdingiz."
        elif score >= 70: feedback = f"Yaxshi natija! {correct}/{total}. Ba'zi mavzularni mustahkamlang."
        elif score >= 50: feedback = f"Qoniqarli. {correct}/{total}. Xato mavzularni qayta ko'ring."
        else:             feedback = f"Yana urinib ko'ring. {correct}/{total}. O'qituvchingizga murojaat qiling."

    return {
        'score': score,
        'feedback': feedback,
        'correct_count': correct,
        'total_count': total,
        'details': details,
    }


# ─────────────────────────────────────────────────────────
# 3. Yozma ish baholash
# ─────────────────────────────────────────────────────────
def grade_written(title, subject, question, answer):
    wc = len(answer.split()) if answer else 0

    prompt = f"""Sen {subject} fanidan mutaxassissan. O'zbek tilida baho.
Topshiriq: {title}. Savol: {question[:300]}
Talaba javobi ({wc} so'z): {answer[:1800]}
100 ballik tizimda baho. FAQAT JSON:
{{"score":75,"feedback":"...","strengths":["..."],"improvements":["..."]}}"""

    text   = _call_ai(prompt, max_tokens=500)
    result = _parse_json(text)

    if result and 'score' in result:
        return result

    s = min(85, max(25, wc * 1.5))
    return {
        'score': round(s, 1),
        'feedback': f"Demo baholash: {wc} so'z. AI kalitini .env ga qo'shing.",
        'strengths': ["Topshiriq bajarildi"],
        'improvements': [],
    }


# ─────────────────────────────────────────────────────────
# 4. Accessibility tekshiruvi (TTS uchun)
# ─────────────────────────────────────────────────────────
def check_accessibility(questions_data):
    import re as _re
    formula_chars = ['\u222b','\u2211','\u221a','\u00b2','\u00b3','\u2264','\u2265','\u221e','\u03c0',
                     '\u2202','\u0394','\u2207','\u2208','\u2209','\u2282','\u2283','\u222a','\u2229',
                     '\u2192','\u2190','\u2194','\u21d2','\u21d4','\u2200','\u2203','\u00ac','\u2227',
                     '\u2228','\u2295','\u00b1','\u00d7','\u00f7','\u2260','\u2248','\u2261']
    latex_patterns = ['\\frac','\\int','\\sum','\\sqrt','\\alpha','\\beta','\\gamma',
                      '\\delta','\\theta','\\lambda','\\sigma','\\omega','\\infty',
                      '\\partial','\\nabla','\\begin','\\end','$','\\(','\\[']

    auto_accessible   = []
    auto_inaccessible = []
    reasons           = {}

    for q in questions_data:
        qid  = q['id']
        text = q.get('text', '')
        has_formula    = any(c in text for c in formula_chars)
        has_latex      = any(p in text for p in latex_patterns)
        has_image_only = bool(q.get('image')) and len(text.strip()) < 10

        if has_formula:
            auto_inaccessible.append(qid); reasons[qid] = "Formula belgisi"
        elif has_latex:
            auto_inaccessible.append(qid); reasons[qid] = "LaTeX formati"
        elif has_image_only:
            auto_inaccessible.append(qid); reasons[qid] = "Faqat rasm"
        else:
            auto_accessible.append(qid)

    if questions_data:
        q_list = "\n".join([
            f"{i+1}. [ID:{q['id']}] {q.get('text','')[:120]}"
            for i, q in enumerate(questions_data[:20])
        ])
        prompt = (
            "Test savollarini ovozli o'qish (TTS) uchun mosligini baholab JSON qaytaring.\n"
            "Mos EMAS: matematik formulalar, integral, differensial, matritsa, faqat rasm.\n"
            "Mos: oddiy matn savollar, ta'riflar, tushunchalar.\n\n"
            f"Savollar:\n{q_list}\n\n"
            'JSON: {"accessible_ids":[1,3],"inaccessible_ids":[2,4],"reasons":{"2":"integral","4":"rasm"}}'
        )
        ai_text = _call_ai(prompt, max_tokens=500)
        result  = _parse_json(ai_text)

        if result and ('accessible_ids' in result or 'inaccessible_ids' in result):
            id_list = [q['id'] for q in questions_data]
            def resolve(lst):
                out = []
                for x in lst:
                    if isinstance(x, int) and 1 <= x <= len(id_list):
                        out.append(id_list[x-1])
                    elif x in id_list:
                        out.append(x)
                return out
            acc_ids   = resolve(result.get('accessible_ids', []))
            inacc_ids = resolve(result.get('inaccessible_ids', []))
            if acc_ids or inacc_ids:
                return {
                    'accessible_ids':   acc_ids,
                    'inaccessible_ids': inacc_ids,
                    'accessible_count': len(acc_ids),
                    'total_count':      len(questions_data),
                    'feedback':         f"AI tekshiruvi: {len(acc_ids)}/{len(questions_data)} savol TTS uchun mos.",
                    'reasons':          result.get('reasons', reasons),
                }

    return {
        'accessible_ids':   auto_accessible,
        'inaccessible_ids': auto_inaccessible,
        'accessible_count': len(auto_accessible),
        'total_count':      len(questions_data),
        'feedback':         f"Avtomatik tekshiruv: {len(auto_accessible)}/{len(questions_data)} savol mos.",
        'reasons':          reasons,
    }


# ─────────────────────────────────────────────────────────
# 5. Savol bankida takroriy tekshiruv
# ─────────────────────────────────────────────────────────
def check_bank_duplicates_ai(questions):
    if len(questions) < 2:
        return {}

    q_list = "\n".join([f"{i+1}. {q.text[:80]}" for i, q in enumerate(questions[:25])])

    prompt = f"""Quyidagi test savollarini ko'rib, takroriy yoki juda o'xshash juftlarni toping.

{q_list}

FAQAT JSON qaytaring:
{{"duplicates": [{{"index": 3, "similar_to": 1, "note": "bir xil savol"}}]}}
Takroriy yo'q bo'lsa: {{"duplicates": []}}"""

    text   = _call_ai(prompt, max_tokens=400)
    result = _parse_json(text)

    if result and 'duplicates' in result:
        return {d['index']: d for d in result['duplicates']}
    return {}


# ─────────────────────────────────────────────────────────
# Bildirishnoma yuborish
# ─────────────────────────────────────────────────────────
def send_notification(user, title, message, ntype='info', link=''):
    from assessment.models import Notification
    Notification.objects.create(
        recipient=user, title=title, message=message,
        notification_type=ntype, link=link
    )


# ─────────────────────────────────────────────────────────
# Rate Limiting — Django cache (multi-worker safe)
# ─────────────────────────────────────────────────────────
def check_rate_limit(user_id, action, limit=10, window_minutes=60):
    """
    Django cache orqali rate limiting.
    Redis CACHES sozlansa — multi-worker da ham ishlaydi.
    LocMemCache — development uchun yetarli.
    """
    from django.core.cache import cache
    import time

    key     = f"rl:{user_id}:{action}"
    now_ts  = int(time.time())
    cutoff  = now_ts - window_minutes * 60
    timeout = window_minutes * 60 + 60

    timestamps = cache.get(key, [])
    timestamps = [t for t in timestamps if t > cutoff]

    if len(timestamps) >= limit:
        return False

    timestamps.append(now_ts)
    cache.set(key, timestamps, timeout)
    return True
