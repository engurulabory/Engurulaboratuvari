# ENGÜRÜ PLive™ — Beyin Mimarisi V3
## 78/100 → tasarım hedefi 100/100 | GitHub modeli ve karşıt sınamalar

**Durum:** Mühendislik adayı. GitHub model simülasyonu, OSi gerçek kabulünün yerine geçmez. **Yöntem:** ENGÜRÜ Süzgeci™ v2.4; mevcut sekiz aşama, yeni core yok, yeni sayaç yok, yeni issuer yok.

### Önce hangi 100?

Eski **78/100**, önceki görsel beyin şemasının 10 boyutlu yorumlayıcı değerlendirmesidir. Bu pakette **A01–A10'un 10'ar puanlık bağlayıcı tasarım gereksinimleri + otomatik karşıt testleri** ile ayrı ve nesnel bir **mimari spesifikasyon 100/100** hedefliyoruz. Eski puanı silmiyoruz; eşleştirme sözleşmedeki baseline78Crosswalk alanındadır. PLive bütünsel **ürün hazırlığı 67/100** ayrıca tutulur. OSi uygulama, ekran, performans, gerçek yazma ve Verified Finish **HOLD / ölçüm bekliyor** kalır.

### Beyin haritası

~~~mermaid
flowchart TD
    I["Tek insan: Hedef, kapsam, karar"] --> S["Süzgeç v2.4: sekiz aşama"]
    S --> W["Canonical iş sözleşmesi, kabul ve bağımlılıklar"]
    W --> Q{"Yapılacak işlem"}
    Q -->|"Salt-okunur"| O["OSi gerçek kaynakları, SHA ve tazelik"]
    Q -->|"Üretim"| L["Laboratuvar / Ana Fabrika: kanıtlı devir"]
    L --> C["Beş üretim alanı: Motor / Çekirdek / Web / App / Agent"]
    C --> T["Bağımlı işler, gerçek test, karşıt simülasyon, kanıt"]
    T --> G{"Tam kapsamlı onay + gerçek issuer/grant + writer?"}
    G -->|"HOLD"| H["Gerekçe + insan sahibi + yapılabilir sonraki adım"]
    G -->|"PASS"| D["Mevcut yetkili canonical writer + DoneCheck"]
    D --> P["Mevcut Native Progress Core: iş/paket/proje"]
    P --> F{"Tüm gerçek kabul koşulları tamam?"}
    F -->|"Evet"| Z["Verified Finish: BİTTİ → DUR"]
    F -->|"Hayır"| H
    P --> O
    O --> UI["PLive: Genel Durum / Şimdi / 5 görünür alan"]
    H --> UI
    UI --> E["İş detayı / kanıt çekmecesi"]
~~~

**Beynin hafızası** gerçek OSi canonical kaynaklarıdır; **durum hakikati** yalnız mevcut Progress Core'dur; **karar yöntemi** Süzgeç; **yetkili eli** mevcut kabul edilmiş writer'dır; **gözü** salt-okunur PLive adaptörüdür.

### İlk ekrandaki beş sabit üretim başlığı

Motor · Çekirdek · Web Yapımı · Uygulama / App Yapımı · Agent.

Başlıklar boş olsa bile görünür. İşi olmayan başlık **Kayıtlı iş yok** der. Kaynak sınıflandırması eksik iş **Sınıflandırma bekliyor** olarak görünür; altıncı başlık kurulmaz. Bir iş bir tek ana üretim başlığına sayılır. Çapraz etiketler ikinci iş veya ikinci sayaç yaratmaz. **Laboratuvar ve Ana Fabrika**, bu beş başlıktan ayrı bir **üretim ortamı boyutudur**; kaynak doğrulanmadan bu alan da tahmin edilmez.

**Laboratuvar → Ana Fabrika devir şartı:** gerçek kaynak proje kimliği, HEAD, kanıt SHA-256, kapsam, nitelendirme makbuzu ve açık insan kararı; devir kendiliğinden PASS veya ikinci iş kimliği üretmez.

### Deterministik üretim ve finiş

Hedef → Work Contract → Paket/iş bağımlılıkları → doğru yetkiyle yürütme → karşıt simülasyon → gerçek test → kanıt makbuzu → DoneCheck / insan kabulü → native readback → tüm proje koşulları karşılanırsa **BİTTİ → DUR**.

Hazır iş, yalnız önceki bağımlılıkları kabul edilmişse seçilir. Sıralama **öncelik artan; sonra workId alfabetik**; dosyanın okuma sırası sonucu etkilemez. Döngü veya kaynakta bulunmayan bağımlılık **HOLD**. İş, paket ve proje finişleri ayrı ele alınır. Bu anlatım yeni canonical state machine değildir.

Yanlış proje/eylem/scope, süresi bitmiş grant, tekrar nonce, yetkisiz writer, bozuk/eskimiş snapshot, hatalı DoneCheck, sonlandırılmamış Human Threshold durumunda **güvenli HOLD**. Salt-okunur ekran kullanılmaya devam eder; son doğrulanmış okumanın gerçek zaman damgası görünür. Simülasyonun 300 saniyelik tazelik örneği gerçek OSi SLA'sı değildir.

### Tasarım kabul kapıları — her biri 10 puan

| Kapı | Gereken tamamlanmış tasarım |
|---|---|
| A01 | Hedef–sonuç, kapsam ve bitiş sınırı |
| A02 | Beş üretim başlığının doğru sırada ve her zaman görünmesi |
| A03 | Laboratuvar / Ana Fabrika devir ve tek sahip kuralı |
| A04 | Hedeften Verified Finish'e yaşam döngüsü |
| A05 | Deterministik bağımlılık, sıralama ve döngü reddi |
| A06 | Tek insan onayı, ayrı issuer/grant/writer ve DoneCheck |
| A07 | Tek kaynak, native sayaç, SHA/provenance, tazelik |
| A08 | Hata, mükerrer işlem ve toparlanma |
| A09 | Mac-native erişim ve kullanıcının az işlem yapması |
| A10 | Gerçek kanıt kapıları, performans hedefi ve OSi finiş sınırı |

**Kabul matematiği:** 10 kapı × 10 puan; bir kapı gerekli kaynak alanı veya gerçek pozitif invariant değerinden yoksunsa kapsam puanı 100 verilemez. Model testleri **sahte** saha verisiyle resmî PASS oluşturamaz. GitHub CI yeşil olmadıkça mimari spesifikasyon PASS değil.

### Sabit olacak gerçek durum

- **P01:** Son OSi gözlemi 2/2, LOCKED, VERIFIED bildirmiştir; OSi'de final binding + native verify ile tekrar bağlanacak. Eski raporların HOLD kararı farklı tarihlere aittir.
- **P02:** Son gerçek makbuzlar S01 üç teknik kanıt adayını destekliyor, ancak 0/12 resmî COUNTED PASS. S01 yetkili yazma, G3 issuer/grant/writer HOLD.
- **P06:** Ayrı güvenlik otoritesi. P01'in izni P02'nin izni değildir.
- **Canonical main ve yerel OSi:** GitHub tasarım dalı bunları güncellemez.
- **Süzgeç:** Sekiz aşama sabit; v2.4 GitHub taslağı ayrı onay alanındadır.

### Simülasyon / CI ve sonraki adım

- Pure fixture simulator: tools/plive_brain_v3_simulator.py
- Karşıt testler: tests/test_plive_brain_architecture_v3.py
- GitHub workflow: .github/workflows/plive-brain-architecture-v3.yml

Çalıştırma: python -m unittest discover -s tests -p 'test_plive_brain_architecture_v3.py' -v

**GitHub hedef hükmü:** ARCHITECTURE_SPECIFICATION_100/100, SIMULATION_PASS, OSi_FIELD_HOLD.

**OSi'de ilk sonraki adım:** yalnız salt-okunur P01 final binding, P02 12 iş/4 paket, mevcut native Progress Core, uygulama kaynak/imza, beş kategorinin **gerçek** kaynak sınıflandırması ve performans baseline kontrolü. Gerçek üretim ve yetkili yazma ayrı kabul aşamasında.

**DUR:** GitHub modelini kanıtlayınca OSi'ye güvenli saha devir paketi hazırlıyoruz. OSi gerçek PASS olmadan ürün finalini ilan etmiyoruz.
