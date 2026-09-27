from __future__ import annotations

from app.crawler.adapters.base import ParsedCourse, ParsedCurriculum, ParsedOutcome


def _c(
    semester: int,
    code: str,
    name_tr: str,
    name_en: str,
    kind: str,
    ects: int,
    description: str,
    outcomes: list[str],
) -> ParsedCourse:
    return ParsedCourse(
        code=code,
        name_tr=name_tr,
        name_en=name_en,
        semester_raw=str(semester),
        course_type_raw=kind,
        ects_raw=str(ects),
        local_credit_raw=str(3 if ects >= 5 else 2),
        description=description,
        weekly_content=description,
        purpose=description,
        outcomes=[ParsedOutcome(outcome_no=i, text=t) for i, t in enumerate(outcomes, start=1)],
    )


def _lo(verb_tr: str, topic: str) -> list[str]:
    return [
        f"{topic} ile ilgili temel kavramları tanımlar ve listeler.",
        f"{topic} problemlerini analiz eder ve uygun yöntemi seçer.",
        f"{topic} için çalışan bir çözüm tasarlar ve geliştirir.",
        f"Sonucu değerlendirir ve {verb_tr}.",
    ]


CS_CORE = [
    _c(1, "CENG101", "Programlamaya Giriş", "Introduction to Programming", "Z", 6,
       "Değişken, kontrol yapıları, fonksiyon ve temel algoritmalar. Yazılım geliştirme temelleri.",
       _lo("doğrular", "programlamaya giriş")),
    _c(1, "MATH101", "Matematik I", "Calculus I", "Z", 6,
       "Limit, türev, integral. Mühendislik matematiği ve istatistik temelleri.",
       _lo("hesaplar", "matematik")),
    _c(1, "PHYS101", "Fizik I", "Physics I", "Z", 5,
       "Mekanik ve elektrik temelleri.",
       _lo("açıklar", "fizik")),
    _c(1, "CENG111", "Bilgisayar Mühendisliğine Giriş", "Intro to Computer Engineering", "Z", 4,
       "Meslek, etik, sistem temelleri ve yazılım-donanım ayrımı.",
       _lo("yorumlar", "meslek etiği")),
    _c(1, "TUR101", "Türk Dili I", "Turkish I", "Z", 2,
       "Akademik yazım ve iletişim.",
       _lo("yazar", "iletişim")),
    _c(2, "CENG102", "Nesne Yönelimli Programlama", "Object Oriented Programming", "Z", 6,
       "Sınıf, kalıtım, çok biçimlilik ve yazılım geliştirme temelleri.",
       _lo("geliştirir", "nesne yönelimli programlama")),
    _c(2, "MATH102", "Matematik II", "Calculus II", "Z", 6,
       "Çok değişkenli kalkülüs ve seri.",
       _lo("uygular", "matematik")),
    _c(2, "MATH121", "Ayrık Matematik", "Discrete Mathematics", "Z", 5,
       "Kümeler, graf, mantık, indüksiyon. Algoritma temelleri.",
       _lo("kanıtlar", "ayrık matematik")),
    _c(2, "CENG104", "Dijital Mantık", "Digital Logic", "Z", 5,
       "Kapılar, combinational/sequential circuits, sistem temelleri.",
       _lo("tasarlar", "dijital mantık")),
    _c(2, "ENG102", "İngilizce II", "English II", "Z", 3,
       "Teknik İngilizce.",
       _lo("özetler", "ingilizce")),
    _c(3, "CENG201", "Veri Yapıları ve Algoritmalar", "Data Structures and Algorithms", "Z", 6,
       "Liste, ağaç, graf, karmaşıklık, sıralama. Algoritma temelleri.",
       _lo("analiz eder", "veri yapıları ve algoritmalar")),
    _c(3, "CENG203", "Bilgisayar Organizasyonu", "Computer Organization", "Z", 5,
       "İşlemci, bellek hiyerarşisi, komut seti. Bilgisayar mimarisi.",
       _lo("açıklar", "bilgisayar mimarisi")),
    _c(3, "MATH201", "Lineer Cebir", "Linear Algebra", "Z", 5,
       "Matris, vektör uzayı, özdeğer.",
       _lo("hesaplar", "lineer cebir")),
    _c(3, "STAT201", "Olasılık ve İstatistik", "Probability and Statistics", "Z", 5,
       "Dağılımlar, hipotez, istatistiksel temeller.",
       _lo("yorumlar", "istatistik")),
    _c(3, "CENG205", "Programlama Dilleri", "Programming Languages", "S", 4,
       "Sözdizimi, semantik, derleyiciye giriş.",
       _lo("karşılaştırır", "programlama dilleri")),
    _c(4, "CENG202", "Veri Tabanı Sistemleri", "Database Systems", "Z", 6,
       "İlişkisel model, SQL, normalizasyon, transaction. Veri yönetimi.",
       _lo("tasarlar", "veri tabanı sistemleri")),
    _c(4, "CENG204", "İşletim Sistemleri", "Operating Systems", "Z", 6,
       "Süreç, iş parçacığı, bellek, dosya sistemi, kernel.",
       _lo("uygular", "işletim sistemleri")),
    _c(4, "CENG206", "Sistem Programlama", "Systems Programming", "Z", 5,
       "C, sistem çağrıları, sistem temelleri.",
       _lo("geliştirir", "sistem programlama")),
    _c(4, "CENG208", "Yazılım Mühendisliği", "Software Engineering", "Z", 5,
       "Gereksinim, tasarım, test, süreç, scrum.",
       _lo("değerlendirir", "yazılım mühendisliği")),
    _c(4, "CENG210", "Sayısal Yöntemler", "Numerical Methods", "S", 4,
       "Yaklaşık çözüm ve hata analizi.",
       _lo("uygular", "sayısal yöntemler")),
    _c(5, "CENG301", "Bilgisayar Ağları", "Computer Networks", "Z", 6,
       "Katmanlar, TCP/IP, yönlendirme, protokol.",
       _lo("analiz eder", "bilgisayar ağları")),
    _c(5, "CENG303", "Web Programlama", "Web Programming", "Z", 5,
       "HTTP, frontend, backend, platform geliştirme.",
       _lo("geliştirir", "web programlama")),
    _c(5, "CENG305", "Algoritma Analizi", "Algorithm Analysis", "Z", 5,
       "Asimptotik analiz, dinamik programlama, graf algoritmaları.",
       _lo("karşılaştırır", "algoritma analizi")),
    _c(5, "CENG307", "İnsan Bilgisayar Etkileşimi", "Human Computer Interaction", "S", 5,
       "Kullanıcı arayüzü, kullanılabilirlik, UX.",
       _lo("tasarlar", "insan bilgisayar etkileşimi")),
    _c(5, "CENG309", "Mikroişlemciler", "Microprocessors", "S", 4,
       "Gömülü sistem ve mimari.",
       _lo("kullanır", "mikroişlemciler")),
    _c(6, "CENG302", "Yapay Zeka", "Artificial Intelligence", "Z", 6,
       "Arama, bilgi temsili, makine öğrenmesi girişi.",
       _lo("geliştirir", "yapay zeka")),
    _c(6, "CENG304", "Bilgi Güvenliği", "Information Security", "Z", 5,
       "Kriptografi, kimlik doğrulama, siber güvenlik.",
       _lo("değerlendirir", "bilgi güvenliği")),
    _c(6, "CENG306", "Derleyici Tasarımı", "Compiler Design", "S", 5,
       "Lexical analiz, parsing, kod üretimi.",
       _lo("tasarlar", "derleyici")),
    _c(6, "CENG308", "Paralel Programlama", "Parallel Programming", "S", 5,
       "Thread, distributed computing, cloud.",
       _lo("geliştirir", "paralel ve dağıtık hesaplama")),
    _c(6, "CENG310", "Bilgisayar Grafikleri", "Computer Graphics", "S", 4,
       "Dönüşüm, rendering, etkileşimli görselleştirme.",
       _lo("üretilir", "bilgisayar grafikleri")),
    _c(7, "CENG401", "Makine Öğrenmesi", "Machine Learning", "S", 6,
       "Denetimli/denetimsiz öğrenme, sinir ağları.",
       _lo("uygular", "makine öğrenmesi")),
    _c(7, "CENG403", "Mobil Programlama", "Mobile Programming", "S", 5,
       "Android/iOS, özel platform geliştirme.",
       _lo("geliştirir", "mobil programlama")),
    _c(7, "CENG405", "Bulut Bilişim", "Cloud Computing", "S", 5,
       "Dağıtık sistemler, ölçekleme.",
       _lo("tasarlar", "bulut bilişim")),
    _c(7, "CENG407", "Mesleki Etik", "Professional Ethics", "Z", 3,
       "Etik, hukuk, toplum ve meslek.",
       _lo("eleştirir", "etik")),
    _c(7, "CENG490", "Bitirme Projesi I", "Senior Project I", "Z", 5,
       "Proje planı, gereksinim ve prototip.",
       _lo("tasarlar", "bitirme projesi")),
    _c(8, "CENG402", "Veri Madenciliği", "Data Mining", "S", 5,
       "Örüntü, sınıflandırma, veri yönetimi.",
       _lo("analiz eder", "veri madenciliği")),
    _c(8, "CENG404", "Gömülü Sistemler", "Embedded Systems", "S", 5,
       "Gerçek zaman, donanım-yazılım eş tasarımı.",
       _lo("geliştirir", "gömülü sistemler")),
    _c(8, "CENG406", "Bilgisayar Mimarisi II", "Computer Architecture II", "S", 5,
       "Pipeline, önbellek, çok çekirdek.",
       _lo("karşılaştırır", "bilgisayar mimarisi")),
    _c(8, "CENG491", "Bitirme Projesi II", "Senior Project II", "Z", 8,
       "Uygulama, test, rapor ve sunum.",
       _lo("üretilir", "bitirme projesi")),
    _c(8, "CENG408", "Seçmeli Staj", "Internship", "S", 2,
       "Saha deneyimi.",
       _lo("uygular", "staj")),
]

SE_CORE = [
    _c(1, "SE101", "Programlamaya Giriş", "Introduction to Programming", "Z", 6,
       "Yazılım geliştirme temelleri, temel programlama.",
       _lo("geliştirir", "programlama")),
    _c(1, "MATH101", "Matematik I", "Calculus I", "Z", 6,
       "Mühendislik matematiği.",
       _lo("hesaplar", "matematik")),
    _c(1, "SE111", "Yazılım Mühendisliğine Giriş", "Intro to Software Engineering", "Z", 5,
       "Süreç, meslek, etik, takım.",
       _lo("açıklar", "yazılım mühendisliği")),
    _c(1, "SE113", "Bilgisayar Sistemlerine Giriş", "Computing Essentials", "Z", 4,
       "İşletim sistemi ve ağ temelleri.",
       _lo("tanımlar", "bilgisayar sistemleri")),
    _c(1, "TUR101", "Türk Dili I", "Turkish I", "Z", 2,
       "İletişim.",
       _lo("yazar", "iletişim")),
    _c(2, "SE102", "Nesne Yönelimli Programlama", "Object Oriented Programming", "Z", 6,
       "Nesne modelleme ve kodlama.",
       _lo("geliştirir", "nesne yönelimli programlama")),
    _c(2, "MATH121", "Ayrık Matematik", "Discrete Mathematics", "Z", 5,
       "Mantık ve ayrık yapılar.",
       _lo("analiz eder", "ayrık matematik")),
    _c(2, "SE104", "Veri Yapıları", "Data Structures", "Z", 6,
       "Temel veri yapıları ve algoritmalar.",
       _lo("uygular", "veri yapıları")),
    _c(2, "SE106", "Web Teknolojileri", "Web Technologies", "Z", 5,
       "HTML/CSS/HTTP, platform geliştirme.",
       _lo("geliştirir", "web")),
    _c(2, "ENG102", "İngilizce II", "English II", "Z", 3,
       "Teknik İngilizce.",
       _lo("özetler", "ingilizce")),
    _c(3, "SE201", "Veri Tabanı Sistemleri", "Database Systems", "Z", 6,
       "SQL ve veri yönetimi.",
       _lo("tasarlar", "veri tabanı")),
    _c(3, "SE203", "Yazılım Gereksinimleri", "Software Requirements", "Z", 5,
       "Paydaş analizi, SRS, modelleme.",
       _lo("analiz eder", "yazılım gereksinimleri")),
    _c(3, "SE205", "Yazılım Süreçleri", "Software Process", "Z", 5,
       "Agile, scrum, CMMI.",
       _lo("karşılaştırır", "yazılım süreci")),
    _c(3, "STAT201", "Olasılık ve İstatistik", "Probability and Statistics", "Z", 5,
       "Ölçüm ve istatistik.",
       _lo("yorumlar", "istatistik")),
    _c(3, "SE207", "Kullanıcı Arayüzü Tasarımı", "UI Design", "S", 4,
       "HCI, UX, arayüz.",
       _lo("tasarlar", "kullanıcı arayüzü")),
    _c(4, "SE202", "Yazılım Tasarımı", "Software Design", "Z", 6,
       "Mimari, desen, UML.",
       _lo("tasarlar", "yazılım tasarımı")),
    _c(4, "SE204", "Yazılım Testi", "Software Testing", "Z", 5,
       "Birim/entegrasyon testi, doğrulama.",
       _lo("değerlendirir", "yazılım testi")),
    _c(4, "SE206", "İşletim Sistemleri", "Operating Systems", "Z", 5,
       "Süreç ve bellek yönetimi.",
       _lo("açıklar", "işletim sistemleri")),
    _c(4, "SE208", "Yazılım Kalitesi", "Software Quality", "Z", 5,
       "Metrik, kalite güvence.",
       _lo("ölçer", "yazılım kalitesi")),
    _c(4, "SE210", "Algoritmalar", "Algorithms", "S", 4,
       "Algoritma analizi.",
       _lo("analiz eder", "algoritmalar")),
    _c(5, "SE301", "Yazılım Mimarisi", "Software Architecture", "Z", 5,
       "Katmanlı, mikroservis, mimari karar.",
       _lo("tasarlar", "yazılım mimarisi")),
    _c(5, "SE303", "Bilgisayar Ağları", "Computer Networks", "Z", 5,
       "Protokol ve iletişim.",
       _lo("uygular", "bilgisayar ağları")),
    _c(5, "SE305", "Yazılım Proje Yönetimi", "Software Project Management", "Z", 5,
       "Maliyet, risk, zaman planı.",
       _lo("değerlendirir", "proje yönetimi")),
    _c(5, "SE307", "Web Uygulama Geliştirme", "Web Application Development", "Z", 5,
       "REST, güvenlik, platform.",
       _lo("geliştirir", "web uygulama")),
    _c(5, "SE309", "İnsan Bilgisayar Etkileşimi", "HCI", "S", 4,
       "Kullanılabilirlik testi.",
       _lo("eleştirir", "hci")),
    _c(6, "SE302", "Bilgi Güvenliği", "Information Security", "Z", 5,
       "Uygulama güvenliği, kriptografi.",
       _lo("doğrular", "güvenlik")),
    _c(6, "SE304", "Yazılım Doğrulama ve Geçerleme", "V&V", "Z", 5,
       "Doğrulama, geçerleme, kalite.",
       _lo("değerlendirir", "doğrulama")),
    _c(6, "SE306", "Mobil Uygulama Geliştirme", "Mobile Development", "S", 5,
       "Android/iOS platform.",
       _lo("geliştirir", "mobil")),
    _c(6, "SE308", "Yapay Zeka", "Artificial Intelligence", "S", 5,
       "Yazılım sistemlerinde ML.",
       _lo("uygular", "yapay zeka")),
    _c(6, "SE310", "DevOps ve Sürümleme", "DevOps", "S", 5,
       "CI/CD, süreç otomasyonu.",
       _lo("kurar", "devops")),
    _c(7, "SE401", "Kurumsal Yazılım", "Enterprise Software", "S", 5,
       "Büyük ölçekli tasarım.",
       _lo("tasarlar", "kurumsal yazılım")),
    _c(7, "SE403", "Bulut ve Dağıtık Sistemler", "Cloud and Distributed Systems", "S", 5,
       "Dağıtık hesaplama.",
       _lo("geliştirir", "dağıtık sistemler")),
    _c(7, "SE405", "Mesleki Uygulama", "Professional Practice", "Z", 3,
       "Etik, takım, iletişim.",
       _lo("savunur", "mesleki etik")),
    _c(7, "SE490", "Bitirme Projesi I", "Capstone I", "Z", 6,
       "Gereksinim ve tasarım.",
       _lo("tasarlar", "bitirme")),
    _c(7, "SE407", "Oyun Yazılımı", "Game Software", "S", 4,
       "Grafik ve etkileşim.",
       _lo("üretilir", "oyun")),
    _c(8, "SE402", "Yazılım Bakımı", "Software Maintenance", "S", 4,
       "Evrim, borç, kalite.",
       _lo("analiz eder", "bakım")),
    _c(8, "SE404", "Veri Yoğun Uygulamalar", "Data Intensive Apps", "S", 5,
       "Veri yönetimi ve ölçek.",
       _lo("geliştirir", "veri yoğun uygulama")),
    _c(8, "SE491", "Bitirme Projesi II", "Capstone II", "Z", 8,
       "Uygulama ve değerlendirme.",
       _lo("üretilir", "bitirme")),
    _c(8, "SE406", "Seçmeli Staj", "Internship", "S", 3,
       "Saha uygulaması.",
       _lo("uygular", "staj")),
    _c(8, "SE408", "Yazılım Ölçümü", "Software Measurement", "S", 4,
       "Metrik ve kalite ölçümü.",
       _lo("ölçer", "yazılım ölçümü")),
]


def _clone(course: ParsedCourse) -> ParsedCourse:
    return ParsedCourse(
        code=course.code,
        name_tr=course.name_tr,
        name_en=course.name_en,
        semester_raw=course.semester_raw,
        course_type_raw=course.course_type_raw,
        ects_raw=course.ects_raw,
        local_credit_raw=course.local_credit_raw,
        description=course.description,
        weekly_content=course.weekly_content,
        purpose=course.purpose,
        outcomes=list(course.outcomes),
    )


def curriculum_for_program(program) -> ParsedCurriculum:
    is_se = "yazılım" in (program.name or "").lower() or "software" in (program.name or "").lower()
    base = [_clone(c) for c in (SE_CORE if is_se else CS_CORE)]
    uni = (program.university.name if program.university else "") or ""
    key = uni.lower()

    drop_codes: set[str] = set()
    extras: list[ParsedCourse] = []
    if "orta doğu" in key or "metu" in key:
        drop_codes = {"CENG310", "CENG408"}
        extras = [
            _c(7, "CENG411", "Doğal Dil İşleme", "Natural Language Processing", "S", 5,
               "Yapay zeka, dil modelleri.",
               _lo("geliştirir", "doğal dil işleme")),
        ]
    elif "boğaziçi" in key or "boun" in key:
        drop_codes = {"CENG309"}
        extras = [
            _c(6, "CENG322", "Kriptografi", "Cryptography", "S", 5,
               "Güvenlik ve kriptografi.",
               _lo("analiz eder", "kriptografi")),
        ]
    elif "istanbul teknik" in key or "itu" in key:
        extras = [
            _c(5, "CENG321", "Sinyal İşleme", "Signal Processing", "S", 4,
               "Sayısal sinyal, sistem temelleri.",
               _lo("uygular", "sinyal işleme")),
        ]
    elif "yıldız" in key:
        drop_codes = {"CENG306"}
        extras = [
            _c(6, "CENG330", "Siber Güvenlik", "Cyber Security", "S", 5,
               "Siber güvenlik uygulamaları.",
               _lo("değerlendirir", "siber güvenlik")),
        ]
    elif "hacettepe" in key:
        extras = [
            _c(7, "CENG421", "Biyoenformatik", "Bioinformatics", "S", 4,
               "Veri yönetimi ve algoritma uygulamaları.",
               _lo("analiz eder", "biyoenformatik")),
        ]
    elif "ege" in key:
        drop_codes = {"CENG404"}
    elif "dokuz" in key:
        extras = [
            _c(6, "SE331", "Yazılım Ürün Hatları", "Software Product Lines", "S", 5,
               "Yazılım tasarımı ve süreç.",
               _lo("tasarlar", "ürün hatları")),
        ]
    elif "bahçeşehir" in key or "bau" in key:
        extras = [
            _c(5, "SE321", "Oyun Motorları", "Game Engines", "S", 5,
               "Grafik ve etkileşimli teknikler.",
               _lo("geliştirir", "oyun motoru")),
        ]
    elif "örnek üniversitesi b" in key:
        drop_codes = {"SE407"}
    elif "örnek üniversitesi a" in key:
        extras = [
            _c(7, "CENG431", "Robotik", "Robotics", "S", 4,
               "Gömülü sistem ve yapay zeka.",
               _lo("tasarlar", "robotik")),
        ]

    courses = [c for c in base if c.code not in drop_codes] + extras
    if (program.language or "tr") == "en":
        for c in courses:
            c.name_tr = c.name_en
    ects = sum(int(float(c.ects_raw)) for c in courses if c.ects_raw)
    return ParsedCurriculum(
        academic_year="2025/2026",
        version_name="lisans-katalog",
        total_ects_raw=str(ects),
        courses=courses,
        parser_name="catalog_seed",
    )
