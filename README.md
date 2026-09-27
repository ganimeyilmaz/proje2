# Türkiye Üniversiteleri Mühendislik Müfredat Analiz Projesi

Kamuya açık Bologna / ders bilgi paketi sayfalarından **Bilgisayar Mühendisliği** ve **Yazılım Mühendisliği** müfredatını toplayan, kalitesini ölçen ve programlar arası karşılaştırma üreten yeniden çalıştırılabilir sistem.

Bu depo, proje tanımındaki kabul kriterlerinin çalışan bir iskeletini içerir: adapter/parser, izlenebilir kaynak kaydı, normalizasyon, kalite skoru, Jaccard + TF-IDF cosine, Bloom yaklaşık sınıflandırması, CS2023/SE2014 anahtar sözcük eşlemesi, dashboard ve CSV dışa aktarma.

## Etik sınır

- Yalnızca kimlik doğrulama gerektirmeyen sayfalar
- CAPTCHA, oturum veya güvenlik mekanizması yok
- `robots.txt` okunur; istekler hız sınırlıdır
- Kişisel akademisyen verisi toplanmaz

## Kurulum (Windows)

```powershell
cd C:\Users\ganim\OneDrive\Desktop\yeni
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Çalıştırma

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Tarayıcı: http://127.0.0.1:8000

İlk açılışta envanter (`seed/universities.csv`) ve iki örnek üniversitenin yerel HTML müfredatı yüklenir. Gerçek bir üniversite için dashboard’dan kamuya açık URL ekleyip program kartındaki **yeniden çek** düğmesini kullanın.

## Test

```powershell
pytest -q
```

## Mimari

1. Kaynak envanteri (CSV + SQLite)
2. HTTP crawler (httpx, gecikme, hash, snapshot)
3. Adapter: `generic_html` ve `bologna_like`
4. Normalizasyon (tür, dönem, AKTS, başlık)
5. Kalite motoru (0–100, konfigüre ağırlıklar `app/quality/engine.py`)
6. Analiz: benzerlik, Bloom, CS2023/SEEK
7. FastAPI + HTML dashboard
8. CSV dışa aktarma

## Veri modeli

`universities` → `programs` → `curriculum_versions` → `semesters` → `courses` → içerik / öğrenme çıktıları  
Kanıt: `source_snapshots` · Hata: `validation_issues`

Ham HTML `data/snapshots/` altında hash ile saklanır.

## Sonraki adımlar (proje planı gün 3–20)

- Daha fazla üniversite şablonu için yeni adapter sınıfları
- Playwright ile yalnızca JS-render edilen **kamuya açık** sayfalar
- Elle 20 kayıt doğrulama tablosu
- Embedding tabanlı benzerlik (baseline ile kıyaslayarak)


