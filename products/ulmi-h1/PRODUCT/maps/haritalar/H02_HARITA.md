# H02 — Beyin ve Karar Mimarisi
## ENGÜRÜ UstaMimar OSi™ · Teori, Tasarım, Teknik Hazırlık ve Zülfikar V1.4.1

**Harita:** `H02` · **Hedef 1:** ACTIVE / HTML prototip · **Hedef 2:** PARKED / Mac OSi · **Yetki:** Owner.
**Kapsam hükmü:** `PASS_SCOPED_DESIGN_SELF_CHECKED_ONLY`. Bu harita, fiilen çalışan UstaMimar mühendislik ürününün ya da Mac kurulumu kabulünün kanıtı değildir.

### Niyet ve kapsam
Yerel modelin önerisini görev/sözleşme/otorite kontrolüyle sınırlayarak karar üretmek.

**Ana soru:** Usta nasıl düşünüyor ve riskli kararı kim veriyor?
**Sorumlu rol:** Tek Usta karar katmanı + owner

### Kaynak ve bütünlük
Kaynak: owner V1.2 ürün kararı; V1.1 hizalama; V1 temel iş/kabul sözleşmesi; özgün UM V1 matrisi ve yalnız salt-okunur GitHub AGENTS.md referansı. Asıl SHA-256 eşlikleri üst `HARITALAR_V1_KAYNAK_MATRISI.json` içindedir. Git blob SHA-1 ile SHA-256 farklıdır; ana Saray'a yazma yetkisi türetilmez.

### Kuramsal ilkeler ve mimari sınırlar
- K01–K03 hedef ve bağlam
- K04–K06 hazırlık ve plan
- K07–K09 inşa kontrolü
- K10–K12 finiş ve seçici öğrenim

### Şema
```mermaid
flowchart TD
  G["Görev ve köken"] --> C["K01–K06 hedef/hazırlık"] --> L["Ollama/Qwen · plan adayı"] --> V{"Kaynak, şema, yetki?"}
  V -->|Evet| X["H03 izinli araç talebi"]
  V -->|Hayır| H["HOLD / owner kararı"]
  X --> D["K10–K12 sonuç ve öğrenim"]
```

### Teknik giriş–çıkış ve bağlantı sözleşmesi
**Girdi**
- görev zarfı, kabul ID ve kaynak SHA
- çevrimdışı Ollama/Qwen model yanıtı

**Çıktı**
- yapılandırılmış plan ve risk sınıfı
- yetkilendirilmeyi bekleyen araç isteği

**Arayüz ve veri bağı (hedef tasarım; mevcut API iddiası değil)**
- plan.task_id = görev zarfı task_id
- model_output = öneri; authority_ref üretmez
- plan -> H07 kontrol -> H03 araç

**Bağlı üst/yan haritalar:** H03, H07.
**Korunan gereksinim/iş/yetenek izleri:** R02, R06, R08, R12, UM-03, UM-10, UM-12, W02, W08. 4H özgün H01/H02/DG02/DG03/DG04 koşulları ayrı asıl sözleşmelerden doğrulanır.

### Zülfikar V1.4.1 · Üçlü senaryo / onarım
- **SIM1 (normal):** Gerekli kaynak varsa plan oluşturulur ve scoped onaya gönderilir. Beklenen hüküm `PASS_DESIGN_RULE_ONLY`; gerçek icra makbuzu talep edilirse `NOT_TESTED`.
- **SIM2 (karşıt):** Modelin özgün dosyadaki kötü niyetli talimatı yetki olarak kabul edilmez. Beklenen hüküm `SAFE_REJECT`, yetkisiz dış etki 0.
- **SIM3 (kesinti/onarım):** Kırık plan geçersiz şema olarak HOLD; deterministik başlangıç planıyla onarım adımı önerilir. Beklenen hüküm `HOLD_OR_RECOVERY_NOT_FAKE_FINISH`.
- **Döngü Onarım:** Gözlem → kök neden → dar değişiklik → yeniden SIM1/SIM2/SIM3 → regresyon → yalnız kanıtlı hüküm.

### Kabul şartı / beklenen teslim
**Tasarım uygunluğu:** Model hiçbir koşulda kendi yetkisini veya bağımsız kabulünü üretmez.
**Tasarım riskleri:** prompt injection ile sahte owner yetkisi, modelin uydurduğu kaynak veya test.

**Yapısal tasarım değerlendirmesi (10 bağımsız anlam başlığı × 10 puan):** G01, G02, G03, G04, G05, G06, G07, G08, G09, G10. Bu belgede tüm alanlar bulunduğu için yerel kendi-yazarlı rubrik `100/100`; kapsam `SELF_ASSESSED_DESIGN`. Harici hakem veya gerçek teknik performans olarak değerlendirilmez.

**Hedef 1 gerçek bitiş için:** Model hiçbir koşulda kendi yetkisini veya bağımsız kabulünü üretmez. İlgili kod, gerçek görev/araç/test makbuzları ve ürünün özgün kabul kimlikleri W07–W14 aşamasında ayrıca kanıtlanır.
**Hedef 2:** `PARKED`; `MAC_INSTALL_GO=NOT_GRANTED`, `W15/M01–M06=NOT_TESTED`. Gerçek işletim, gerçek model ve Mac saha yeteneği burada test edilmemiştir.
