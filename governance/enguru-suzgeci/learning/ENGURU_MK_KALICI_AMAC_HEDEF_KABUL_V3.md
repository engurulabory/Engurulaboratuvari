# ENGÜRÜ Mühendislik Kası™ — Kalıcı Amaç, Hedef ve Kabul Sözleşmesi V3

**Kalıcı sabit amaç:** ChatGPT + OSi mühendisliğinde ortaya çıkan gerçek fark, hata, ihtiyaç, beklenmedik davranış ve başarıyı *kanıta bağlı, güvenli, tekrar kullanılabilir çalışma bilgisine* dönüştürmek. Her yeni çalışmada tekrar teşhisi, gereksiz manuel adımı ve erken bitiş beyanını ölçerek azaltmak.

**Kalıcı sabit hedef:** `GERÇEK_OLAY → KAYNAK_KANITI → KAPSAM/OWNER → TEKRAR_AYIKLAMA → HATA/İHTİYAÇ SINIFLAMA → KARŞIT TEST → GÖZDEN GEÇİRİLEN İYİLEŞTİRME → GÜNCEL KAYNAĞA HİZALANMA → ÖLÇÜMLÜ KAZANIM`.

**Ürün hedefi ayrı:** `ENGURU_MANAGEMENT_V69_PR_203 → G2 OWNER TRUST → G3 ED25519 HUMAN REVIEW → G4 DONECHECK AUDIT → G5 AUTHORIZED MERGE/EXACT MAIN → G6 VERIFIED_FINISH → BITTI_DUR`.

## Yetki ve çalışma sözleşmesi

1. Kaynakların değeri: GitHub gerçek commit/CI/olay id, Mac OSi SHA-256 ve gerçek yetkili kabul; tahmin `HYPOTHESIS`, kaynak kanıtı `OBSERVED`, kabul yalnız canonical kriptografik mekanizmayla `PASS`.
2. Öğrenme adaptörü **mevcut ENGÜRÜ Süzgeci™ sekiz aşaması içinde** yardımcı katmandır; yeni issuer, owner, core veya bağımsız resmî otorite değildir.
3. GitHub izleyicisi bir Python worker'dır; `*/5 * * * *` **beş dakikalık deneme hedefi**, garantili SLA değil. Gerçek `event=schedule` run'ları ve timestamp aralıkları bağımsız ölçülür. ChatGPT zamanlanmış nöbeti **saatliktir**; ChatGPT her yeni iş turunda **en güncel yaşayan dosyayı yeniden okur**.
4. Açık `Engurulaboratuvari` izleme dalına **özel `enguru-mac-engineer` PR #14 yorumları, commit SHA/CI detayları ve yerel Mac özel içerikleri otomatik taşınmaz**. İzinli geçiş yalnız owner'ın gizlisiz, incelemeye uygun kaydı PR #203/#206'ya özellikle aktarmasıyla mümkündür.
5. OSi'nin gönderilen blok ve dönen yanıtı, onaylı GitHub owner yorumunda `TASK_ID=ENGURU_MANAGEMENT_V69_PR_203` ve `BLOCK_ID=OSIBLOCK-...` alanlarıyla bağlanır. Eşleşme = izlenebilirlik kanıtı; yetkili imza değildir. Eşleşmeyen yanıt `PAIR_MISSING_REVIEW_REQUIRED`.
6. Bir olay `NEW_REVIEW_CANDIDATE` veya `HOLD` olarak sınıflanır; yetkili kabulü, özel anahtar/macos parolasını, ledger'ı, ürün PR merge'ini ve terminal kabul durumunu değiştirmez. Kaynak SHA işaretçisi, gerçek bayt doğrulamasının yerine geçmez.
7. Tek yaşayan dosya `governance/enguru-suzgeci/ENGURU_OSI_MUHENDISLIK_KASI_CANLI_KAYIT_V1.md`; teknik cursor `learning/MK_WATCH_CHECKPOINT.json`; bot değişiklikleri yalnız korunan `docs/enguru-osi-muhendislik-kasi-20261023` inceleme dalında. `main` yalnız yetkili yayın/CI ile güncellenir.
8. GitHub'daki olay kendini yazabilir; **ChatGPT model ağırlıklarını yeniden eğitmez**. Güncel belge her çalışma turunda gerçek okunarak hizalanır. Ürün koduna kural alma gerçek CI/test ve owner review gerektirir.

## 100/100 amaç/kapsam kabulü

**Tasarım/izole kabul:** 25 farklı amaca bağlı kapı × 4 puan = 100. Her kapı gerçek çalışan test adıyla eşlenir; en az 95 bireysel test senaryosu çalıştırılır (önceki 79 temel senaryoya göre **%20 ek sınama payı**). Art arda iki ayrı temiz subprocess turu gerekir. Hata çıkarsa düzeltme ve tur tekrarları, aynı özgün senaryolar korunarak yapılır. `tools/enguru_mk_acceptance_v3.py` makine-okunur `MK_V3_ACCEPTANCE_RECEIPT.json` üretir. Dinamik sayı, sonuç ve kaynak SHA içerir. Simülasyon PASS, gerçek GitHub schedule / Mac owner kabul PASS'i değildir.

**Gerçek çalışma kabulü:** Workflow ve testler GitHub exact-HEAD `completed/success`; gerçek owner event ve yaşayan dosya yazımı ayrıca doğrulanır. GitHub `schedule` için aynı workflow'un exact-main üzerinde birbirini izleyen **4 gerçek tamamlanmış `schedule` run** sonucu ve 3 gerçek aralık doğrulanır. GitHub yoğunluğunda cron gecikme/atlama gözlenirse `SCHEDULE_HOLD`; hizmet düzeyi yanlış iddia edilmez. Özel depodan otomatik veri taşınmaması ve sırların korunması karşıt testlerle sürdürülür.

**Performans ölçüleri:** 
- `P01` owner'ın bir onaylı icra için ayrı manuel hareketleri (aynı kapsamda önce/sonra),
- `P02` aynı doğrulanmış kök neden teşhis tekrar oranı,
- `P03` resmî kanıt öncesi hatalı bitiş oranı (hedef 0),
- `P04` ilk hata raporundan doğrulanmış onarıma geçen medyan süre,
- `P05` gerçek GitHub schedule güvenilirliği (gerçek event ve run ID),
- `P06` gerçek owner key/grant, imza, ledger ve exact-main kapı tamamlanması.

**Sınır:** Veri oluşmadan önce performans iyileşmesini yüzdeyle iddia etme. `THEORETICAL_DESIGN=100/100` yalnız ölçülen test kapsama tanımıyla mümkündür; `FIELD_PASS` gerçek saha kanıtına dayanır. Kanıtlı bitiş `VERIFIED_FINISH → BITTI_DUR` ürünün yetkili DoneCheck+Human Threshold kapısıdır.

## OSi blok/yanıt örneği

```text
<!-- ENGURU_OSI_BLOCK_V1 -->
TASK_ID=ENGURU_MANAGEMENT_V69_PR_203
BLOCK_ID=OSIBLOCK-20261023-A
Gizli bilgi içermeyen, izinli ve kaynaklı saha kontrolü
```

```text
<!-- ENGURU_OSI_RESPONSE_V1 -->
TASK_ID=ENGURU_MANAGEMENT_V69_PR_203
BLOCK_ID=OSIBLOCK-20261023-A
Gerçek SHA-256 ve kanıta bağlanmış saha yanıtı
```

**Konum:** Yalnız yetkili owner tarafından GitHub PR #203 / #206 yorumunda açıkça yayınlandığında GitHub izleme girdisi olur. Aynı işaretçiler özel PR #14 üzerinde tek başına kamusal yayın izni oluşturmaz. Owner private key, parola veya token bu kayıtlara eklenmez.