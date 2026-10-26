# ENGÜRÜ Zülfikar™ V1.3.1 — Tek Sabit Kabul ve Bitiş Bağı

**Yönetim kararı (26 Ekim 2026):** Tek ana kaynak, altı alanın ilk ve son puanları dâhil **mevcut** \`ZULFIKAR_V131_OPERATIONAL_SCORECARD_V1.json\` dosyasıdır. Diğer hazırlık ve simülasyon kayıtları bu kaynağı destekler; yeni bir genel puan cetveli oluşturulmaz. Sözleşme \`canonicalClosure\` altında iki hedefi **kesin sırayla** taşır.

## Hedef 1 — gerçek yönetişim onarımı

\`6/6 ALAN 100/100 + ACTUAL_REAL_TASK_EVIDENCE + EXISTING_DONECHECK + AUTHORIZED_HUMAN_THRESHOLD → VERIFIED_FINISH\`.

Korunan teknik kazanımlar: hedef/kod/test üçü 100/100; kapsamlı hazırlık 3×100/100 (PR #246). Korunan gerçek saha durumu: yönetişim 98 HOLD, projeler arası 90 HOLD, gerçek bitirme 65 HOLD, birleşik 91 HOLD.

**Üç somut kapanış işi:**

- \`ZF.G1.01 / GOVERNANCE\`: Mevcut Mac owner/issuer, görev kapsamı, canlı kaynak ve bağımsız doğrulama. **Yürütücü:** mevcut owner Human Threshold; sahada yetki makbuzu.
- \`ZF.G1.02 / PORTABILITY\`: Dondurulan üç tür gerçek yetkili görev ve her birinin source→handler→output→test→bağımsız gözlem kanıtı. **Yürütücü:** mevcut Work/Mac Engineer tek görev yazıcısı.
- \`ZF.G1.03 / E2E_REAL\`: Kaynaktan kullanıcı sonucuna gerçek uçtan uca yürütme; kesintiden devam, eş koşullu gerçek muadil ölçümü, DoneCheck ve insan kabulü. **Yürütücü:** mevcut Work/Mac Engineer ve mevcut DoneCheck/Human Threshold.

**İlk somut veri adayı:** PiLive Work PR #241, \`P02.S01.01\`. Kayıtlı Mac Engineer \`BUILD\` aksiyonu **yalnız kendi disposable build proof kapsamında** doğrulanmıştır; PiLive yayın/kurulum yetkisini genişletmez. Gerçek uygulama kanıtı için mevcut Work'ün Mac'te owner izinli binary/UI kullanıcı kabulü gerekir. Diğer görevler Mac recovery ve web build/test/repair; bunlar ayrı owner kapsamları olmadan çalıştırılmaz.

**Tek komutlu kaynak kontrolü:** \`python3 -B governance/enguru-suzgeci/zulfikar-v12/zulfikar_v131_single_acceptance.py --mode status\` (salt-okunur, Python standart kütüphane + mevcut projedeki kod). \`--mode plan\` kaynak-pimli üç görev devrini JSON olarak sunar. İki komut da Mac yürütmesi, yeni issuer, yeni writer, GitHub push, ürün PASS veya yetki kararı oluşturmaz.

**Gerçek bitti koşulu:** Bunların her biri mevcut canonical gerçek kaynak ve yetkiyle bağımsız doğrulanır. Görev makbuzundaki SHA ve PASS metni yalnız kaynak iddiasıdır; gerçek çalışma/owner imzası değildir.

## Hedef 2 — yeteneklerin tümü 100/100

**Hedef 1'in gerçek resmî finişinden sonra** açılır. Hazırlık 3×100 veya GitHub 6/6 CI otomatik açma sebebi değildir. Yeteneklerin tamamı mevcut ilk hedefin aynı kaynağında ölçülecek; yeni bağımsız puan defteri, yeni owner, ikinci core ve ücretli servis kurulmayacak.

## Yöntem: 8 aşama + üç karşıt tur

1. Kaynağı gör: exact Git HEAD ve iki Mac Engineer kayıt defteri.
2. Kazanımları koru: 6 başlangıç ve 3×100 hazırlık ayrı.
3. İhtiyaçları/eksikleri tespit et: üç gerçek kapanış işi.
4. Gerekli farkı üret: kaynaklı action devir paketi.
5. Onar: Work/Mac Engineer gerçek yetkili icra.
6. Kanıtla: 3 tur karşıt test + saha makbuzu + bağımsız kabul.
7. Sonraki ihtiyacı gör: tek açık iş.
8. İlerlet: 6×100 sağlandıysa DoneCheck/Human Threshold; aksi halde HOLD.

**Güvenli durum:** CI testlerinin başarılı olması kanıtlı teknik alt kapı PASS'dir. Kullanıcının Mac'ine veya mevcut Work oturumuna bu PR'dan bağlantı/uzaktan yürütme yapılamamıştır. Bu yüzden **G1 gerçek bitiş HOLD, G2 kilitli**. Gerçek saha makbuzu geldiğinde aynı tek kaynak üzerinden değerlendirilir.

\`G1_HOLD → G1_REAL_EVIDENCE → SIX×100 + AUTHORIZED_VERIFIED_FINISH → G2_UNLOCK → G2_REAL_100/100\`.
