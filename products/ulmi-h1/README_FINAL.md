# ENGÜRÜ Mühendisi ULMi™ — H1 V7 · Kanıtlı yerel model rota güvenliği

**Durum:** `PASS_SCOPED_REAL_ENGINEERING` · `H1_V7_OWNER_SAFARI=NOT_TESTED` · `REAL_QWEN_INFERENCE=HOLD` · `INDEPENDENT_DONECHECK=NOT_EXECUTED` · `VERIFIED_FINISH=HOLD`.

V6 korunmuştur; V7 ayrı kaynak kopyasıdır. Özgün V22 ve A/B/C sözleşmelerinin hiçbir kabul maddesi değiştirilmedi. **Geçmişteki V5 Safari 60/60 tek gerçek kullanıcı koşusu V7 kabulü yerine geçmez.** Teslim kapsamı yalnız çalışan H1 HTML ürünüdür.

## Tek ürünün başlatılması

ZIP'i **ayrı bir klasöre** çıkarın. Önceki H1 sunucusu 18990 portunda çalışıyorsa onu durdurun veya `ENGURU_USTA_PORT` ile farklı port belirleyin. Mac Finder'da `START_ULMI_H1.command` dosyasını açın. Başlatıcı eski portu yanlışlıkla yeniden kullanmaz; tarayıcıyı ancak aynı klasördeki `server.py` SHA ve V7 sürüm kimliği eşleşince açar. Bu kolaylık **Mac saha testinden geçmemiştir**; Linux izole mantık testi 6/6 PASS.

Uygulama `http://127.0.0.1:18990/` adresindedir (özel port seçildiyse o port). İzinli izole ürün klasörünün `STATE/` dizini kullanılır; ek ücretli API/kurulum yoktur. `http://127.0.0.1:18990/uat-final` bağımsız gerçek tarayıcı koşusu başlatma ekranıdır.

## Gerçek yeni kullanıcı işlevi

Ana ekranda **Yerel Qwen3 ile özgün taslak** kartı eklendi. Türkçe mühendislik görevi girildiğinde mevcut H1 `/api/plan` yürütücüsü **yalnız 127.0.0.1:11434/api/chat** üzerinden Qwen3 14B biçiminde JSON plan ister. Geçerli model etiketi, `done: true`, assistant rolü ve sıkı JSON içeriği bulunmazsa `HOLD` ile reddeder. Bu öneri hiçbir shell komutu çalıştırmaz. Dosya ancak mevcut açık **Onayla ve üret** düğmesine basıldıktan sonra izole workspace'e yazılır. Modelden gelen serbest Python kodu otomatik alt süreçte test/çalıştırılmaz: `functional_test=NOT_TESTED`.

Modelin kendisi veya kaynak doğruluğu **bağımsız atteste edilmez**. Bir loopback servisinin kendi `model` alanını `qwen3:14b` diye beyan etmesi gerçek model ağırlığı, kalite veya owner kabulünü kanıtlamaz.

- `/api/model/receipt?task_id=...` — aynı H1 oturum token'ıyla SQLite'daki **istek/cevap SHA ve kendini beyan etmiş model rotası** makbuzunu geri okur.
- `/api/model/readiness` — salt-okunur yerel model listesi, Shared AI portu ve **sekiz rolün kaynak/baseline** hazırlığını ayrı sınıflandırır; **model çıkarımı çalıştırmaz**. Gerçek Mac'te çalışma kanıtı ve bağımsız yetki hâlâ ayrıca gerekir.
- `/api/status` — çalışan kaynak dosyalarının SHA ve birleşik sürüm kimliği.

## RED→GREEN ve kanıt

V6 **yanlış model kimliğiyle READY plan oluşturabiliyordu**; V7 25/25 yerel gerçek HTTP/SQLite testinde bu ve diğer 9 güvenlik dışlanımını reddetti. Bu kontrollü testte Ollama şekline sahip sağlayıcı **SENTETİKTİR; gerçek Qwen değildir**. Shared AI 8787 sözleşme/rota karşıt kontrolleri 18/18 sentetik gerçek HTTP. Sürüm/SHA 7/7; Mac açıcı mantığı Linux'ta 6/6; önceki regresyon aileleri 6/6, 17/17, 49/49, 44/44, 49/49, 42/42, 34/34; V22 değişmez ID/oracle denetimi 16/16.

## Açık özgün kabul

`V22_HISTORICAL_TECHNICAL=4/12` (*güncel tam kanıtlı ID sayısı olarak otomatik kabul edilmez*), `V22_FORMAL=0/12`, `PILOTS_A_B_C=0/8 EACH`, `4H=0/56`, `REAL_QWEN=HOLD`, `3_REAL_OWNER_BROWSER_E2E=HOLD`, `OWNER_PRODUCER_AUTH=HOLD`, `DONECHECK=NOT_EXECUTED`, `OWNER_FINAL=NOT_ISSUED`.

**V7’nin açık tek kapısı:** Gerçek owner Mac'inde kaynakları birebir doğrulanan Qwen/Shared AI oturumunda özgün mühendislik görevinin model yanıtını ve yöntem rollerini **yetkili kaynak SHA + bağımsız inceleme** ile kanıtlamak. Yalnız model portu açık olması veya olumlu sentetik fixture, W01/W04/W05/W06/W09 tam PASS değildir.

**Kurulan teknik sınır:** `LOCAL_HTTP_MODEL_RESPONSE_CHECKS=PASS_SCOPED`; `INDEPENDENT_MODEL_AUTHENTICATION=HOLD`; `VERIFIED_FINISH=HOLD`.

## V7 gerçek tarayıcı kabul sınırı

`NOT_TESTED_BROWSER` — Bu V7+W07/W08 kaynak yaması owner Mac Safari ortamında henüz çalıştırılmadı. Geçmiş V5 Safari 60/60 yalnız V5 kaynakları için korunur; bu paketin kabulü değildir. Bağımsız DoneCheck ve owner nihai imzası ayrıca HOLD.

## 18 Kasım kaynak kimliği dondurma eki

İş 08 güvenli dosya tanıtıcısı onarımı, taşınabilir V6 kaynak karşılaştırma testi ve V22 12/12 kanıt defteri bu kaynak adayına eklendi. Tek doğru güncel kaynak kimliği `FROZEN_HANDOFF/SOURCE_FREEZE_IDENTITY.json` içindedir. Bu paket resmî ürün finali değildir: `SOURCE_FREEZE_CANDIDATE=PASS_SCOPED`, `INDEPENDENT_DONECHECK=NOT_EXECUTED`, `OWNER_FINAL=NOT_ISSUED`, `VERIFIED_FINISH=HOLD`.

## H1 tek hedefli teslim sınırı

Bu pakette H1 arayüzündeki ikinci hedef sunumu kaldırılmıştır. H02 mimari harita kimliği korunur; H2 hedefi değildir. Önceki kanıt ve özgün V22 sözleşmesi kaynak arşivinde değişmezdir. Bu yeni H1 görünümü için eski ZIP SHA veya eski Safari kabulü kullanılamaz. Çalışan ürün, Python HTTP sunucusu ve izole SQLite ile açılır; tek HTML dosyasını `file://` ile açmak gerçek üretimi çalıştırmaz.
